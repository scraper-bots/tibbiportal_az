#!/usr/bin/env python3
"""
Async scraper for tibbiportal.az doctors data
Uses asyncio and aiohttp for concurrent scraping
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import re
from typing import List, Dict, Optional
from datetime import datetime


class TibbiPortalScraper:
    def __init__(self, max_concurrent: int = 10):
        self.base_url = "https://tibbiportal.az"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.doctors_data = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def get_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a page with retry logic"""
        async with self.semaphore:
            for attempt in range(max_retries):
                try:
                    async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        response.raise_for_status()
                        html = await response.text()
                        return BeautifulSoup(html, 'html.parser')
                except Exception as e:
                    print(f"Error fetching {url} (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    else:
                        return None
        return None

    async def extract_doctor_links_from_listing(self, page_number: int) -> List[Dict[str, str]]:
        """Extract doctor information from a listing page"""
        url = f"{self.base_url}/search?page_objects=2&page_doctors={page_number}"
        print(f"Scraping listing page {page_number}...")

        soup = await self.get_page(url)
        if not soup:
            return []

        doctors = []
        doctor_items = soup.select('section#doctors .item')

        for item in doctor_items:
            try:
                link_elem = item.find('a', href=True)
                name_elem = item.find('h3')
                specialty_elem = item.find('p')

                if link_elem and name_elem:
                    doctor = {
                        'url': link_elem['href'] if link_elem['href'].startswith('http') else self.base_url + link_elem['href'],
                        'name': name_elem.text.strip(),
                        'specialty_preview': specialty_elem.text.strip() if specialty_elem else ''
                    }
                    doctors.append(doctor)
            except Exception as e:
                print(f"Error parsing doctor item: {e}")
                continue

        return doctors

    async def extract_doctor_details(self, doctor_url: str, doctor_name: str) -> Dict[str, str]:
        """Extract detailed information from a doctor's detail page"""
        soup = await self.get_page(doctor_url)
        if not soup:
            return {'url': doctor_url}

        details = {'url': doctor_url}

        try:
            # Extract name from widget title
            title_elem = soup.select_one('section.item-detail .widget-title')
            if title_elem:
                # Remove the heart icon and count from the title
                title_text = title_elem.get_text(strip=True)
                # Extract just the name (before any numbers)
                name_match = re.match(r'^([^\d]+)', title_text)
                if name_match:
                    details['name'] = name_match.group(1).strip()

            # Extract like count
            like_count_elem = soup.select_one('.rateItemCount')
            if like_count_elem:
                details['likes'] = like_count_elem.text.strip()

            # Extract information from the list items
            list_items = soup.select('section.item-detail ul li')

            for li in list_items:
                icon = li.find('i')
                span = li.find('span')

                if not icon or not span:
                    continue

                icon_class = ' '.join(icon.get('class', []))
                text = span.text.strip()

                # Parse based on icon type
                if 'fa-user-md' in icon_class:
                    details['specialty'] = text
                elif 'fa-calendar' in icon_class:
                    details['experience'] = text
                elif 'fa-phone' in icon_class or 'fa-mobile' in icon_class:
                    details['phone'] = text
                elif 'fa-clock-o' in icon_class:
                    details['work_hours'] = text
                elif 'fa-map-marker' in icon_class:
                    # Extract workplace
                    workplace_link = li.find('a')
                    if workplace_link:
                        details['workplace'] = workplace_link.text.strip()
                        details['workplace_url'] = workplace_link.get('href', '')
                    else:
                        details['workplace'] = text

        except Exception as e:
            print(f"Error extracting details from {doctor_url}: {e}")

        return details

    async def scrape_page(self, page_number: int, total_pages: int):
        """Scrape a single listing page and all its doctors"""
        print(f"\n=== Processing listing page {page_number}/{total_pages} ===")

        # Get doctors from listing page
        doctors = await self.extract_doctor_links_from_listing(page_number)
        print(f"Found {len(doctors)} doctors on page {page_number}")

        if not doctors:
            return

        # Fetch details for all doctors on this page concurrently
        print(f"Fetching details for {len(doctors)} doctors...")
        tasks = [
            self.extract_doctor_details(doctor['url'], doctor['name'])
            for doctor in doctors
        ]
        details_list = await asyncio.gather(*tasks)

        # Merge listing info with details
        for doctor, details in zip(doctors, details_list):
            doctor.update(details)
            self.doctors_data.append(doctor)

        print(f"✓ Page {page_number} completed: {len(doctors)} doctors scraped")

    async def scrape_all_doctors(self, start_page: int = 1, end_page: int = 214, batch_size: int = 5):
        """
        Scrape all doctors from listing pages and their detail pages

        Args:
            start_page: First page to scrape
            end_page: Last page to scrape
            batch_size: Number of listing pages to process concurrently
        """
        print(f"Starting async scraper...")
        print(f"Pages: {start_page} to {end_page}")
        print(f"Batch size: {batch_size} pages at a time")
        print(f"This will scrape much faster than the synchronous version!\n")

        start_time = datetime.now()

        # Process pages in batches
        for batch_start in range(start_page, end_page + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_page)
            batch_pages = range(batch_start, batch_end + 1)

            print(f"\n{'='*60}")
            print(f"Processing batch: pages {batch_start}-{batch_end}")
            print(f"{'='*60}")

            # Scrape multiple pages concurrently
            tasks = [self.scrape_page(page_num, end_page) for page_num in batch_pages]
            await asyncio.gather(*tasks)

            # Display progress
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = len(self.doctors_data) / elapsed if elapsed > 0 else 0
            print(f"\n✓ Progress: {len(self.doctors_data)} doctors scraped")
            print(f"  Time elapsed: {elapsed:.1f}s | Rate: {rate:.1f} doctors/sec")

            # Small delay between batches
            await asyncio.sleep(1)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"✓ Scraping completed!")
        print(f"  Total doctors: {len(self.doctors_data)}")
        print(f"  Total time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"  Average rate: {len(self.doctors_data)/elapsed:.1f} doctors/sec")
        print(f"{'='*60}")

    def save_to_csv(self, filename: str = 'doctors_data.csv'):
        """Save scraped data to CSV file"""
        if not self.doctors_data:
            print("No data to save!")
            return

        # Define all possible fields
        fieldnames = [
            'name',
            'specialty',
            'specialty_preview',
            'experience',
            'phone',
            'work_hours',
            'workplace',
            'workplace_url',
            'likes',
            'url'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()

                for doctor in self.doctors_data:
                    writer.writerow(doctor)

            print(f"✓ Data saved to {filename} ({len(self.doctors_data)} records)")
        except Exception as e:
            print(f"Error saving to CSV: {e}")


async def main():
    # Configuration
    start_page = 1
    end_page = 214
    batch_size = 5  # Process 5 listing pages at a time
    max_concurrent = 10  # Max concurrent connections per batch

    print("Tibbiportal.az Async Doctor Scraper")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Pages to scrape: {start_page} to {end_page}")
    print(f"  Batch size: {batch_size} pages")
    print(f"  Max concurrent connections: {max_concurrent}")
    print(f"  Expected total doctors: ~2136")
    print("=" * 60)
    print()

    try:
        async with TibbiPortalScraper(max_concurrent=max_concurrent) as scraper:
            await scraper.scrape_all_doctors(
                start_page=start_page,
                end_page=end_page,
                batch_size=batch_size
            )
            scraper.save_to_csv('doctors_data_complete.csv')
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user!")
        print("Saving progress...")
        if scraper:
            scraper.save_to_csv('doctors_data_interrupted.csv')
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Saving progress...")
        if scraper:
            scraper.save_to_csv('doctors_data_error.csv')
        raise


if __name__ == "__main__":
    asyncio.run(main())

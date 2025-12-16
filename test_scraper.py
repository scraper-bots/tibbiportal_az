#!/usr/bin/env python3
"""
Test script for tibbiportal.az scraper
Scrapes only the first page to verify functionality
"""

from scrape_doctors import TibbiPortalScraper


def main():
    scraper = TibbiPortalScraper()

    print("Testing scraper with first page only...")
    print("=" * 50)

    try:
        # Test with just the first page
        scraper.scrape_all_doctors(start_page=1, end_page=1)

        # Save test results
        scraper.save_to_csv('doctors_data_test.csv')

        print("\n" + "=" * 50)
        print(f"✓ Test completed successfully!")
        print(f"✓ Scraped {len(scraper.doctors_data)} doctors")
        print(f"✓ Data saved to doctors_data_test.csv")
        print("\nSample data (first doctor):")
        if scraper.doctors_data:
            for key, value in scraper.doctors_data[0].items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

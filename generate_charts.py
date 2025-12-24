"""
TibbiPortal.az Medical Data Analysis
Generates business-focused charts and insights from doctors/healthcare data
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from collections import Counter

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Create charts directory
os.makedirs('charts', exist_ok=True)

# Load data
print("Loading data...")
df = pd.read_csv('doctors_data_complete.csv')
print(f"Total records: {len(df)}")

# Clean data - remove duplicates based on URL
df_unique = df.drop_duplicates(subset=['url'])
print(f"Unique records: {len(df_unique)}")

# Separate doctors from organizations/centers
doctors_mask = df_unique['url'].str.contains('doctor-detailed', na=False)
df_doctors = df_unique[doctors_mask].copy()
df_centers = df_unique[~doctors_mask].copy()

print(f"Doctors: {len(df_doctors)}")
print(f"Medical Centers/Organizations: {len(df_centers)}")

# ============================================
# CHART 1: Top 15 Medical Specialties by Count
# ============================================
print("\nGenerating Chart 1: Top Specialties by Count...")

# Clean specialty field - take first specialty for multi-specialty doctors
df_doctors['primary_specialty'] = df_doctors['specialty'].apply(
    lambda x: str(x).split(',')[0].strip() if pd.notna(x) else 'Unknown'
)

specialty_counts = df_doctors['primary_specialty'].value_counts().head(15)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(specialty_counts)))[::-1]
bars = ax.barh(range(len(specialty_counts)), specialty_counts.values, color=colors)
ax.set_yticks(range(len(specialty_counts)))
ax.set_yticklabels(specialty_counts.index)
ax.invert_yaxis()
ax.set_xlabel('Number of Doctors')
ax.set_title('Top 15 Medical Specialties by Number of Doctors\n(Market Supply Analysis)', fontweight='bold')

# Add value labels
for bar, val in zip(bars, specialty_counts.values):
    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, str(val),
            va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_top_specialties_by_count.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 2: Total Likes by Specialty (Patient Engagement)
# ============================================
print("Generating Chart 2: Specialties by Patient Engagement...")

df_doctors['likes'] = pd.to_numeric(df_doctors['likes'], errors='coerce').fillna(0)
specialty_likes = df_doctors.groupby('primary_specialty')['likes'].sum().sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(specialty_likes)))[::-1]
bars = ax.barh(range(len(specialty_likes)), specialty_likes.values, color=colors)
ax.set_yticks(range(len(specialty_likes)))
ax.set_yticklabels(specialty_likes.index)
ax.invert_yaxis()
ax.set_xlabel('Total Likes (Patient Engagement)')
ax.set_title('Top 15 Specialties by Patient Engagement\n(Total Likes - Demand Indicator)', fontweight='bold')

for bar, val in zip(bars, specialty_likes.values):
    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{int(val)}',
            va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_specialties_by_engagement.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 3: Supply vs Demand Analysis
# ============================================
print("Generating Chart 3: Supply vs Demand Analysis...")

# Calculate average likes per doctor for each specialty (demand/supply ratio)
specialty_stats = df_doctors.groupby('primary_specialty').agg({
    'likes': ['sum', 'mean', 'count']
}).round(2)
specialty_stats.columns = ['total_likes', 'avg_likes', 'doctor_count']
specialty_stats = specialty_stats[specialty_stats['doctor_count'] >= 5]  # Min 5 doctors
specialty_stats = specialty_stats.sort_values('avg_likes', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(specialty_stats)))[::-1]
bars = ax.barh(range(len(specialty_stats)), specialty_stats['avg_likes'].values, color=colors)
ax.set_yticks(range(len(specialty_stats)))
ax.set_yticklabels(specialty_stats.index)
ax.invert_yaxis()
ax.set_xlabel('Average Likes per Doctor')
ax.set_title('Top 15 Specialties by Average Engagement per Doctor\n(High Demand / Low Supply Indicator)', fontweight='bold')

for bar, val, count in zip(bars, specialty_stats['avg_likes'].values, specialty_stats['doctor_count'].values):
    ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.1f} ({int(count)} docs)',
            va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('charts/03_supply_demand_ratio.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 4: Top 20 Most Popular Doctors
# ============================================
print("Generating Chart 4: Top Doctors by Popularity...")

top_doctors = df_doctors.nlargest(20, 'likes')[['name', 'primary_specialty', 'likes']]

fig, ax = plt.subplots(figsize=(14, 10))
colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_doctors)))[::-1]
bars = ax.barh(range(len(top_doctors)), top_doctors['likes'].values, color=colors)
ax.set_yticks(range(len(top_doctors)))
labels = [f"{row['name'][:25]}... ({row['primary_specialty'][:15]})" if len(row['name']) > 25
          else f"{row['name']} ({row['primary_specialty'][:15]})"
          for _, row in top_doctors.iterrows()]
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlabel('Number of Likes')
ax.set_title('Top 20 Most Popular Doctors\n(Key Opinion Leaders / Influencers)', fontweight='bold')

for bar, val in zip(bars, top_doctors['likes'].values):
    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, str(int(val)),
            va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_top_doctors_popularity.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 5: District/Location Distribution
# ============================================
print("Generating Chart 5: Geographic Distribution...")

def extract_district(workplace):
    if pd.isna(workplace):
        return 'Unknown'
    workplace = str(workplace)
    # Extract district names from address
    districts = ['Nərimanov', 'Binəqədi', 'Səbail', 'Nəsimi', 'Xətai', 'Yasamal',
                 'Nizami', 'Sabunçu', 'Suraxanı', 'Xəzər', 'Qaradağ', 'Pirallahı',
                 'Abşeron', 'Masazır']
    for district in districts:
        if district.lower() in workplace.lower():
            return district + ' r-nu'
    if 'Bakı' in workplace or 'Baku' in workplace:
        return 'Bakı (Digər)'
    return 'Unknown'

# Combine doctors and centers for geographic analysis
df_all = df_unique.copy()
df_all['district'] = df_all['workplace'].apply(extract_district)
district_counts = df_all[df_all['district'] != 'Unknown']['district'].value_counts()

if len(district_counts) > 0:
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = plt.cm.Purples(np.linspace(0.4, 0.9, len(district_counts)))[::-1]
    bars = ax.barh(range(len(district_counts)), district_counts.values, color=colors)
    ax.set_yticks(range(len(district_counts)))
    ax.set_yticklabels(district_counts.index)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Healthcare Providers')
    ax.set_title('Healthcare Provider Distribution by District\n(Geographic Market Analysis)', fontweight='bold')

    for bar, val in zip(bars, district_counts.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, str(val),
                va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig('charts/05_geographic_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()

# ============================================
# CHART 6: Medical Center Types
# ============================================
print("Generating Chart 6: Medical Center Categories...")

center_types = df_centers['specialty'].value_counts().head(10)

if len(center_types) > 0:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Set2(np.linspace(0, 1, len(center_types)))
    wedges, texts, autotexts = ax.pie(center_types.values, labels=center_types.index,
                                       autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('Medical Center Distribution by Type\n(Business Category Analysis)', fontweight='bold')
    plt.tight_layout()
    plt.savefig('charts/06_medical_center_types.png', dpi=150, bbox_inches='tight')
    plt.close()

# ============================================
# CHART 7: Engagement Distribution (Likes Histogram)
# ============================================
print("Generating Chart 7: Engagement Distribution...")

fig, ax = plt.subplots(figsize=(12, 6))
likes_data = df_doctors[df_doctors['likes'] > 0]['likes']
ax.hist(likes_data, bins=30, color='steelblue', edgecolor='white', alpha=0.7)
ax.axvline(likes_data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {likes_data.mean():.1f}')
ax.axvline(likes_data.median(), color='orange', linestyle='--', linewidth=2, label=f'Median: {likes_data.median():.1f}')
ax.set_xlabel('Number of Likes')
ax.set_ylabel('Number of Doctors')
ax.set_title('Distribution of Doctor Engagement (Likes)\n(Understanding Engagement Patterns)', fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('charts/07_engagement_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 8: Specialty Market Share
# ============================================
print("Generating Chart 8: Specialty Market Share...")

top_10_specialties = df_doctors['primary_specialty'].value_counts().head(10)
other_count = len(df_doctors) - top_10_specialties.sum()

fig, ax = plt.subplots(figsize=(12, 8))
labels = list(top_10_specialties.index) + ['Other Specialties']
sizes = list(top_10_specialties.values) + [other_count]
colors = plt.cm.tab20(np.linspace(0, 1, len(labels)))
explode = [0.02] * len(labels)

wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                   colors=colors, explode=explode, startangle=90)
ax.set_title('Medical Specialty Market Share\n(Portfolio Analysis)', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/08_specialty_market_share.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 9: Doctors with/without Work Hours (Availability)
# ============================================
print("Generating Chart 9: Availability Analysis...")

df_doctors['has_work_hours'] = df_doctors['work_hours'].notna() & (df_doctors['work_hours'] != '')
availability_counts = df_doctors['has_work_hours'].value_counts()

fig, ax = plt.subplots(figsize=(10, 6))
labels = ['Work Hours Listed', 'No Work Hours']
sizes = [availability_counts.get(True, 0), availability_counts.get(False, 0)]
colors = ['#2ecc71', '#e74c3c']
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                   colors=colors, startangle=90, explode=[0.02, 0.02])
ax.set_title('Doctor Availability Information\n(Profile Completeness Analysis)', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/09_availability_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# CHART 10: Engagement by Profile Completeness
# ============================================
print("Generating Chart 10: Profile Completeness Impact...")

df_doctors['has_workplace'] = df_doctors['workplace'].notna() & (df_doctors['workplace'] != '')
df_doctors['profile_score'] = df_doctors['has_work_hours'].astype(int) + df_doctors['has_workplace'].astype(int)

completeness_engagement = df_doctors.groupby('profile_score')['likes'].mean().reindex([0, 1, 2], fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))
labels = ['No Info (0)', 'Partial (1)', 'Complete (2)']
x_pos = range(len(labels))
colors_profile = ['#e74c3c', '#f39c12', '#2ecc71'][:len(completeness_engagement)]
bars = ax.bar(x_pos, completeness_engagement.values, color=colors_profile)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels)
ax.set_ylabel('Average Likes')
ax.set_xlabel('Profile Completeness Level')
ax.set_title('Impact of Profile Completeness on Patient Engagement\n(Data Quality ROI)', fontweight='bold')

for bar, val in zip(bars, completeness_engagement.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 0.1, f'{val:.2f}',
            ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_profile_completeness_impact.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================
# Generate Summary Statistics
# ============================================
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)

stats = {
    'Total Records': len(df_unique),
    'Total Doctors': len(df_doctors),
    'Total Medical Centers': len(df_centers),
    'Unique Specialties': df_doctors['primary_specialty'].nunique(),
    'Total Likes': int(df_doctors['likes'].sum()),
    'Average Likes per Doctor': round(df_doctors['likes'].mean(), 2),
    'Max Likes (Single Doctor)': int(df_doctors['likes'].max()),
    'Doctors with 0 Likes': len(df_doctors[df_doctors['likes'] == 0]),
    'Doctors with Work Hours': int(df_doctors['has_work_hours'].sum()),
    'Doctors with Workplace Info': int(df_doctors['has_workplace'].sum()),
}

for key, value in stats.items():
    print(f"{key}: {value}")

# Save statistics to file
with open('charts/statistics.txt', 'w', encoding='utf-8') as f:
    f.write("TibbiPortal.az Data Analysis Summary\n")
    f.write("="*50 + "\n\n")
    for key, value in stats.items():
        f.write(f"{key}: {value}\n")

print("\n" + "="*60)
print("Charts generated successfully in 'charts/' folder!")
print("="*60)

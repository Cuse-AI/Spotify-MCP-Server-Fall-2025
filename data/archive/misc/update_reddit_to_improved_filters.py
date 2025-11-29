"""
Update all Reddit scrapers to use IMPROVED quality filters (relaxed thresholds)
"""

from pathlib import Path

def update_reddit_scraper(file_path):
    """Update a single Reddit scraper to use improved filters"""
    print(f"Updating: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Replace old import with new one
    if 'from quality_filters import QualityFilter' in content:
        content = content.replace(
            'from quality_filters import QualityFilter',
            'from improved_quality_filters import ImprovedQualityFilter'
        )

        # Replace class instantiation
        content = content.replace(
            'self.quality_filter = QualityFilter()',
            'self.quality_filter = ImprovedQualityFilter()'
        )

        # Copy improved_quality_filters.py to reddit directory if not there
        improved_filter_src = Path(__file__).parent / 'improved_quality_filters.py'
        improved_filter_dst = Path(__file__).parent / 'reddit' / 'smart_scrapers' / 'improved_quality_filters.py'

        if improved_filter_src.exists() and not improved_filter_dst.exists():
            import shutil
            shutil.copy(improved_filter_src, improved_filter_dst)
            print(f"  [COPY] Copied improved_quality_filters.py to reddit/smart_scrapers/")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Updated to use ImprovedQualityFilter")
            return True
        else:
            print(f"  [SKIP] Already using improved filters")
            return False
    else:
        print(f"  [SKIP] No quality filter found")
        return False


def main():
    # First, copy improved filters to reddit directory
    improved_filter_src = Path(__file__).parent.parent / 'improved_quality_filters.py'
    improved_filter_dst = Path(__file__).parent / 'smart_scrapers' / 'improved_quality_filters.py'

    if improved_filter_src.exists():
        import shutil
        shutil.copy(improved_filter_src, improved_filter_dst)
        print("[OK] Copied improved_quality_filters.py to reddit/smart_scrapers/\n")

    scrapers_dir = Path(__file__).parent / 'smart_scrapers'
    scraper_files = sorted(scrapers_dir.glob('scrape_*.py'))

    print("="*70)
    print("UPDATING REDDIT SCRAPERS TO IMPROVED FILTERS")
    print("="*70)
    print(f"Found {len(scraper_files)} scrapers\n")

    updated = 0
    for scraper in scraper_files:
        if update_reddit_scraper(scraper):
            updated += 1

    print(f"\n{'='*70}")
    print(f"COMPLETE: Updated {updated}/{len(scraper_files)} scrapers")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

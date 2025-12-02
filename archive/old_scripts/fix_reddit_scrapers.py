# -*- coding: utf-8 -*-
"""
Fix Reddit Scrapers - Add quality filtering
Nov 30, 2025

This script fixes all Reddit scrapers to:
1. Import and use UnifiedQualityFilter
2. Filter comments BEFORE extracting songs
3. Reject multi-song lists and low-quality comments
"""

import os
import re
from pathlib import Path

REDDIT_DIR = Path(__file__).parent.parent / 'scrapers' / 'reddit'

def fix_scraper_file(filepath):
    """Fix a single Reddit scraper file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Add import for unified filter after checkpoint_utils import
    if 'from unified_quality_filter import' not in content:
        import_pattern = r'(from checkpoint_utils import CheckpointManager\n)'
        if re.search(import_pattern, content):
            content = re.sub(
                import_pattern,
                r'\1from unified_quality_filter import UnifiedQualityFilter\n',
                content
            )
    
    # 2. Add filter initialization in __init__
    if 'self.quality_filter = UnifiedQualityFilter()' not in content:
        # Find self.scraped_urls = set() and add after it
        init_pattern = r'(self\.scraped_urls = set\(\)\n)'
        if re.search(init_pattern, content):
            content = re.sub(
                init_pattern,
                r'\1        self.quality_filter = UnifiedQualityFilter()\n',
                content
            )
    
    # 3. Add quality check before extract_from_comment call
    # Find the pattern where songs are extracted and add filter check
    old_extract_pattern = r'''(                                songs = self\.extract_from_comment\(
                                    comment\.body, url, comment\.score,
                                    post_title, post_body
                                \))'''
    
    new_extract_pattern = '''                                # Quality filter check FIRST
                                passed, reason = self.quality_filter.check(comment.body, source='reddit')
                                if not passed:
                                    continue
                                
                                songs = self.extract_from_comment(
                                    comment.body, url, comment.score,
                                    post_title, post_body
                                )'''
    
    content = re.sub(old_extract_pattern, new_extract_pattern, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("="*60)
    print("FIXING REDDIT SCRAPERS")
    print("="*60)
    
    fixed = 0
    skipped = 0
    
    for filepath in REDDIT_DIR.glob('scrape_*.py'):
        print(f"\nProcessing: {filepath.name}")
        if fix_scraper_file(filepath):
            print(f"  [FIXED] {filepath.name}")
            fixed += 1
        else:
            print(f"  [SKIPPED] {filepath.name} - already fixed or pattern not found")
            skipped += 1
    
    print("\n" + "="*60)
    print(f"DONE! Fixed: {fixed}, Skipped: {skipped}")
    print("="*60)

if __name__ == '__main__':
    main()

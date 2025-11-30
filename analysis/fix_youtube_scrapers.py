# -*- coding: utf-8 -*-
"""
Fix YouTube Scrapers - Remove playlist description fallback
Nov 30, 2025

This script fixes all YouTube scrapers to:
1. Import and use UnifiedQualityFilter
2. Never use playlist descriptions as comments
3. Skip songs without quality comments
"""

import os
import re
from pathlib import Path

YOUTUBE_DIR = Path(__file__).parent.parent / 'scrapers' / 'youtube'

def fix_scraper_file(filepath):
    """Fix a single YouTube scraper file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Add import for unified filter after other imports
    if 'from unified_quality_filter import' not in content:
        # Find the last import line
        import_section = re.search(r'(from checkpoint_utils.*?\n)', content)
        if import_section:
            insert_pos = import_section.end()
            new_import = "from unified_quality_filter import UnifiedQualityFilter\n"
            content = content[:insert_pos] + new_import + content[insert_pos:]
    
    # 2. Add filter initialization in __init__ if not present
    if 'self.quality_filter = UnifiedQualityFilter()' not in content:
        # Find self.scraped_videos = set() and add after it
        init_pattern = r'(self\.scraped_videos = set\(\)\n)'
        if re.search(init_pattern, content):
            content = re.sub(
                init_pattern,
                r'\1        self.quality_filter = UnifiedQualityFilter()\n',
                content
            )
    
    # 3. Fix the comment selection logic - this is the critical fix
    # Replace the fallback to playlist description
    old_pattern = r"'comment_text': best_comment if best_comment else playlist\['description'\]\[:500\],"
    new_pattern = "'comment_text': best_comment,  # NEVER use playlist description as fallback"
    content = re.sub(old_pattern, new_pattern, content)
    
    # 4. Add quality filter check and skip if no good comment
    # Find the comment selection block and enhance it
    old_comment_block = '''                        # Find best emotional comment
                        best_comment = ""
                        best_likes = 0
                        for comment in comments:
                            if comment['likes'] > best_likes and len(comment['text']) > 20:
                                best_comment = comment['text']
                                best_likes = comment['likes']'''
    
    new_comment_block = '''                        # Find best emotional comment using quality filter
                        best_comment = ""
                        best_likes = 0
                        for comment in comments:
                            text = comment['text']
                            # Use unified quality filter
                            passed, reason = self.quality_filter.check(text, source='youtube')
                            if passed and comment['likes'] >= best_likes:
                                best_comment = text
                                best_likes = comment['likes']
                        
                        # SKIP if no quality comment found (never use playlist description!)
                        if not best_comment:
                            continue'''
    
    content = content.replace(old_comment_block, new_comment_block)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("="*60)
    print("FIXING YOUTUBE SCRAPERS")
    print("="*60)
    
    fixed = 0
    skipped = 0
    
    for filepath in YOUTUBE_DIR.glob('scrape_*.py'):
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

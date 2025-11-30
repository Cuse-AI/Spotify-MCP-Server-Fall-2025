# -*- coding: utf-8 -*-
"""
UNIFIED QUALITY FILTER v3.0
============================
Comprehensive quality filter for BOTH Reddit and YouTube scrapers.

KEY IMPROVEMENTS (Nov 30, 2025):
1. NEVER accept playlist descriptions as comments
2. Detect and reject multi-song list comments  
3. YouTube-specific spam (timestamps, "who's here 2024")
4. Reddit-specific spam (generic praise)
5. Require genuine emotional depth

This filter ensures PURE DATA enters our pipeline.
"""

import re
from typing import Tuple, Optional, Dict


class UnifiedQualityFilter:
    """
    Universal quality filter for Reddit AND YouTube scraping.
    
    Usage:
        filter = UnifiedQualityFilter()
        passed, reason = filter.check(comment_text, source='youtube')
    """
    
    # Length constraints
    MIN_LENGTH = 40
    MAX_LENGTH = 500
    MIN_WORDS = 10
    
    def __init__(self):
        self.stats = {
            'examined': 0,
            'passed': 0,
            'rejected_empty': 0,
            'rejected_too_short': 0,
            'rejected_too_long': 0,
            'rejected_few_words': 0,
            'rejected_url': 0,
            'rejected_playlist_desc': 0,
            'rejected_multi_song_list': 0,
            'rejected_youtube_spam': 0,
            'rejected_generic': 0,
            'rejected_no_emotion': 0,
            'rejected_shallow': 0,
        }
        
        # === URL PATTERNS ===
        self.url_patterns = [
            'http://', 'https://', 'www.', 
            'spotify.com', 'youtube.com', 'youtu.be',
            'soundcloud.com', 'bandcamp.com', 'apple.music',
            '.com/watch', '.com/track', '.com/playlist',
            'bit.ly', 'tinyurl'
        ]
        
        # === PLAYLIST DESCRIPTION PATTERNS ===
        # These indicate the text is a playlist/video description, NOT a comment
        self.playlist_desc_patterns = [
            r'playlist',
            r'subscribe',
            r'channel',
            r'follow us',
            r'follow me',
            r'like and share',
            r'turn on notifications',
            r'new music every',
            r'best.*hits.*20\d\d',
            r'top.*songs.*20\d\d',
            r'music.*compilation',
            r'mix.*20\d\d',
            r'official.*playlist',
            r'curated',
            r'featuring:',
            r'tracklist:',
            r'songs? included:',
            r'all rights? reserved',
            r'copyright',
            r'℗',
            r'©',
            r'distributed by',
            r'released under',
            r'check out our',
            r'stream now',
            r'available on',
            r'new uploads?',
            r'weekly update',
            r'monthly update',
        ]
        
        # === MULTI-SONG LIST PATTERNS ===
        # Comments that list multiple songs should be rejected
        self.multi_song_indicators = [
            # Numbered lists
            r'^\s*\d+[\.\)]\s*[A-Z]',
            # Bullet points
            r'^\s*[\-\*•]\s*[A-Z]',
            # Multiple "Artist - Song" patterns
            r'([A-Z][a-z]+.*?[-–—].*?){3,}',
            # OST/soundtrack listings
            r'(OST|soundtrack|tracklist)',
            # "and also" chains
            r'(and also|also try|check out also)',
        ]
        
        # === YOUTUBE-SPECIFIC SPAM ===
        self.youtube_spam_patterns = [
            r'^\d+:\d+',                      # Timestamps "2:34"
            r'who.*here.*202\d',              # "who's here in 2024"
            r'who.*listening.*202\d',         # "who's listening in 2024"
            r'anyone.*202\d',                 # "anyone else 2024"
            r'still.*here.*202\d',            # "still here in 2024"
            r'still.*listening.*202\d',       # "still listening in 2024"
            r'came here from',                # Referral spam
            r'algorithm brought',
            r'algorithm blessed',
            r'recommended.*brought',
            r'^first!*$',
            r'like if you',
            r'thumbs up if',
            r'notification squad',
            r'early squad',
            r'before.*million',
            r'here before.*viral',
            r'^i was here',
            r'^goosebumps\.?!?$',
            r'^chills\.?!?$',
            r'^wow\.?!?$',
            r'^damn\.?!?$',
            r'^rip\b',
            r'legend never dies?',
            r'rest in (peace|paradise)',
        ]
        
        # === GENERIC PRAISE (NO EMOTIONAL VALUE) ===
        self.generic_patterns = [
            r'^great song\.?!?$',
            r'^love this\.?!?$',
            r'^amazing\.?!?$',
            r'^this slaps\.?!?$',
            r'^banger\.?!?$',
            r'^fire\.?!?$',
            r'^masterpiece\.?!?$',
            r'^underrated\.?!?$',
            r'^classic\.?!?$',
            r'^beautiful\.?!?$',
            r'^perfect\.?!?$',
            r'^legend\.?!?$',
            r'^same\.?!?$',
            r'^mood\.?!?$',
            r'^vibe\.?!?$',
            r'^iconic\.?!?$',
            r'^timeless\.?!?$',
            r'^best song ever',
            r'^one of the best',
            r'^this is it\.?!?$',
            r'^this generation will never',
        ]
        
        # === SHALLOW PATTERNS (mention emotion but no depth) ===
        self.shallow_patterns = [
            r'^[^.]{0,40}reminds me of [^.]{0,20}$',   # Just "X reminds me of Y"
            r'^[^.]{0,30}great for [^.]{0,20}$',       # Just "great for X"
            r'^check out\b',
            r'^try\b',
            r'^listen to\b',
            r'^my (go-?to|favorite)\b[^.]{0,30}$',     # "My go-to" with nothing else
        ]
        
        # === EMOTIONAL DEPTH INDICATORS ===
        # Comments MUST have one of these to pass
        self.emotional_phrases = [
            # WHY phrases - explain the emotional connection
            'because', 'makes me feel', 'made me feel', 
            'helps me', 'helped me',
            'whenever i listen', 'every time i hear', 'when i hear this',
            'every time it', 'whenever it',
            'takes me back', 'transports me', 'brings me back',
            'brings back', 'takes me to', 'puts me in',
            'going through', 'went through', 'been through',
            'gets me through', 'got me through',
            'perfectly captures', 'captures the feeling', 'captures that',
            'this song is', 'this track is',
            'i play this when', 'i listen to this when',
            'cry every time', 'tears every time', 'always makes me',
            'healing', 'therapeutic', 'cathartic',
            'relate to', 'resonates', 'speaks to me',
            'the lyrics', 'the melody', 'the way',
            'love this because', 'love this song because',
            'perfect for when', 'great for when',
            'reminds me of when', 'reminds me of the time',
            'came out when', 'was in college', 'was in high school',
            'great times', 'good times', 'those days', 'back then',
            'instantly', 'immediately',
            'hits different', 'hit different',
            'soundtrack to my', 'soundtrack of my',
            'saved my', 'changed my life',
            'feel', 'felt', 'feeling',
            'cry', 'cried', 'tears',
            'comfort', 'comforting',
            'discovered', 'found this',
            'perfect for', 'great for',
        ]
    
    def check(self, text: str, source: str = 'reddit') -> Tuple[bool, str]:
        """
        Check if comment passes quality standards.
        
        Args:
            text: The comment text to check
            source: 'reddit' or 'youtube' (enables source-specific filters)
            
        Returns:
            (passed, reason) - reason is 'ok' if passed, else rejection reason
        """
        self.stats['examined'] += 1
        
        # Empty check
        if not text or not text.strip():
            self.stats['rejected_empty'] += 1
            return False, 'empty'
        
        text = text.strip()
        text_lower = text.lower()
        
        # === LENGTH CHECKS ===
        if len(text) < self.MIN_LENGTH:
            self.stats['rejected_too_short'] += 1
            return False, 'too_short'
        
        if len(text) > self.MAX_LENGTH:
            self.stats['rejected_too_long'] += 1
            return False, 'too_long'
        
        # Word count check
        word_count = len(text.split())
        if word_count < self.MIN_WORDS:
            self.stats['rejected_few_words'] += 1
            return False, 'few_words'
        
        # === URL CHECK ===
        if any(url in text_lower for url in self.url_patterns):
            self.stats['rejected_url'] += 1
            return False, 'has_url'
        
        # === PLAYLIST DESCRIPTION CHECK (CRITICAL!) ===
        # This catches YouTube playlist descriptions used as comments
        playlist_matches = sum(
            1 for pattern in self.playlist_desc_patterns 
            if re.search(pattern, text_lower)
        )
        if playlist_matches >= 2:  # 2+ indicators = definitely a description
            self.stats['rejected_playlist_desc'] += 1
            return False, 'playlist_description'
        
        # === MULTI-SONG LIST CHECK (CRITICAL!) ===
        # Reject comments that list multiple songs
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Check for 3+ lines with song patterns
        if len(lines) >= 3:
            song_pattern_lines = sum(
                1 for l in lines 
                if re.search(r'[-–—]|by\s+[A-Z]|\d+[\.\)]', l)
            )
            if song_pattern_lines >= len(lines) * 0.5:
                self.stats['rejected_multi_song_list'] += 1
                return False, 'multi_song_list'
        
        # Check for multiple Artist - Song patterns in text
        dash_count = len(re.findall(r'[A-Za-z]{2,}[-–—][A-Za-z]{2,}', text))
        if dash_count >= 3:
            self.stats['rejected_multi_song_list'] += 1
            return False, 'multi_song_list'
        
        # Check for numbered/bulleted lists
        list_items = len(re.findall(r'^\s*[\d\.\)\-\*•]', text, re.MULTILINE))
        if list_items >= 3:
            self.stats['rejected_multi_song_list'] += 1
            return False, 'multi_song_list'
        
        # === YOUTUBE-SPECIFIC SPAM ===
        if source == 'youtube':
            for pattern in self.youtube_spam_patterns:
                if re.search(pattern, text_lower):
                    self.stats['rejected_youtube_spam'] += 1
                    return False, 'youtube_spam'
        
        # === GENERIC PHRASE CHECK ===
        for pattern in self.generic_patterns:
            if re.match(pattern, text_lower):
                self.stats['rejected_generic'] += 1
                return False, 'generic'
        
        # === SHALLOW PATTERN CHECK ===
        for pattern in self.shallow_patterns:
            if re.match(pattern, text_lower, re.IGNORECASE):
                self.stats['rejected_shallow'] += 1
                return False, 'shallow'
        
        # === EMOTIONAL DEPTH CHECK ===
        has_emotion = any(phrase in text_lower for phrase in self.emotional_phrases)
        if not has_emotion:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'
        
        # PASSED ALL CHECKS!
        self.stats['passed'] += 1
        return True, 'ok'
    
    def is_playlist_description(self, text: str) -> bool:
        """
        Quick check if text looks like a playlist/video description.
        Use this to NEVER use descriptions as comment fallback!
        
        Args:
            text: Text to check
            
        Returns:
            True if this looks like a description, False if it could be a comment
        """
        if not text:
            return True  # Empty = bad
        
        text_lower = text.lower()
        
        # Check for description indicators
        matches = sum(
            1 for pattern in self.playlist_desc_patterns 
            if re.search(pattern, text_lower)
        )
        
        # 1+ match = probably a description
        return matches >= 1
    
    def get_stats(self) -> Dict:
        """Get current filtering statistics."""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics for a new run."""
        for key in self.stats:
            self.stats[key] = 0
    
    def print_stats(self, source: str = 'scraper'):
        """Print filtering statistics in a nice format."""
        print("\n" + "="*60)
        print(f"UNIFIED QUALITY FILTER STATS - {source.upper()}")
        print("="*60)
        
        total = self.stats['examined']
        passed = self.stats['passed']
        
        if total > 0:
            pass_rate = passed / total * 100
            print(f"Examined: {total}")
            print(f"Passed:   {passed} ({pass_rate:.1f}%)")
        else:
            print("No comments examined yet.")
            return
        
        print(f"\nRejection breakdown:")
        rejection_keys = [
            'rejected_empty',
            'rejected_too_short',
            'rejected_too_long',
            'rejected_few_words',
            'rejected_url',
            'rejected_playlist_desc',
            'rejected_multi_song_list',
            'rejected_youtube_spam',
            'rejected_generic',
            'rejected_shallow',
            'rejected_no_emotion',
        ]
        
        for key in rejection_keys:
            val = self.stats.get(key, 0)
            if val > 0:
                label = key.replace('rejected_', '').replace('_', ' ')
                pct = val / total * 100
                print(f"  {label}: {val} ({pct:.1f}%)")
        
        print("="*60)


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == '__main__':
    """Test the filter with sample comments."""
    
    filter = UnifiedQualityFilter()
    
    # Test cases
    test_comments = [
        # Should PASS - genuine emotional content
        ("This song got me through my divorce. Every time I hear it, I'm transported back to those nights alone in my apartment, but now it feels healing.", "reddit"),
        ("Whenever I listen to this, it takes me back to summer 2019. We used to play this on every road trip.", "youtube"),
        
        # Should FAIL - playlist description
        ("Best Deep House Music Hits 2025 | Deep House Playlist | Subscribe for more!", "youtube"),
        ("Night Drive Playlist | Car Music playlist 2024, chill vibes. New music every week!", "youtube"),
        
        # Should FAIL - multi-song list
        ("1. Artist - Song\n2. Another - Track\n3. Third - Music\n4. Fourth - Tune", "reddit"),
        ("The Cure - Lovesong, Depeche Mode - Enjoy the Silence, New Order - Blue Monday", "reddit"),
        
        # Should FAIL - generic
        ("Great song!", "reddit"),
        ("This slaps!", "youtube"),
        ("Masterpiece", "youtube"),
        
        # Should FAIL - youtube spam
        ("Who's listening in 2024?", "youtube"),
        ("2:34 best part", "youtube"),
        ("Algorithm brought me here", "youtube"),
        
        # Should FAIL - too short
        ("Love it", "reddit"),
        
        # Should FAIL - no emotion
        ("This is a song by a band from the 90s. They made several albums.", "reddit"),
    ]
    
    print("="*70)
    print("UNIFIED QUALITY FILTER - TEST RESULTS")
    print("="*70)
    
    for text, source in test_comments:
        passed, reason = filter.check(text, source)
        status = "[PASS]" if passed else f"[FAIL: {reason}]"
        preview = text[:50] + "..." if len(text) > 50 else text
        preview = preview.replace('\n', ' ')
        print(f"{status:35} | {preview}")
    
    filter.print_stats('test')

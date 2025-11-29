"""
Quality Filters for Emotional Context Validation

These filters ensure we only scrape comments that provide genuine emotional context
about music, not spam, memes, or generic praise.

Per Replit's analysis: 70% of current data is garbage. These filters prevent that.
"""

import re
from typing import Dict, Optional


class QualityFilter:
    """
    Validates comment quality for emotional context.

    UPDATED Requirements (Nov 16, 2025 - relaxed after testing):
    - 30-500 character length (relaxed from 40-400)
    - Contains emotional language (1+ indicators, or 2+ if no first-person)
    - First-person is bonus but not required (allows "this makes you cry")
    - Expanded emotional vocabulary (70+ indicators vs original 42)
    - Reduced spam patterns (only truly spammy, not generic praise)
    - NO spam like "who's listening in 2024", "subscribe", "notification squad"
    """

    def __init__(self):
        self.stats = {
            'comments_examined': 0,
            'songs_extracted': 0,
            'quality_passed': 0,
            'rejected_too_short': 0,
            'rejected_too_long': 0,
            'rejected_spam': 0,
            'rejected_no_emotion': 0,
            'rejected_not_personal': 0
        }

        # Spam patterns (reduced - only truly spammy)
        self.spam_patterns = [
            r'who.*listening.*202\d',
            r'anyone.*202\d',
            r'\bi was here\b',
            r'before.*viral',
            r'subscribe',
            r'notification squad',
            r'^first!*$',
            r'pin this'
        ]

        # Emotional language indicators - EXPANDED for better coverage
        self.emotional_indicators = [
            # Original strong indicators
            'feel', 'felt', 'feeling', 'emotion', 'emotional',
            'helped me', 'helps me', 'help me',
            'going through', 'went through', 'been through',
            'reminds me', 'reminded me', 'remind me',
            'makes me', 'made me', 'make me',
            'when i', 'cry', 'cried', 'crying', 'tears',
            'healing', 'heal', 'relate', 'related', 'understand',
            'pain', 'hurt', 'hurting', 'heartbreak', 'broken',
            'depression', 'depressed', 'anxiety', 'anxious',
            'sad', 'sadness', 'lonely', 'loneliness',
            'happy', 'happiness', 'joy', 'joyful',
            'comfort', 'comforting', 'comforted',
            'struggle', 'struggling', 'struggled',
            # NEW - Common emotional expressions
            'resonates', 'resonate', 'hits different', 'speaks to',
            'captures', 'nails it', 'gets it', 'gets me',
            'therapeutic', 'cathartic', 'raw', 'vulnerable',
            'connected', 'connection', 'understood',
            'mood', 'atmosphere', 'melancholy', 'bittersweet',
            'nostalgia', 'nostalgic', 'takes me back',
            'saved my life', 'changed my life', 'got me through',
            'cope', 'coping', 'process', 'processing', 'deal with',
            'tough time', 'hard time', 'rough patch', 'dark place',
            'escape', 'solace', 'peace', 'calm', 'soothe',
            'powerful', 'moving', 'touching', 'beautiful',
            'vibe with', 'soundtrack', 'describes',
            # Second-person emotional (also valid!)
            'makes you', 'hits you', 'gets you', 'you feel',
            'you understand', 'speaks to you', "you'll cry",
            'when you', 'if you'
        ]

        # First-person indicators
        self.first_person_indicators = [
            'i ', 'my ', 'me ', 'mine ', "i'm", "i've", "i'd", "i'll"
        ]

    def is_quality_emotional_context(self, comment_text: str) -> tuple[bool, Optional[str]]:
        """
        Validate comment has genuine emotional context.

        Returns:
            (is_valid, rejection_reason)
        """
        self.stats['comments_examined'] += 1

        text = comment_text.strip()
        text_lower = text.lower()

        # Length validation: 30-500 characters (relaxed from 40-400)
        if len(text) < 30:
            self.stats['rejected_too_short'] += 1
            return False, 'too_short'

        if len(text) > 500:
            self.stats['rejected_too_long'] += 1
            return False, 'too_long'

        # No lyrics (multiple line breaks indicate copy-pasted lyrics)
        if text.count('\n') > 5:
            self.stats['rejected_too_long'] += 1
            return False, 'lyrics'

        # Check for spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, text_lower):
                self.stats['rejected_spam'] += 1
                return False, 'spam'

        # Require emotional language (at least 1 indicator - relaxed from 2)
        emotional_count = sum(
            1 for indicator in self.emotional_indicators
            if indicator in text_lower
        )

        if emotional_count < 1:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'

        # First-person is now a BONUS but not required
        # This allows second-person emotional comments like "this will make you cry"
        has_first_person = any(
            indicator in text_lower
            for indicator in self.first_person_indicators
        )

        # If no first-person, require stronger emotional signal (2+ indicators)
        if not has_first_person and emotional_count < 2:
            self.stats['rejected_not_personal'] += 1
            return False, 'not_personal'

        # Passed all checks
        self.stats['quality_passed'] += 1
        return True, None

    def get_stats(self) -> Dict:
        """Get current filtering statistics"""
        return self.stats.copy()

    def log_stats(self, logger) -> None:
        """Log filtering statistics"""
        total_extracted = self.stats['songs_extracted']
        quality_passed = self.stats['quality_passed']

        if total_extracted == 0:
            pass_rate = 0
        else:
            pass_rate = (quality_passed / total_extracted) * 100

        logger.info("="*70)
        logger.info("QUALITY FILTERING STATISTICS")
        logger.info("="*70)
        logger.info(f"Comments examined: {self.stats['comments_examined']}")
        logger.info(f"Songs extracted: {total_extracted}")
        logger.info(f"Quality passed: {quality_passed} ({pass_rate:.1f}%)")
        logger.info(f"")
        logger.info(f"REJECTIONS:")
        logger.info(f"  Too short (<40 chars): {self.stats['rejected_too_short']}")
        logger.info(f"  Too long/lyrics (>400 chars): {self.stats['rejected_too_long']}")
        logger.info(f"  Spam/generic: {self.stats['rejected_spam']}")
        logger.info(f"  No emotional content: {self.stats['rejected_no_emotion']}")
        logger.info(f"  Not personal/first-person: {self.stats['rejected_not_personal']}")
        logger.info("="*70)

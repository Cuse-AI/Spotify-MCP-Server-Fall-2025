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

    Requirements per Replit analysis:
    - 40-400 character length
    - Contains emotional language (2+ indicators)
    - First-person personal experience
    - NO spam, memes, jokes, generic praise
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

        # Spam patterns that indicate low-quality comments
        self.spam_patterns = [
            r'masterpiece',
            r'best song ever',
            r'underrated',
            r'who.*listening.*202\d',
            r'anyone.*202\d',
            r'i was here',
            r'before.*viral',
            r'subscribe',
            r'notification',
            r'never gets old',
            r'love this song$',
            r'this is amazing$',
            r'this slaps$',
            r'banger$',
            r'fire$',
            r'vibe$'
        ]

        # Emotional language indicators
        self.emotional_indicators = [
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
            'struggle', 'struggling', 'struggled'
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

        # Length validation: 40-400 characters
        if len(text) < 40:
            self.stats['rejected_too_short'] += 1
            return False, 'too_short'

        if len(text) > 400:
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

        # Require emotional language (at least 2 indicators)
        emotional_count = sum(
            1 for indicator in self.emotional_indicators
            if indicator in text_lower
        )

        if emotional_count < 2:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'

        # Require first-person (personal experience)
        has_first_person = any(
            indicator in text_lower
            for indicator in self.first_person_indicators
        )

        if not has_first_person:
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

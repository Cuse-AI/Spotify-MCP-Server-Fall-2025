"""
IMPROVED Quality Filters for Emotional Context Validation
Based on test results: 96% rejection was too strict. These filters aim for 20-30% pass rate.

Changes from original:
- Min length: 40 → 30 characters
- Emotional indicators required: 2+ → 1+
- First-person: Now optional (bonus, not requirement)
- Added 50+ more emotional keywords
- Added context-awareness (relaxes filters for emotional post titles)
"""

import re
from typing import Dict, Optional, Tuple

class ImprovedQualityFilter:
    """
    Validates comment quality for emotional context - IMPROVED VERSION
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
            'rejected_not_personal': 0,
            'context_boost_applied': 0
        }

        # Spam patterns (unchanged)
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
            r'love this song',
            r'this is amazing',
            r'this slaps',
            r'banger',
            r'fire',
            r'vibe check'
        ]

        # EXPANDED emotional language indicators (from 42 → 90+)
        self.emotional_indicators = [
            # Original indicators
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

            # NEW: Strong emotional phrases
            'soundtrack to my', 'this song saved', 'changed my life',
            'saved my life', 'got me through',

            # NEW: Emotional resonance
            'resonates', 'resonate', 'hits different', 'speaks to',
            'captures the feeling', 'nails the feeling', 'gets it',
            'understood me', 'connected to', 'connection',

            # NEW: Therapeutic language
            'therapeutic', 'cathartic', 'raw emotion', 'vulnerable',
            'vulnerability', 'honest', 'real', 'authentic',

            # NEW: Mood/atmosphere
            'vibe with', 'vibes', 'mood', 'atmosphere',
            'melancholy', 'bittersweet', 'nostalgia', 'nostalgic',
            'takes me back', 'reminds me of when',

            # NEW: Coping/processing
            'cope', 'coping', 'process', 'processing', 'deal with',
            'dealing with', 'work through', 'working through',

            # NEW: Comfort/solace
            'solace', 'escape', 'refuge', 'safe place',
            'comfort zone', 'peaceful', 'calming',

            # NEW: Second-person emotional (captures "makes you feel" type comments)
            'makes you feel', "you'll cry", 'hits you', 'gets you',
            'you can feel', 'you understand', 'speaks to you',
            'you relate', 'resonates with you'
        ]

        # First-person indicators (now optional)
        self.first_person_indicators = [
            'i ', 'my ', 'me ', 'mine ', "i'm", "i've", "i'd", "i'll"
        ]

        # NEW: Emotional post title indicators (for context-awareness)
        self.emotional_post_titles = [
            'makes you cry', 'makes you feel', 'reminds you of',
            'what song', 'hits you in the feels', 'emotional',
            'sad songs', 'depressing', 'heartbreak', 'breakup',
            'lonely', 'depression', 'anxiety', 'grief', 'loss',
            'healing', 'comfort', 'therapeutic', 'cathartic',
            'cry', 'tears', 'feelings', 'emotions'
        ]

    def is_emotional_post_context(self, post_title: str) -> bool:
        """Check if the post itself is asking for emotional content"""
        if not post_title:
            return False

        title_lower = post_title.lower()
        return any(indicator in title_lower for indicator in self.emotional_post_titles)

    def is_quality_emotional_context(
        self,
        comment_text: str,
        post_title: str = '',
        post_body: str = ''
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate comment has genuine emotional context - IMPROVED VERSION

        Returns:
            (is_valid, rejection_reason)
        """
        self.stats['comments_examined'] += 1

        text = comment_text.strip()
        text_lower = text.lower()

        # Check if post context is emotional (enables context boost)
        context_is_emotional = self.is_emotional_post_context(post_title) or \
                              self.is_emotional_post_context(post_body)

        # Length validation: 30-400 characters (relaxed from 40)
        if len(text) < 30:
            self.stats['rejected_too_short'] += 1
            return False, 'too_short'

        if len(text) > 400:
            self.stats['rejected_too_long'] += 1
            return False, 'too_long'

        # No lyrics (multiple line breaks)
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

        # Context-aware filtering: If post is emotional, be more lenient
        required_emotional_count = 1 if not context_is_emotional else 0

        if emotional_count < required_emotional_count:
            self.stats['rejected_no_emotion'] += 1
            return False, 'no_emotion'

        # First-person is now OPTIONAL (not required)
        # But we still track it as a quality signal
        has_first_person = any(
            indicator in text_lower
            for indicator in self.first_person_indicators
        )

        # If context is emotional, we don't need first-person at all
        if context_is_emotional:
            self.stats['context_boost_applied'] += 1
        elif not has_first_person and emotional_count < 2:
            # If NO first-person AND only 1 emotional indicator, reject
            # (prevents generic descriptions like "this song is sad")
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
        logger.info("IMPROVED QUALITY FILTERING STATISTICS")
        logger.info("="*70)
        logger.info(f"Comments examined: {self.stats['comments_examined']}")
        logger.info(f"Songs extracted: {total_extracted}")
        logger.info(f"Quality passed: {quality_passed} ({pass_rate:.1f}%)")
        logger.info(f"Context boosts applied: {self.stats['context_boost_applied']}")
        logger.info(f"")
        logger.info(f"REJECTIONS:")
        logger.info(f"  Too short (<30 chars): {self.stats['rejected_too_short']}")
        logger.info(f"  Too long/lyrics (>400 chars): {self.stats['rejected_too_long']}")
        logger.info(f"  Spam/generic: {self.stats['rejected_spam']}")
        logger.info(f"  No emotional content: {self.stats['rejected_no_emotion']}")
        logger.info(f"  Not personal (generic description): {self.stats['rejected_not_personal']}")
        logger.info("="*70)

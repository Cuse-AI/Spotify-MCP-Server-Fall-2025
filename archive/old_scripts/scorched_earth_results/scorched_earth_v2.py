"""
SCORCHED EARTH CLASSIFIER v2
============================
Improved based on Replit's analysis:
- Lyric + reaction combos = GOLD (were getting cut before)
- Pure lyric dumps = CUT (were getting false gold)
- Action statements ("ending this relationship today") = bonus
- Temporal transformation ("2009: knew it. 2025: understand it") = bonus
- Off-topic artist praise = penalty
- Length bonus ONLY if not mostly lyrics
"""

import json
import re
from pathlib import Path
from datetime import datetime


def is_mostly_lyrics(text):
    """
    Detect if text is mostly copied lyrics vs personal content.
    IMPROVED: Don't flag personal stories with '...' or 'I' statements
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    if len(lines) < 4:
        return False
    
    # Check for strong personal markers FIRST - if found, NOT lyrics
    personal_markers = [
        r'\bi (cry|cried|feel|felt|was|am|remember|think|went|had|have)\b',
        r'\bmy (wife|husband|ex|mom|dad|friend|heart|soul)\b',
        r'\bwhen i\b',
        r'\bgot me through\b',
        r'\bthe (pain|depression|grief)\b',
        r'\.{3,}',  # Multiple dots like "..." often indicates personal stories
    ]
    personal_count = sum(1 for p in personal_markers if re.search(p, text, re.I))
    if personal_count >= 2:
        return False  # Has personal content, NOT a lyric dump
    
    # Multiple lines with capitalized starts AND poetic structure = likely lyrics
    cap_lines = sum(1 for l in lines if l and l[0].isupper())
    if cap_lines >= len(lines) * 0.8 and len(lines) >= 5:
        # Additional check: lyrics don't usually have "I was" "I am" "I feel" personal statements
        personal_lines = sum(1 for l in lines if re.search(r'\bi\s+(was|am|feel|went|had|cried|remember)', l, re.I))
        if personal_lines < 1:
            return True
    
    return False


def score_comment_v2(comment):
    """
    Score a comment for emotional quality - IMPROVED VERSION.
    Returns (score, reasons, warnings)
    """
    if not comment or not comment.strip():
        return 0, ['empty'], []
    
    text = comment.strip()
    c = text.lower()
    words = len(c.split())
    score = 0
    reasons = []
    warnings = []
    
    # =========================================================================
    # INSTANT REJECTION (return 0 immediately)
    # =========================================================================
    
    # Too short
    if len(text) < 25:
        return 0, ['too_short'], []
    
    # Video/YouTube spam
    video_spam = [
        r"who'?s?\s+(still\s+)?(here|listening|watching)",
        r"still (listening|watching) in 20\d\d",
        r"anyone else (here|listening)",
        r"like if you",
        r"first comment|early gang",
        r"write.*before.*viral",
        r"i was here before",
        r"notification squad",
        r"your (cat|dog|video|channel)",
        r"subscribe",
    ]
    for pattern in video_spam:
        if re.search(pattern, c):
            return 0, ['video_spam'], []
    
    # Song list dumps (Artist - Song repeated)
    if c.count(' - ') >= 2 and words < 50:
        return 0, ['song_list_dump'], []
    if re.search(r'[A-Z][a-z]+\s*-\s*[A-Z].{5,}\n[A-Z][a-z]+\s*-\s*[A-Z]', text):
        return 0, ['song_list_dump'], []
    
    # Generic short praise
    generic_short = ['love it', 'amazing', 'fire', 'goated', 'beautiful', 'perfect', 
                     'masterpiece', 'banger', 'slaps', 'vibes', 'mood', 'underrated']
    if words < 10 and any(x in c for x in generic_short):
        return 0, ['generic_short'], []
    
    # =========================================================================
    # LYRIC DUMP DETECTION (heavy penalty, not instant reject)
    # =========================================================================
    
    is_lyrics = is_mostly_lyrics(text)
    if is_lyrics:
        warnings.append('mostly_lyrics')
        score -= 4  # Heavy penalty but might have reaction at end
    
    # =========================================================================
    # POSITIVE SCORING
    # =========================================================================
    
    # First person (base requirement)
    has_first_person = bool(re.search(r'\b(i|me|my|we|our|i\'m|i\'ve|i\'d|myself)\b', c))
    if has_first_person:
        score += 1
        reasons.append('first_person')
    
    # Story context markers (+2 each, max 4)
    story_patterns = [
        r'\b(when i was|back when|years ago|remember when)\b',
        r'\b(after my|during my|before my)\b',
        r'\b(used to|i once|there was a time)\b',
        r'\b(last (year|month|week)|recently)\b',
    ]
    story_count = sum(1 for p in story_patterns if re.search(p, c))
    if story_count > 0:
        score += min(story_count * 2, 4)
        reasons.append(f'story_context_{story_count}')
    
    # Cause-effect language (+2 each, max 4)
    cause_effect = [
        r'\b(makes? me feel|made me feel)\b',
        r'\b(helps? me|helped me)\b',
        r'\b(brings? me|brought me)\b',
        r'\b(takes? me back|took me back)\b',
        r'\b(reminds? me|reminded me)\b',
        r'\b(got me through|gets me through)\b',
        r'\b(allows? me to)\b',
    ]
    cause_count = sum(1 for p in cause_effect if re.search(p, c))
    if cause_count > 0:
        score += min(cause_count * 2, 4)
        reasons.append(f'cause_effect_{cause_count}')
    
    # Life events (+2)
    life_events = [
        r'\b(break.?up|breakup|divorce|separated)\b',
        r'\b(passed away|died|death|funeral|lost (my|someone))\b',
        r'\b(wedding|married|engagement)\b',
        r'\b(hospital|surgery|cancer|illness)\b',
        r'\b(depression|anxiety|grief|healing|recovery)\b',
        r'\b(deployed|military)\b',
        r'\b(rehab|addiction|sober)\b',
        r'\b(toxic relationship|abusive)\b',
        r'\b(walked out|left me|cheated)\b',  # NEW: relationship endings
        r'\b(homeless|shelter)\b',  # NEW: hardship
        r'\b(my (wife|husband|ex|girlfriend|boyfriend|partner))\b',  # NEW: relationship context
    ]
    if any(re.search(p, c) for p in life_events):
        score += 2
        reasons.append('life_event')
    
    # Emotional words (+1 each, max 4)
    emotional_words = [
        r'\b(cry|crying|cried|tears|sob|weep)\b',
        r'\b(my (heart|soul|chest))\b',
        r'\b(goosebumps|chills|shivers)\b',
        r'\b(destroyed|wrecked|broke me|hit me hard)\b',
        r'\b(saved my life|kept me going)\b',
        r'\b(healing|peace|comfort)\b',
        r'\b(miss|missing|longing|nostalgia)\b',
    ]
    emotion_count = sum(1 for p in emotional_words if re.search(p, c))
    if emotion_count > 0:
        score += min(emotion_count, 4)
        reasons.append(f'emotional_words_{emotion_count}')
    
    # NEW: Lyric + reaction combo (+3) - THIS IS GOLD
    # Someone quotes a lyric AND reacts to it personally
    # Handle both straight quotes "..." and curly quotes "..." and fancy quotes
    lyric_reaction_patterns = [
        r'["\u201c\u201d\u201e\u201f][^"\u201c\u201d\u201e\u201f]{10,}["\u201c\u201d\u201e\u201f].{0,30}(destroyed|broke|hit|kills?|hurts?|gets? me)',
        r'["\u201c\u201d\u201e\u201f][^"\u201c\u201d\u201e\u201f]{10,}["\u201c\u201d\u201e\u201f].{0,30}(this (line|part|lyric))',
        r'(this (line|lyric|part|verse)).{0,30}["\u201c\u201d]',
        r'["\u201c\u201d][^"\u201c\u201d]{10,}["\u201c\u201d]\s*(!{2,}|what a)',
        r'(what a lyric|what a line)',
        r'(this line|that line|this part).{0,20}(destroyed|broke|hit|kills|got me)',
        r'(destroyed me|broke me|hit me hard|kills me)',  # Even without quotes
    ]
    if any(re.search(p, c) for p in lyric_reaction_patterns):
        score += 3
        reasons.append('lyric_reaction')
    
    # NEW: Action statements (+2) - doing something RIGHT NOW
    action_patterns = [
        r"\b(i'm (ending|leaving|starting|going through|finally))\b",
        r'\b(moving out|walking away|letting go)\b',
        r'\b(finally (left|ended|realized|understood))\b',
        r'\b(today i|right now i|currently going)\b',
        r'\b(wish me luck)\b',
    ]
    if any(re.search(p, c) for p in action_patterns):
        score += 2
        reasons.append('action_statement')
    
    # NEW: Temporal transformation (+3) - song meaning evolved over time
    temporal_patterns = [
        r'20\d\d:.{5,50}20\d\d:',  # "2009: X. 2025: Y"
        r"\b(back then|at first).{10,50}(now i|today i|finally)",
        r"\b(didn't understand|didn't get it).{5,30}(now i|finally)",
        r"\b(years later).{5,30}(understand|realize|feel)",
    ]
    if any(re.search(p, c) for p in temporal_patterns):
        score += 3
        reasons.append('temporal_transformation')
    
    # Repeated connection (+2) - song they keep returning to
    repeated_patterns = [
        r'\b(every time i (hear|listen|play))\b',
        r"\b(can't stop (listening|playing))\b",
        r'\b(on repeat|over and over)\b',
        r'\b(always (come back|return) to)\b',
        r'\b(never fails to)\b',
    ]
    if any(re.search(p, c) for p in repeated_patterns):
        score += 2
        reasons.append('repeated_connection')
    
    # Length bonus (ONLY if not mostly lyrics!)
    if not is_lyrics:
        if words >= 40:
            score += 2
            reasons.append('great_length')
        elif words >= 20:
            score += 1
            reasons.append('good_length')
    
    # =========================================================================
    # NEGATIVE SCORING (penalties)
    # =========================================================================
    
    # Off-topic (about artist/video, not emotional connection) (-2)
    off_topic = [
        r'\b(underrated artist|deserves more)\b',
        r'\b(never released a bad song)\b',
        r'\b(one of (his|her|their) best)\b',
        r'\b(people (slept on|don\'t appreciate))\b',
        r'\b(genius|legend|goat)\b',
    ]
    if any(re.search(p, c) for p in off_topic) and score < 5:
        score -= 2
        warnings.append('off_topic')
    
    # No personal connection at all (-2)
    if not has_first_person and emotion_count == 0 and cause_count == 0:
        score -= 2
        warnings.append('no_personal_connection')
    
    # Agreement-only without depth (-2)
    agreement_only = [
        r'\b(belongs here|perfect for|fits perfectly)\b',
        r'\b(great addition|adding this|saved)\b',
        r'\b(this belongs|should be on)\b',
    ]
    if any(re.search(p, c) for p in agreement_only) and score < 4:
        score -= 2
        warnings.append('agreement_only')
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    return score, reasons, warnings


def classify_tapestry(tapestry_path):
    """Load tapestry and classify all songs into GOLD/REVIEW/CUT buckets"""
    print(f"Loading tapestry from {tapestry_path}...")
    with open(tapestry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    gold = []      # Score >= 6 - definite keepers
    review = []    # Score 4-5 - need manual review  
    cut = []       # Score < 4 - delete
    
    all_scores = []
    
    for vibe_name, vibe_data in data['vibes'].items():
        for song in vibe_data.get('songs', []):
            comment = song.get('comment_text', '')
            score, reasons, warnings = score_comment_v2(comment)
            
            song_entry = {
                'artist': song.get('artist', 'Unknown'),
                'song': song.get('song', 'Unknown'),
                'vibe': vibe_name,
                'score': score,
                'reasons': reasons,
                'warnings': warnings,
                'comment': comment[:300],
                'spotify_id': song.get('spotify_id', ''),
                'full_data': song
            }
            
            all_scores.append(score)
            
            if score >= 6:
                gold.append(song_entry)
            elif score >= 4:
                review.append(song_entry)
            else:
                cut.append(song_entry)
    
    return gold, review, cut, all_scores


def print_examples(bucket, name, count=8):
    """Print example songs from a bucket"""
    print(f"\n{'='*70}")
    print(f"  {name} EXAMPLES (showing {min(count, len(bucket))} of {len(bucket)})")
    print(f"{'='*70}")
    for song in bucket[:count]:
        print(f"\n  [{song['score']}] {song['artist']} - {song['song']}")
        print(f"      Reasons: {', '.join(song['reasons']) if song['reasons'] else 'none'}")
        if song['warnings']:
            print(f"      Warnings: {', '.join(song['warnings'])}")
        comment_preview = song['comment'][:120].replace('\n', ' ')
        print(f"      Comment: {comment_preview}...")


def save_buckets(gold, review, cut, output_dir):
    """Save buckets to JSON files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for bucket, name in [(gold, 'GOLD_v2'), (review, 'REVIEW_v2'), (cut, 'CUT_v2')]:
        clean_bucket = [{k: v for k, v in s.items() if k != 'full_data'} for s in bucket]
        filepath = output_dir / f'{name}_{timestamp}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_bucket, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(bucket)} songs to {filepath.name}")
    
    return timestamp


def build_gold_tapestry(gold, review_approved, original_path, output_path):
    """Build new tapestry with only approved songs"""
    with open(original_path, 'r', encoding='utf-8') as f:
        original = json.load(f)
    
    # Combine gold + approved review songs
    all_approved = gold + review_approved
    
    # Group by vibe
    by_vibe = {}
    for song in all_approved:
        vibe = song['vibe']
        if vibe not in by_vibe:
            by_vibe[vibe] = []
        by_vibe[vibe].append(song['full_data'])
    
    # Build new tapestry
    new_tapestry = {'vibes': {}}
    for vibe_name in original['vibes'].keys():
        if vibe_name in by_vibe:
            new_tapestry['vibes'][vibe_name] = {'songs': by_vibe[vibe_name]}
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_tapestry, f, indent=2, ensure_ascii=False)
    
    total = sum(len(v['songs']) for v in new_tapestry['vibes'].values())
    print(f"\nBuilt GOLD tapestry: {total} songs across {len(new_tapestry['vibes'])} vibes")
    return new_tapestry


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent
    tapestry_path = base_dir / 'core' / 'tapestry.json'
    output_dir = base_dir / 'analysis' / 'scorched_earth_output'
    
    print("=" * 70)
    print("  SCORCHED EARTH CLASSIFIER v2")
    print("  With Replit's improvements: lyric+reaction, action statements,")
    print("  temporal transformation, lyric dump detection")
    print("=" * 70)
    
    # Run classification
    gold, review, cut, all_scores = classify_tapestry(tapestry_path)
    
    # Statistics
    total = len(gold) + len(review) + len(cut)
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"\n{'='*70}")
    print(f"  RESULTS SUMMARY (v2 - Improved Classifier)")
    print(f"{'='*70}")
    print(f"  Total songs analyzed: {total}")
    print(f"  Average score: {avg_score:.2f}")
    print(f"")
    print(f"  GOLD (score >= 6):   {len(gold):>5} ({100*len(gold)/total:.1f}%) - DEFINITE KEEP")
    print(f"  REVIEW (score 4-5):  {len(review):>5} ({100*len(review)/total:.1f}%) - YOU DECIDE")
    print(f"  CUT (score < 4):     {len(cut):>5} ({100*len(cut)/total:.1f}%) - DELETE")
    
    # Score distribution
    print(f"\n  Score Distribution:")
    for i in range(max(all_scores) + 1):
        count = sum(1 for s in all_scores if s == i)
        bar = '#' * (count // 30)
        print(f"    {i:>2}: {count:>4} {bar}")
    
    # Show examples
    print_examples(gold, "GOLD", 8)
    print_examples(review, "REVIEW", 8)
    print_examples(cut, "CUT", 8)
    
    # Save buckets
    print(f"\n{'='*70}")
    print(f"  SAVING BUCKETS")
    print(f"{'='*70}")
    timestamp = save_buckets(gold, review, cut, output_dir)
    
    print(f"\n{'='*70}")
    print(f"  FILES SAVED TO: analysis/scorched_earth_output/")
    print(f"  - GOLD_v2_{timestamp}.json")
    print(f"  - REVIEW_v2_{timestamp}.json")
    print(f"  - CUT_v2_{timestamp}.json")
    print(f"{'='*70}")

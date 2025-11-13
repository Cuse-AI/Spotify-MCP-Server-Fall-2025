"""
Restructure Master Clean CSV for Model Training
Transforms data into explicit vibe → song → reasoning relationships
Creates a "tree structure" for Claude to build mental models from
"""

import pandas as pd
import re
from datetime import datetime


class DataRestructurer:
    def __init__(self):
        # Keywords that indicate non-music posts
        self.non_music_keywords = [
            'maga', 'trump', 'christian', 'political', 'election',
            'courtney stodden', 'marriage', 'legal', 'spotify quit',
            'ice ads', 'daniel elk', 'ai weapons', 'era has lost',
            'kenny loggins wants', 'removed from'
        ]

        # Subreddit to genre mapping (approximate)
        self.subreddit_genres = {
            'jazz': 'Jazz',
            'experimentalmusic': 'Experimental',
            'ambientmusic': 'Ambient/Electronic',
            'electronicmusic': 'Electronic',
            'Metal': 'Metal',
            'hiphopheads': 'Hip-Hop',
            'indieheads': 'Indie',
            'psychedelicrock': 'Psychedelic/Rock',
            'FolkPunk': 'Folk/Punk',
            'WorldMusic': 'World Music',
            'musicsuggestions': 'Various',
            'ifyoulikeblank': 'Various',
            'ListenToThis': 'Various',
            'LetsTalkMusic': 'Various',
            'popheads': 'Pop',
            'Music': 'Various',
            'spotify': 'Various'
        }

    def is_music_post(self, title, full_text):
        """Filter out non-music posts"""
        combined = (title + " " + full_text).lower()

        # Check for non-music keywords
        for keyword in self.non_music_keywords:
            if keyword in combined:
                return False

        # Must contain music-related indicators
        music_indicators = [
            'song', 'music', 'album', 'artist', 'playlist', 'recommend',
            'vibe', 'genre', 'track', 'listen', 'sound'
        ]

        has_music_indicator = any(indicator in combined for indicator in music_indicators)

        return has_music_indicator

    def extract_vibe_description(self, title, full_text):
        """Extract clean vibe description from post"""
        # Use title as primary vibe
        vibe = title.strip()

        # If there's additional context in full_text, include first sentence
        if full_text and len(full_text) > 10:
            # Get first meaningful sentence (up to 200 chars)
            first_part = full_text[:200].split('.')[0].strip()
            if first_part and first_part != title:
                vibe = f"{title} - {first_part}"

        # Clean up common artifacts
        vibe = re.sub(r'\s+', ' ', vibe)  # Multiple spaces
        vibe = re.sub(r'\n+', ' ', vibe)  # Newlines

        return vibe

    def extract_reasoning(self, comment_context, extraction_method):
        """Extract why this song was recommended"""
        if not comment_context or len(comment_context) < 10:
            return "Direct recommendation"

        # Clean up comment
        reasoning = comment_context.strip()

        # Remove the song/artist names from reasoning (they're in separate columns)
        # This leaves just the commentary about WHY
        reasoning = re.sub(r'"[^"]+" by [A-Za-z\s\'-]+', '[SONG]', reasoning)
        reasoning = re.sub(r'[A-Z][A-Za-z\s\'-]+ - [A-Za-z\s\'-]+', '[SONG]', reasoning)

        # Truncate to reasonable length
        if len(reasoning) > 300:
            reasoning = reasoning[:297] + "..."

        return reasoning if reasoning else "Direct recommendation"

    def infer_genre(self, subreddit, vibe_text, reasoning):
        """Infer genre from subreddit and context"""
        # Start with subreddit mapping
        genre = self.subreddit_genres.get(subreddit, 'Various')

        # If "Various", try to infer from text
        if genre == 'Various':
            combined = (vibe_text + " " + reasoning).lower()

            genre_keywords = {
                'Jazz': ['jazz', 'bebop', 'swing', 'spiritual jazz', 'free jazz'],
                'Experimental': ['experimental', 'noise', 'avant-garde', 'weird', 'abstract'],
                'Classical': ['classical', 'orchestra', 'symphony', 'opera', 'baroque'],
                'Folk': ['folk', 'acoustic', 'traditional', 'bluegrass', 'appalachian'],
                'Rock': ['rock', 'punk', 'grunge', 'alternative'],
                'Metal': ['metal', 'doom', 'black metal', 'death metal', 'heavy'],
                'Electronic': ['electronic', 'edm', 'techno', 'house', 'ambient', 'idm'],
                'Hip-Hop': ['hip hop', 'rap', 'trap', 'underground'],
                'Country': ['country', 'nashville', 'bluegrass'],
                'R&B/Soul': ['r&b', 'soul', 'funk', 'motown'],
                'Indie': ['indie', 'indie rock', 'indie pop'],
                'Pop': ['pop', 'mainstream', 'charts']
            }

            for genre_name, keywords in genre_keywords.items():
                if any(keyword in combined for keyword in keywords):
                    genre = genre_name
                    break

        return genre

    def infer_vibe_category(self, vibe_text):
        """Categorize the vibe/emotion being requested"""
        text = vibe_text.lower()

        # Emotional categories
        if any(word in text for word in ['sad', 'depressing', 'melancholic', 'grief', 'loss', 'cry']):
            return 'Emotional/Sad'
        elif any(word in text for word in ['happy', 'upbeat', 'cheerful', 'joyful', 'fun']):
            return 'Happy/Upbeat'
        elif any(word in text for word in ['angry', 'aggressive', 'rage', 'intense']):
            return 'Angry/Intense'
        elif any(word in text for word in ['chill', 'relaxing', 'calm', 'peaceful', 'mellow']):
            return 'Chill/Relaxing'
        elif any(word in text for word in ['energy', 'pump', 'hype', 'workout', 'gym', 'motivation']):
            return 'Energetic/Motivational'
        elif any(word in text for word in ['introspective', 'contemplative', 'thinking', 'philosophical']):
            return 'Introspective/Thoughtful'
        elif any(word in text for word in ['nostalgia', 'nostalgic', 'memories', 'throwback']):
            return 'Nostalgic'
        elif any(word in text for word in ['sexy', 'sensual', 'romantic', 'love']):
            return 'Romantic/Sensual'
        elif any(word in text for word in ['dark', 'eerie', 'creepy', 'haunting', 'gothic']):
            return 'Dark/Atmospheric'
        elif any(word in text for word in ['study', 'focus', 'concentration', 'work']):
            return 'Focus/Study'
        elif any(word in text for word in ['party', 'dance', 'club', 'night out']):
            return 'Party/Dance'
        elif any(word in text for word in ['driving', 'road trip', 'car']):
            return 'Driving/Travel'
        elif any(word in text for word in ['sleep', 'bedtime', 'night', '3am']):
            return 'Night/Sleep'
        elif any(word in text for word in ['discover', 'hidden', 'obscure', 'unknown', 'deep cut']):
            return 'Discovery/Exploration'
        elif any(word in text for word in ['brilliant', 'genius', 'innovative', 'unique']):
            return 'Innovative/Unique'
        else:
            return 'Other'

    def restructure_data(self, input_csv_path):
        """Main restructuring function"""
        print("=" * 70)
        print("RESTRUCTURING DATA FOR MODEL TRAINING")
        print("=" * 70)
        print("\nLoading master clean CSV...")

        df = pd.read_csv(input_csv_path, encoding='utf-8')
        print(f"Loaded {len(df)} rows")

        # Filter music-only posts
        print("\nFiltering for music-only posts...")
        df['is_music'] = df.apply(
            lambda row: self.is_music_post(
                str(row['vibe_request_title']),
                str(row['vibe_request_full'])
            ),
            axis=1
        )
        df_music = df[df['is_music']].copy()
        print(f"Kept {len(df_music)} music posts ({len(df) - len(df_music)} filtered out)")

        # Create new structured columns
        print("\nCreating structured columns...")

        df_music['vibe_description'] = df_music.apply(
            lambda row: self.extract_vibe_description(
                str(row['vibe_request_title']),
                str(row['vibe_request_full'])
            ),
            axis=1
        )

        df_music['recommendation_reasoning'] = df_music.apply(
            lambda row: self.extract_reasoning(
                str(row.get('vibe_request_full', '')),
                str(row['extraction_method'])
            ),
            axis=1
        )

        df_music['genre_category'] = df_music.apply(
            lambda row: self.infer_genre(
                str(row['subreddit']),
                str(row['vibe_request_title']),
                str(row.get('vibe_request_full', ''))
            ),
            axis=1
        )

        df_music['vibe_category'] = df_music['vibe_description'].apply(
            self.infer_vibe_category
        )

        # Create final structured dataframe
        df_final = pd.DataFrame({
            'vibe_category': df_music['vibe_category'],
            'vibe_description': df_music['vibe_description'],
            'song_name': df_music['song_name'],
            'artist_name': df_music['artist_name'],
            'recommendation_reasoning': df_music['recommendation_reasoning'],
            'genre_category': df_music['genre_category'],
            'subreddit': df_music['subreddit'],
            'comment_score': df_music['comment_score'],
            'extraction_confidence': df_music['extraction_method'].map({
                'quoted_by': 'high',
                'dash_format': 'medium',
                'unquoted_by': 'medium'
            }),
            'source_url': df_music['permalink'],
            'data_source': df_music['data_source']
        })

        # Sort by vibe_category, then by comment_score
        df_final = df_final.sort_values(
            by=['vibe_category', 'comment_score'],
            ascending=[True, False]
        )

        return df_final

    def save_structured_data(self, df, output_path):
        """Save restructured data and generate report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        csv_path = output_path.replace('.csv', f'_STRUCTURED_{timestamp}.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8')

        print(f"\n[OK] Saved structured CSV: {csv_path}")

        # Generate analysis report
        report_path = output_path.replace('.csv', f'_STRUCTURE_REPORT_{timestamp}.txt')

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("STRUCTURED DATA ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Total Recommendations: {len(df)}\n")
            f.write(f"Unique Songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}\n")
            f.write(f"Unique Vibes: {df['vibe_description'].nunique()}\n\n")

            f.write("VIBE CATEGORY DISTRIBUTION:\n")
            f.write("-" * 70 + "\n")
            for category, count in df['vibe_category'].value_counts().items():
                f.write(f"  {category}: {count} recommendations\n")

            f.write("\nGENRE DISTRIBUTION:\n")
            f.write("-" * 70 + "\n")
            for genre, count in df['genre_category'].value_counts().items():
                f.write(f"  {genre}: {count} recommendations\n")

            f.write("\nEXTRACTION CONFIDENCE:\n")
            f.write("-" * 70 + "\n")
            for conf, count in df['extraction_confidence'].value_counts().items():
                f.write(f"  {conf}: {count} recommendations\n")

            f.write("\nSUBREDDIT DISTRIBUTION:\n")
            f.write("-" * 70 + "\n")
            for sub, count in df['subreddit'].value_counts().head(15).items():
                f.write(f"  r/{sub}: {count} recommendations\n")

            f.write("\nSAMPLE VIBE -> SONG RELATIONSHIPS:\n")
            f.write("-" * 70 + "\n")

            # Show examples from different vibe categories
            for category in df['vibe_category'].unique()[:5]:
                f.write(f"\n[{category}]\n")
                samples = df[df['vibe_category'] == category].head(3)
                for _, row in samples.iterrows():
                    f.write(f"  Vibe: {row['vibe_description'][:80]}...\n")
                    f.write(f"  Song: \"{row['song_name']}\" by {row['artist_name']}\n")
                    f.write(f"  Genre: {row['genre_category']}\n")
                    if row['recommendation_reasoning'] != 'Direct recommendation':
                        f.write(f"  Why: {row['recommendation_reasoning'][:100]}...\n")
                    f.write("\n")

        print(f"[OK] Saved analysis report: {report_path}")

        # Print summary to console
        print("\n" + "=" * 70)
        print("RESTRUCTURING COMPLETE!")
        print("=" * 70)
        print(f"\nTotal recommendations: {len(df)}")
        print(f"Unique songs: {len(df[['song_name', 'artist_name']].drop_duplicates())}")
        print(f"\nVibe categories: {df['vibe_category'].nunique()}")
        print(f"Genre categories: {df['genre_category'].nunique()}")
        print(f"Subreddits: {df['subreddit'].nunique()}")

        print("\nTop vibe categories:")
        for category, count in df['vibe_category'].value_counts().head(10).items():
            print(f"  {category}: {count}")

        print(f"\nFiles created:")
        print(f"  {csv_path}")
        print(f"  {report_path}")

        return csv_path, report_path


def main():
    input_csv = "MASTER_CLEAN_VIBES_20251107_141407.csv"

    restructurer = DataRestructurer()

    print("\nRestructuring data into explicit vibe -> song -> reasoning format...")
    df_structured = restructurer.restructure_data(input_csv)

    print(f"\nSaving structured data...")
    csv_path, report_path = restructurer.save_structured_data(df_structured, input_csv)

    print("\n" + "=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print("\nThe data is now organized for model training with:")
    print("  - Clear vibe descriptions")
    print("  - Song/artist pairs")
    print("  - Reasoning/commentary (why it fits)")
    print("  - Genre and vibe categories")
    print("  - Source URLs for verification")
    print("\nThis structure creates a 'tree' of vibe -> song relationships")
    print("that Claude can use to build a mental model of music recommendations!")


if __name__ == "__main__":
    main()

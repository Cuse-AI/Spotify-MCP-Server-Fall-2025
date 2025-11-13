# Spotify Playlist Scraping

This folder contains the Spotify playlist scraper for collecting vibe descriptions and track listings from curated Spotify playlists.

## 🎯 Goal

Collect authentic vibe language from Spotify playlists and map them to actual Spotify tracks:
- Playlist names with vibe keywords
- Playlist descriptions with emotional language
- Actual tracks in those playlists
- Track metadata (artists, popularity, etc.)

## 📋 Setup Instructions

### 1. Get Spotify API Credentials

You should already have these from the main web app setup, but if not:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Create a new app or use existing one
4. Copy your **Client ID** and **Client Secret**

### 2. Install Dependencies

```bash
cd spotify
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.env` file:
```bash
copy .env.example .env
```

Then edit `.env` and add your credentials:
```
SPOTIFY_CLIENT_ID=your_actual_client_id
SPOTIFY_CLIENT_SECRET=your_actual_client_secret
```

**Note:** You can use the same credentials from `code/web/.env.local`

### 4. Run the Scraper

```bash
python spotify_scraper.py
```

## 📊 What the Scraper Does

**Vibe Queries Used:**
- gym motivation
- study focus
- sad vibes
- confidence
- main character energy
- 3am thoughts
- driving at night
- workout beast mode
- chill vibes
- happy energy
- rainy day
- sunday morning
- party vibes
- aesthetic
- cozy feels
- summer vibes
- late night vibes
- feeling myself
- villain arc
- indie vibes

**For Each Query:**
1. Searches Spotify for playlists matching the vibe
2. Gets up to 15 playlists per query
3. Extracts playlist name and description
4. Gets up to 30 tracks per playlist
5. Records track metadata (name, artist, album, popularity)

**Rate Limiting:**
- 0.3s delay between playlists
- 0.5s delay between queries
- Automatically refreshes access token

## 📁 Output Files

- **`spotify_playlists_[timestamp].json`** - Full nested data with playlists and tracks
- **`spotify_playlists_training_[timestamp].csv`** - Training-friendly format

**Training CSV Format:**
Each row represents one track with its vibe context:
- vibe_query: The search query used
- playlist_name: Name of the playlist
- playlist_description: Curator's description
- track_name: Name of the song
- artists: Artist(s) who created the track
- album: Album name
- popularity: Spotify popularity score (0-100)
- track_url: Link to track on Spotify
- playlist_url: Link to playlist on Spotify

## 🎨 Example Data We're Collecting

**Vibe Query:** "main character energy"

**Playlist Found:** "Main Character Vibes - feel confident and unstoppable"

**Tracks:**
- "Confident" by Demi Lovato
- "Boss Bitch" by Doja Cat
- "good 4 u" by Olivia Rodrigo
- etc.

This creates training data that maps vibe descriptions to actual Spotify tracks!

## 🔄 Next Steps

After collecting Spotify data:
1. Combine with Reddit recommendation data (user vibe requests → song suggestions)
2. Combine with YouTube tracklist data (playlist vibes → actual songs)
3. Create comprehensive training dataset
4. Use for Claude fine-tuning / prompt engineering

## 💡 Why This Data is Valuable

- **Real Spotify tracks** with IDs we can use directly
- **Curated playlists** where someone already did the vibe → track mapping
- **Popularity scores** to help identify widely-loved vs deep-cut tracks
- **Multiple tracks per vibe** to capture variety within each vibe category

---

**Note:** This complements Reddit (user language) and YouTube (community descriptions) with official Spotify data.

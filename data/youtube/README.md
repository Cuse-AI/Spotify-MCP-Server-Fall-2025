# YouTube Comment Scraping

This folder contains YouTube comment scraping tools for collecting vibe descriptions from curated playlist videos.

## 🎯 Goal

Collect authentic vibe language from YouTube comments on music playlist videos, where people describe:
- How playlists make them feel
- Metaphors and POV statements ("POV: you're the main character")
- Aesthetic descriptions ("3am thoughts", "rainy day vibes")
- Emotional associations and cultural context

## 📋 Setup Instructions

### 1. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **YouTube Data API v3**:
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

### 2. Install Dependencies

```bash
cd youtube
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file:
```bash
copy .env.example .env
```

Then edit `.env` and add your API key:
```
YOUTUBE_API_KEY=your_actual_api_key_here
```

### 4. Run the Scraper

```bash
python youtube_scraper.py
```

## 📊 What the Scraper Does

**Search Queries Used:**
- "music playlist vibe"
- "aesthetic playlist"
- "mood playlist music"
- "songs that feel like"
- "playlist for when you"
- "deep cuts playlist"
- "hidden gems music"
- "vibes playlist"
- "3am playlist"
- "main character playlist"

**For Each Query:**
1. Finds top 5 relevant playlist videos
2. Scrapes up to 100 top comments per video
3. Filters for vibe-relevant comments only
4. Captures comment text, likes, author, timestamp

**Vibe-Relevant Comments Include:**
- Emotional descriptions ("this makes me feel...")
- Metaphors ("sounds like a rainy Sunday")
- POV statements ("POV: you're driving at night")
- Aesthetic associations ("3am thoughts energy")
- Mood descriptions ("sad but hopeful vibe")

## 📁 Output Files

- **`youtube_vibe_data_[timestamp].json`** - Full nested data
- **`youtube_vibe_data_summary_[timestamp].csv`** - Flattened for review

## ⚠️ API Quota Limits

YouTube Data API has a daily quota limit:
- **10,000 units per day** (free tier)
- Search request = 100 units
- Comment thread request = 1 unit

Our scraper uses approximately:
- 10 search queries × 100 units = 1,000 units
- ~50 videos × 1 unit = 50 units  
- **Total: ~1,050 units per run**

You can run the scraper about **9 times per day** before hitting quota limits.

## 🎨 Example Vibe Comments We're Looking For

- "This playlist hits different at 3am"
- "POV: you're the villain having a redemption arc"
- "Sounds like driving through the city alone at night"
- "This captures that feeling when you're happy but nostalgic"
- "Main character energy"
- "Feels like a coming-of-age movie soundtrack"

## 🔄 Next Steps

After collecting YouTube data:
1. Review unique vibe language not found in Reddit
2. Combine with Reddit + Spotify data sources
3. Extract training examples for Claude fine-tuning
4. Build the vibe understanding model!

---

**Note:** This complements the Reddit data source with different types of vibe descriptions.

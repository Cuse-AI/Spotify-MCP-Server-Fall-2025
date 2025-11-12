# Tapestry Data

This folder should contain the `tapestry_VALIDATED_ONLY.json` file with the complete emotional music database.

## Expected Format

```json
{
  "songs": [
    {
      "track_id": "spotify:track:...",
      "artist": "Artist Name",
      "title": "Song Title",
      "sub_vibe": "Specific emotional sub-category (one of 114)",
      "meta_vibe": "Higher-level emotional category",
      "reddit_context": "Human-sourced context from Reddit discussions",
      "ananki_reasoning": "Deep emotional analysis of why this song fits this vibe",
      "coordinates": {
        "x": 0.5,
        "y": 0.5
      }
    }
  ]
}
```

## Adding Your Data

1. Place `tapestry_VALIDATED_ONLY.json` in this directory
2. The server will automatically detect and load it
3. Claude will use this data with prompt caching for efficient playlist generation

## Current Status

⚠️ **No tapestry data loaded yet**

The application will use sample playlists until the real data is added.

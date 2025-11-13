# 🔐 API Keys Setup

## IMPORTANT: Never commit your actual API keys!

### Quick Setup:

1. **Copy the example files:**
   ```bash
   # Reddit
   cp data/reddit/.env.example data/reddit/.env
   
   # YouTube
   cp data/youtube/.env.example data/youtube/.env
   
   # Spotify
   cp data/spotify/.env.example data/spotify/.env
   ```

2. **Fill in your actual API keys** in the `.env` files (NOT the `.env.example` files)

3. **Verify .gitignore is working:**
   ```bash
   git status
   # Should NOT show any .env files (only .env.example)
   ```

### What's Safe to Push:
✅ `.env.example` files (have placeholder values)
✅ `.gitignore` (protects your real keys)
✅ All code and scripts

### What's Protected:
❌ `.env` files (have your real keys)
❌ Any file with actual credentials
❌ Large data files and test results

### Getting API Keys:

**Reddit:**
- Go to https://www.reddit.com/prefs/apps
- Create an app, get Client ID & Secret

**YouTube:**
- Go to https://console.cloud.google.com
- Enable YouTube Data API v3
- Create credentials

**Spotify:**
- Go to https://developer.spotify.com/dashboard
- Create an app, get Client ID & Secret

**Anthropic (Claude):**
- Go to https://console.anthropic.com
- Get your API key from settings

---

**The `.env` files are already in .gitignore - your keys are safe!** 🔒

# Tapestry Web App - Local Setup Guide

## 📦 What You Downloaded

This is the complete Tapestry web app that runs in the `code/web/` directory of your GitHub repository.

## 🚀 Quick Start

### 1. **Copy Files to Your Local Repo**

Extract the `code/web/` folder into your local clone of the `Spotify-MCP-Server-Fall-2025` repository:

```
Spotify-MCP-Server-Fall-2025/
├── code/
│   └── web/          ← All web app files go here
├── core/
│   └── tapestry.json ← Required: 6,081 songs database
└── data/
    └── emotional_manifold_COMPLETE.json ← Required: Emotional coordinates
```

**CRITICAL:** The app expects `core/tapestry.json` and `data/emotional_manifold_COMPLETE.json` to be **two directories up** from where you run the server.

### 2. **Install Dependencies**

```bash
cd code/web
npm install
```

### 3. **Set Up Environment Variables**

Create a `.env` file in the `code/web/` directory:

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

**Where to get these:**
- **Anthropic API Key**: https://console.anthropic.com/
- **Spotify Credentials**: https://developer.spotify.com/dashboard

### 4. **Run the App**

```bash
npm run dev
```

Open http://localhost:5000

## 📁 Required File Structure

The app expects this structure when running:

```
your-repo/
├── code/web/         ← Run server FROM HERE
├── core/
│   └── tapestry.json      ← 6,081 songs (REQUIRED)
└── data/
    └── emotional_manifold_COMPLETE.json  ← Emotional coordinates (REQUIRED)
```

**If your data files are elsewhere**, update the paths in `server/claude-service.ts`:

```typescript
const tapestryPath = path.join(process.cwd(), "../../core/tapestry.json");
const manifoldPath = path.join(process.cwd(), "../../data/emotional_manifold_COMPLETE.json");
```

## 🔧 Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Express + Node.js
- **AI**: Anthropic Claude (Sonnet 4.5) with prompt caching
- **Music**: Spotify API for artwork/previews
- **Database**: PostgreSQL (optional - defaults to in-memory)

## 📝 Available Scripts

```bash
npm run dev     # Start development server (port 5000)
npm run build   # Build for production
npm run start   # Run production build
```

## 🎨 Features

- Conversational 3-question emotional journey
- AI-curated playlists from 6,081 human-sourced songs
- Spotify integration for album art and 30s previews
- Thumbs up/down feedback system
- Dark ChatGPT-inspired interface
- Real-time Tapestry stats banner

## 🐛 Troubleshooting

### "Tapestry data files not found"
- Make sure you're running `npm run dev` from inside `code/web/`
- Verify `../../core/tapestry.json` exists from that location
- Verify `../../data/emotional_manifold_COMPLETE.json` exists

### "Missing API key" errors
- Check your `.env` file has all required keys
- Make sure `.env` is in the `code/web/` directory
- Restart the dev server after adding environment variables

### Port 5000 already in use
- Change `PORT=5000` to another port in `.env`
- Or kill the process using port 5000

## 📚 Documentation

Full project documentation is in `replit.md` at the root of your repository.

---

**Questions?** Check the GitHub repo or Replit project for the latest updates!

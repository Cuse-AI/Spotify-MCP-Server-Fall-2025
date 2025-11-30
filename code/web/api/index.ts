import type { VercelRequest, VercelResponse } from "@vercel/node";
import { storage } from "../server/storage.js";
import { createSpotifyPlaylist } from "../server/spotify-service.js";
import { userJourneySchema, userValidatedSongSchema } from "../shared/schema.js";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const createPlaylistSchema = z.object({
  playlistName: z.string(),
  playlistDescription: z.string(),
  trackUris: z.array(z.string()),
});

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const url = new URL(req.url || "", `http://${req.headers.host}`);
  const pathParts = url.pathname.split("/").filter(Boolean);
  const endpoint = pathParts[1] || "";

  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    switch (endpoint) {
      case "health":
        return handleHealth(req, res);
      case "debug":
        return handleDebug(req, res);
      case "generate-playlist":
        return handleGeneratePlaylist(req, res);
      case "tapestry-stats":
        return handleTapestryStats(req, res);
      case "validate-song":
        return handleValidateSong(req, res);
      case "downvote-song":
        return handleDownvoteSong(req, res);
      case "create-spotify-playlist":
        return handleCreateSpotifyPlaylist(req, res);
      default:
        return res.status(404).json({ message: `Unknown endpoint: /api/${endpoint}` });
    }
  } catch (error: any) {
    console.error("API Error:", error);
    return res.status(500).json({ message: error.message || "Internal server error" });
  }
}

// Debug endpoint to understand Vercel's file system
async function handleDebug(req: VercelRequest, res: VercelResponse) {
  const cwd = process.cwd();
  
  // List of paths to check
  const pathsToCheck = [
    { name: "cwd", path: cwd },
    { name: "__dirname", path: __dirname },
    { name: "cwd/core", path: path.join(cwd, "core") },
    { name: "cwd/data", path: path.join(cwd, "data") },
    { name: "__dirname/../core", path: path.join(__dirname, "..", "core") },
    { name: "__dirname/../data", path: path.join(__dirname, "..", "data") },
    { name: "/var/task", path: "/var/task" },
    { name: "/var/task/core", path: "/var/task/core" },
  ];

  const results: any = {
    cwd,
    __dirname,
    pathChecks: [],
    cwdContents: [],
    dirnameContents: [],
  };

  // Check each path
  for (const p of pathsToCheck) {
    const exists = fs.existsSync(p.path);
    let contents: string[] = [];
    if (exists) {
      try {
        const stat = fs.statSync(p.path);
        if (stat.isDirectory()) {
          contents = fs.readdirSync(p.path).slice(0, 20); // First 20 items
        }
      } catch (e) {}
    }
    results.pathChecks.push({ name: p.name, path: p.path, exists, contents });
  }

  // List cwd contents
  try {
    results.cwdContents = fs.readdirSync(cwd);
  } catch (e: any) {
    results.cwdContents = `Error: ${e.message}`;
  }

  // List __dirname parent contents
  try {
    results.dirnameParentContents = fs.readdirSync(path.join(__dirname, ".."));
  } catch (e: any) {
    results.dirnameParentContents = `Error: ${e.message}`;
  }

  return res.json(results);
}

async function handleHealth(req: VercelRequest, res: VercelResponse) {
  const hasAnthropicKey = !!process.env.ANTHROPIC_API_KEY;
  const hasSpotifyId = !!process.env.SPOTIFY_CLIENT_ID;
  const hasSpotifySecret = !!process.env.SPOTIFY_CLIENT_SECRET;

  let stats = null;
  let statsError = null;
  try {
    stats = await storage.getTapestryStats();
  } catch (e: any) {
    statsError = e.message;
  }

  const isHealthy = hasAnthropicKey && hasSpotifyId && hasSpotifySecret && stats !== null;

  return res.status(isHealthy ? 200 : 503).json({
    status: isHealthy ? "healthy" : "degraded",
    timestamp: new Date().toISOString(),
    environment: {
      anthropic_key: hasAnthropicKey ? "✅ set" : "❌ missing",
      spotify_id: hasSpotifyId ? "✅ set" : "❌ missing",
      spotify_secret: hasSpotifySecret ? "✅ set" : "❌ missing",
    },
    data: stats,
    statsError,
  });
}

async function handleGeneratePlaylist(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }
  try {
    const journey = userJourneySchema.parse(req.body);
    const playlist = await storage.generatePlaylist(journey);
    return res.json(playlist);
  } catch (error: any) {
    console.error("Error generating playlist:", error);
    return res.status(400).json({ message: error.message || "Failed to generate playlist" });
  }
}

async function handleTapestryStats(req: VercelRequest, res: VercelResponse) {
  try {
    const stats = await storage.getTapestryStats();
    return res.json(stats);
  } catch (error: any) {
    return res.status(500).json({ message: "Failed to fetch stats", details: error.message });
  }
}

async function handleValidateSong(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }
  try {
    const validatedData = userValidatedSongSchema.parse(req.body);
    const record = {
      song: validatedData.song,
      user_journey: validatedData.user_journey,
      validated_at: new Date().toISOString(),
      source: "user_validated" as const,
    };
    const result = await storage.saveValidatedSong(record);
    return res.json({ 
      success: true, 
      message: result?.boosted ? "Confidence boosted!" : "Song added to Tapestry!",
      boosted: result?.boosted || false
    });
  } catch (error: any) {
    return res.status(400).json({ message: "Failed to save upvote", details: error.message });
  }
}

async function handleDownvoteSong(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }
  try {
    const downvoteData = userValidatedSongSchema.parse(req.body);
    const record = {
      song: downvoteData.song,
      user_journey: downvoteData.user_journey,
      validated_at: new Date().toISOString(),
      source: "user_validated" as const,
    };
    await storage.saveDownvotedSong(record);
    return res.json({ success: true, message: "Feedback recorded!" });
  } catch (error: any) {
    return res.status(400).json({ message: "Failed to record downvote", details: error.message });
  }
}

async function handleCreateSpotifyPlaylist(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }
  try {
    const params = createPlaylistSchema.parse(req.body);
    const result = await createSpotifyPlaylist(params);
    return res.json(result);
  } catch (error: any) {
    return res.status(500).json({ message: "Failed to create Spotify playlist", details: error.message });
  }
}

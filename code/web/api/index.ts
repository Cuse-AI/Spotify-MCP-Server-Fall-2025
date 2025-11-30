import "dotenv/config";
import type { VercelRequest, VercelResponse } from "@vercel/node";
import { storage } from "../server/storage";
import { createSpotifyPlaylist } from "../server/spotify-service";
import { userJourneySchema, userValidatedSongSchema } from "../shared/schema";
import { z } from "zod";

const createPlaylistSchema = z.object({
  playlistName: z.string(),
  playlistDescription: z.string(),
  trackUris: z.array(z.string()),
});

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Parse the path from the URL
  const url = new URL(req.url || "", `http://${req.headers.host}`);
  const pathParts = url.pathname.split("/").filter(Boolean);
  const endpoint = pathParts[1] || ""; // e.g., "generate-playlist" from "/api/generate-playlist"

  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  try {
    // Route handling
    switch (endpoint) {
      case "health":
        return handleHealth(req, res);
      
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

async function handleHealth(req: VercelRequest, res: VercelResponse) {
  const hasAnthropicKey = !!process.env.ANTHROPIC_API_KEY;
  const hasSpotifyId = !!process.env.SPOTIFY_CLIENT_ID;
  const hasSpotifySecret = !!process.env.SPOTIFY_CLIENT_SECRET;

  let stats = null;
  try {
    stats = await storage.getTapestryStats();
  } catch (e) {
    console.error("Error getting stats:", e);
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
    return res.status(400).json({ 
      message: error.message || "Failed to generate playlist" 
    });
  }
}

async function handleTapestryStats(req: VercelRequest, res: VercelResponse) {
  try {
    const stats = await storage.getTapestryStats();
    return res.json(stats);
  } catch (error: any) {
    console.error("Error fetching stats:", error);
    return res.status(500).json({ 
      message: "Failed to fetch stats",
      details: error.message
    });
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
    console.error("Error validating song:", error);
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
    console.error("Error downvoting song:", error);
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
    console.error("Error creating Spotify playlist:", error);
    return res.status(500).json({ message: "Failed to create Spotify playlist", details: error.message });
  }
}

import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { userJourneySchema, userValidatedSongSchema } from "@shared/schema";
import { createSpotifyPlaylist } from "./spotify-service";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";

const createPlaylistSchema = z.object({
  playlistName: z.string(),
  playlistDescription: z.string(),
  trackUris: z.array(z.string()),
});

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Health Check API - validates all systems are ready
  app.get("/api/health", async (req, res) => {
    try {
      // Get project root (same logic as storage.ts)
      let projectRoot = process.cwd();
      const parentDir = path.join(projectRoot, "..", "..");
      if (fs.existsSync(path.join(parentDir, "core", "tapestry.json"))) {
        projectRoot = parentDir;
      }

      const tapestryPath = path.join(projectRoot, "core", "tapestry.json");
      const manifoldPath = path.join(projectRoot, "data", "emotional_manifold_COMPLETE.json");

      // Check file existence
      const tapestryExists = fs.existsSync(tapestryPath);
      const manifoldExists = fs.existsSync(manifoldPath);

      // Check API keys
      const hasAnthropicKey = !!process.env.ANTHROPIC_API_KEY;
      const hasSpotifyId = !!process.env.SPOTIFY_CLIENT_ID;
      const hasSpotifySecret = !!process.env.SPOTIFY_CLIENT_SECRET;

      // Get stats if files exist
      let stats = null;
      if (tapestryExists && manifoldExists) {
        try {
          stats = await storage.getTapestryStats();
        } catch (e) {
          console.error("Error getting stats:", e);
        }
      }

      const isHealthy = tapestryExists && manifoldExists && hasAnthropicKey && hasSpotifyId && hasSpotifySecret;

      res.status(isHealthy ? 200 : 503).json({
        status: isHealthy ? "healthy" : "degraded",
        timestamp: new Date().toISOString(),
        files: {
          tapestry: { exists: tapestryExists, path: tapestryPath },
          manifold: { exists: manifoldExists, path: manifoldPath },
        },
        environment: {
          anthropic_key: hasAnthropicKey ? "✅ set" : "❌ missing",
          spotify_id: hasSpotifyId ? "✅ set" : "❌ missing",
          spotify_secret: hasSpotifySecret ? "✅ set" : "❌ missing",
        },
        data: stats,
      });
    } catch (error: any) {
      console.error("Health check error:", error);
      res.status(500).json({
        status: "error",
        message: error.message || "Health check failed",
      });
    }
  });
  
  // Generate Playlist API
  app.post("/api/generate-playlist", async (req, res) => {
    try {
      const journey = userJourneySchema.parse(req.body);
      
      // Call the playlist generator (currently using placeholder)
      const playlist = await storage.generatePlaylist(journey);
      
      res.json(playlist);
    } catch (error: any) {
      console.error("Error generating playlist:", error);
      res.status(400).json({ 
        message: error.message || "Failed to generate playlist" 
      });
    }
  });

  // Validate Song API - saves upvoted songs directly to tapestry_complete.json
  app.post("/api/validate-song", async (req, res) => {
    try {
      const validatedData = userValidatedSongSchema.parse(req.body);
      
      // Create the record with timestamp
      const record = {
        song: validatedData.song,
        user_journey: validatedData.user_journey,
        validated_at: new Date().toISOString(),
        source: "user_validated" as const,
      };
      
      const result = await storage.saveValidatedSong(record);
      
      res.json({ 
        success: true, 
        message: result?.boosted ? "Confidence boosted!" : "Song added to Tapestry!",
        boosted: result?.boosted || false
      });
    } catch (error: any) {
      console.error("Error validating song:", error);
      
      if (error instanceof z.ZodError) {
        const issues = error.errors.map(e => `${e.path.join(".")}: ${e.message}`).join("; ");
        res.status(400).json({ 
          message: `Invalid song data: ${issues}`,
          details: "Song must have: track_id, title, artist, sub_vibe, confidence, etc."
        });
        return;
      }
      
      if (error.message.includes("Tapestry data file not found")) {
        res.status(503).json({ 
          message: "Cannot save upvote: Tapestry database not found",
          details: "Check /api/health for system status"
        });
        return;
      }
      
      res.status(400).json({ 
        message: "Failed to save upvote",
        details: error.message
      });
    }
  });

  // Downvote Song API - saves flagged songs to user_downvotes.json
  app.post("/api/downvote-song", async (req, res) => {
    try {
      const downvoteData = userValidatedSongSchema.parse(req.body);
      
      // Create the record with timestamp
      const record = {
        song: downvoteData.song,
        user_journey: downvoteData.user_journey,
        validated_at: new Date().toISOString(),
        source: "user_validated" as const,
      };
      
      await storage.saveDownvotedSong(record);
      
      res.json({ success: true, message: "Feedback recorded!" });
    } catch (error: any) {
      console.error("Error downvoting song:", error);
      
      if (error instanceof z.ZodError) {
        const issues = error.errors.map(e => `${e.path.join(".")}: ${e.message}`).join("; ");
        res.status(400).json({ 
          message: `Invalid song data: ${issues}`,
          details: "Required: track_id, title, artist, sub_vibe, meta_vibe"
        });
        return;
      }
      
      res.status(400).json({ 
        message: "Failed to record downvote",
        details: error.message
      });
    }
  });

  // Get Tapestry Stats API
  app.get("/api/tapestry-stats", async (req, res) => {
    try {
      const stats = await storage.getTapestryStats();
      res.json(stats);
    } catch (error: any) {
      console.error("Error fetching Tapestry stats:", error);
      
      if (error.message.includes("Tapestry data files not found")) {
        res.status(503).json({ 
          message: "Tapestry data unavailable",
          details: "Required files missing: core/tapestry.json or data/emotional_manifold_COMPLETE.json",
          check: "Run /api/health for diagnostic details"
        });
        return;
      }
      
      res.status(500).json({ 
        message: "Failed to fetch stats",
        details: error.message
      });
    }
  });

  // Create Spotify Playlist API
  app.post("/api/create-spotify-playlist", async (req, res) => {
    try {
      const params = createPlaylistSchema.parse(req.body);
      const result = await createSpotifyPlaylist(params);
      res.json(result);
    } catch (error: any) {
      console.error("Error creating Spotify playlist:", error);
      
      if (error instanceof z.ZodError) {
        const issues = error.errors.map(e => `${e.path.join(".")}: ${e.message}`).join("; ");
        res.status(400).json({ 
          message: `Invalid playlist data: ${issues}`,
          details: "Required: playlistName (string), playlistDescription (string), trackUris (array)"
        });
        return;
      }
      
      if (error.message.includes("401") || error.message.includes("Unauthorized")) {
        res.status(401).json({ 
          message: "Spotify authentication failed",
          details: "Your Spotify token may have expired. Please re-authenticate."
        });
        return;
      }
      
      if (error.message.includes("429") || error.message.includes("Too Many Requests")) {
        res.status(429).json({ 
          message: "Spotify rate limit exceeded",
          details: "Too many playlist creations. Please try again in a few moments."
        });
        return;
      }
      
      if (error.message.includes("Spotify")) {
        res.status(503).json({ 
          message: "Spotify API error: " + error.message,
          details: "Unable to create playlist on Spotify"
        });
        return;
      }
      
      res.status(500).json({ 
        message: "Failed to create Spotify playlist",
        details: error.message
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}

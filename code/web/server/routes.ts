import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { userJourneySchema, userValidatedSongSchema } from "@shared/schema";
import { createSpotifyPlaylist } from "./spotify-service";
import { z } from "zod";

const createPlaylistSchema = z.object({
  playlistName: z.string(),
  playlistDescription: z.string(),
  trackUris: z.array(z.string()),
});

export async function registerRoutes(app: Express): Promise<Server> {
  
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
      res.status(400).json({ 
        message: error.message || "Failed to validate song" 
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
      res.status(400).json({ 
        message: error.message || "Failed to record feedback" 
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
      res.status(500).json({ 
        message: error.message || "Failed to fetch stats" 
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
      res.status(500).json({ 
        message: error.message || "Failed to create playlist" 
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}

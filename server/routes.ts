import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { userJourneySchema, userValidatedSongSchema } from "@shared/schema";

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
      
      await storage.saveValidatedSong(record);
      
      res.json({ success: true, message: "Song added to Tapestry!" });
    } catch (error: any) {
      console.error("Error validating song:", error);
      res.status(400).json({ 
        message: error.message || "Failed to validate song" 
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}

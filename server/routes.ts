import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { userJourneySchema } from "@shared/schema";

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

  const httpServer = createServer(app);

  return httpServer;
}

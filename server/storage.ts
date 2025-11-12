import type { UserJourney, PlaylistResponse } from "@shared/schema";
import { generatePlaylistWithClaude } from "./claude-service";

export interface IStorage {
  generatePlaylist(journey: UserJourney): Promise<PlaylistResponse>;
}

export class MemStorage implements IStorage {
  
  async generatePlaylist(journey: UserJourney): Promise<PlaylistResponse> {
    // Use the real Claude API integration
    return await generatePlaylistWithClaude(journey);
  }
}

export const storage = new MemStorage();

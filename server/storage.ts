import type { UserJourney, PlaylistResponse, ValidatedSongRecord, TapestrySong } from "@shared/schema";
import { generatePlaylistWithClaude } from "./claude-service";
import * as fs from "fs";
import * as path from "path";

export interface IStorage {
  generatePlaylist(journey: UserJourney): Promise<PlaylistResponse>;
  saveValidatedSong(record: ValidatedSongRecord): Promise<void>;
}

export class MemStorage implements IStorage {
  
  async generatePlaylist(journey: UserJourney): Promise<PlaylistResponse> {
    // Use the real Claude API integration
    return await generatePlaylistWithClaude(journey);
  }

  async saveValidatedSong(record: ValidatedSongRecord): Promise<void> {
    const tapestryPath = path.join(process.cwd(), "data", "tapestry_complete.json");
    
    if (!fs.existsSync(tapestryPath)) {
      throw new Error("Tapestry data file not found");
    }

    // Read current tapestry
    const tapestry = JSON.parse(fs.readFileSync(tapestryPath, "utf-8"));
    
    // Get the sub-vibe for this song
    const subVibe = record.song.sub_vibe;
    
    // Create sub-vibe category if it doesn't exist
    if (!tapestry.vibes[subVibe]) {
      tapestry.vibes[subVibe] = { songs: [] };
    }
    
    // Create the song entry with user validation context
    const songEntry = {
      artist: record.song.artist,
      song: record.song.title,
      spotify_id: record.song.track_id.replace("spotify:track:", ""),
      spotify_uri: record.song.track_id,
      full_context: `User-validated song from journey: "${record.user_journey.vibe}" (${record.user_journey.now} → ${record.user_journey.going})`,
      ananki_analysis: record.song.ananki_reasoning || "User-validated as perfect fit for their emotional journey",
      mapped_subvibe: subVibe,
      mapping_confidence: record.song.confidence,
      source: "user_validated",
      validated_at: record.validated_at,
      manifold_x: record.song.manifold_x,
      manifold_y: record.song.manifold_y,
      emotional_composition: record.song.emotional_composition,
    };
    
    // Add to tapestry (avoid duplicates)
    const exists = tapestry.vibes[subVibe].songs.some(
      (s: any) => s.spotify_uri === songEntry.spotify_uri
    );
    
    if (!exists) {
      tapestry.vibes[subVibe].songs.push(songEntry);
      
      // Write back to file
      fs.writeFileSync(tapestryPath, JSON.stringify(tapestry, null, 2));
      console.log(`✅ Added validated song to Tapestry: ${record.song.artist} - ${record.song.title} (${subVibe})`);
    } else {
      console.log(`ℹ️  Song already exists in Tapestry: ${record.song.artist} - ${record.song.title}`);
    }
  }
}

export const storage = new MemStorage();

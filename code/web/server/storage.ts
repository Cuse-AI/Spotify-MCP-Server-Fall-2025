import type { UserJourney, PlaylistResponse, ValidatedSongRecord, TapestrySong, TapestryStats } from "@shared/schema";
import { generatePlaylistWithClaude } from "./claude-service";
import { enrichTracksWithSpotifyData } from "./spotify-service";
import * as fs from "fs";
import * as path from "path";

// Helper to find project root (works both locally in code/web and on Replit)
function getProjectRoot(): string {
  let currentDir = process.cwd();

  // Check if we're already at project root (has core/ and data/ folders)
  if (fs.existsSync(path.join(currentDir, "core", "tapestry.json"))) {
    return currentDir;
  }

  // Navigate up to find project root
  const parentDir = path.join(currentDir, "..", "..");
  if (fs.existsSync(path.join(parentDir, "core", "tapestry.json"))) {
    return parentDir;
  }

  // Fallback to current directory
  return currentDir;
}

const PROJECT_ROOT = getProjectRoot();

export interface IStorage {
  generatePlaylist(journey: UserJourney): Promise<PlaylistResponse>;
  saveValidatedSong(record: ValidatedSongRecord): Promise<{ boosted: boolean }>;
  saveDownvotedSong(record: ValidatedSongRecord): Promise<void>;
  getTapestryStats(): Promise<TapestryStats>;
}

export class MemStorage implements IStorage {
  
  async generatePlaylist(journey: UserJourney): Promise<PlaylistResponse> {
    // Get playlist from Claude
    const playlist = await generatePlaylistWithClaude(journey);
    
    // Enrich with Spotify metadata (album art, previews)
    const trackIds = playlist.songs.map(s => s.track_id);
    const spotifyMetadata = await enrichTracksWithSpotifyData(trackIds);
    
    // Add Spotify data to each song
    playlist.songs = playlist.songs.map(song => {
      const metadata = spotifyMetadata.get(song.track_id.replace("spotify:track:", ""));
      return {
        ...song,
        album_art: metadata?.album_art || undefined,
        preview_url: metadata?.preview_url || undefined,
        album_name: metadata?.album_name,
      };
    });
    
    return playlist;
  }

  async saveValidatedSong(record: ValidatedSongRecord): Promise<{ boosted: boolean }> {
    const tapestryPath = path.join(PROJECT_ROOT, "core", "tapestry.json");

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
    
    // Normalize IDs for comparison (handle both "spotify:track:XXX" and plain "XXX")
    const normalizeSpotifyId = (id: string) => id.replace("spotify:track:", "");
    const searchId = normalizeSpotifyId(record.song.track_id);
    
    // Check if song already exists in Tapestry
    const existingIndex = tapestry.vibes[subVibe]?.songs.findIndex(
      (s: any) => normalizeSpotifyId(s.spotify_uri || s.spotify_id || "") === searchId
    );
    
    if (existingIndex !== undefined && existingIndex >= 0) {
      // Song exists - boost confidence score
      const existingSong = tapestry.vibes[subVibe].songs[existingIndex];
      const confidenceBoost = 0.05; // 5% boost per validation
      const newConfidence = Math.min(0.99, existingSong.mapping_confidence + confidenceBoost);
      
      tapestry.vibes[subVibe].songs[existingIndex] = {
        ...existingSong,
        mapping_confidence: newConfidence,
        last_validated: record.validated_at,
        validation_count: (existingSong.validation_count || 0) + 1,
      };
      
      fs.writeFileSync(tapestryPath, JSON.stringify(tapestry, null, 2));
      console.log(`⬆️  Boosted confidence for "${record.song.artist} - ${record.song.title}": ${(existingSong.mapping_confidence * 100).toFixed(0)}% → ${(newConfidence * 100).toFixed(0)}%`);
      this.invalidateStatsCache();
      return { boosted: true };
    } else {
      // New extrapolated song - add to Tapestry
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
        validation_count: 1,
        manifold_x: record.song.manifold_x,
        manifold_y: record.song.manifold_y,
        emotional_composition: record.song.emotional_composition,
      };
      
      tapestry.vibes[subVibe].songs.push(songEntry);
      fs.writeFileSync(tapestryPath, JSON.stringify(tapestry, null, 2));
      console.log(`✅ Added validated song to Tapestry: ${record.song.artist} - ${record.song.title} (${subVibe})`);
      this.invalidateStatsCache();
      return { boosted: false };
    }
  }

  async saveDownvotedSong(record: ValidatedSongRecord): Promise<void> {
    const downvotesPath = path.join(PROJECT_ROOT, "data", "user_downvotes.json");
    
    // Create downvotes file if it doesn't exist
    let downvotes: any = { songs: [] };
    if (fs.existsSync(downvotesPath)) {
      downvotes = JSON.parse(fs.readFileSync(downvotesPath, "utf-8"));
    }

    // Create the downvote entry
    const downvoteEntry = {
      artist: record.song.artist,
      song: record.song.title,
      spotify_id: record.song.track_id.replace("spotify:track:", ""),
      spotify_uri: record.song.track_id,
      sub_vibe: record.song.sub_vibe,
      meta_vibe: record.song.meta_vibe,
      confidence: record.song.confidence,
      user_journey: {
        vibe: record.user_journey.vibe,
        now: record.user_journey.now,
        going: record.user_journey.going,
      },
      reason: "User flagged as poor match for their emotional journey",
      downvoted_at: record.validated_at,
      manifold_x: record.song.manifold_x,
      manifold_y: record.song.manifold_y,
      emotional_composition: record.song.emotional_composition,
      extrapolated: record.song.extrapolated,
    };

    // Check for duplicates
    const exists = downvotes.songs.some(
      (s: any) => s.spotify_uri === downvoteEntry.spotify_uri
    );

    if (!exists) {
      downvotes.songs.push(downvoteEntry);
      fs.writeFileSync(downvotesPath, JSON.stringify(downvotes, null, 2));
      console.log(`🚫 Downvoted song saved: ${record.song.artist} - ${record.song.title}`);
    } else {
      console.log(`ℹ️  Song already downvoted: ${record.song.artist} - ${record.song.title}`);
    }
  }

  private statsCache: { stats: TapestryStats; cachedAt: number } | null = null;
  private readonly STATS_TTL = 60 * 1000; // 60 seconds TTL

  async getTapestryStats(): Promise<TapestryStats> {
    // Check cache with TTL
    if (this.statsCache && (Date.now() - this.statsCache.cachedAt) < this.STATS_TTL) {
      return this.statsCache.stats;
    }

    const tapestryPath = path.join(PROJECT_ROOT, "core", "tapestry.json");
    const manifoldPath = path.join(PROJECT_ROOT, "data", "emotional_manifold_COMPLETE.json");

    if (!fs.existsSync(tapestryPath) || !fs.existsSync(manifoldPath)) {
      throw new Error("Tapestry data files not found");
    }

    const tapestry = JSON.parse(fs.readFileSync(tapestryPath, "utf-8"));
    const manifold = JSON.parse(fs.readFileSync(manifoldPath, "utf-8"));

    // Calculate track count
    const totalTracks = Object.values(tapestry.vibes).reduce(
      (sum: number, vibe: any) => sum + (vibe.songs?.length || 0),
      0
    );

    const stats: TapestryStats = {
      total_tracks: totalTracks,
      total_sub_vibes: manifold.metadata.total_sub_vibes,
      total_meta_vibes: manifold.metadata.total_central_vibes,
      human_sourced: true,
    };

    // Cache the stats
    this.statsCache = { stats, cachedAt: Date.now() };

    return stats;
  }

  invalidateStatsCache(): void {
    this.statsCache = null;
  }
}

export const storage = new MemStorage();

import { z } from "zod";

// User Journey - The three questions
export const userJourneySchema = z.object({
  vibe: z.string().min(1, "Please share your vibe"),
  now: z.string().min(1, "Please tell us where you are now"),
  going: z.string().min(1, "Please tell us where you're going"),
});

export type UserJourney = z.infer<typeof userJourneySchema>;

// Song from Tapestry
export interface TapestrySong {
  track_id: string;
  artist: string;
  title: string;
  sub_vibe: string;
  meta_vibe: string;
  confidence: number;
  reddit_context?: string;
  ananki_reasoning?: string;
  coordinates?: {
    x: number;
    y: number;
  };
  // Extrapolation fields (for Claude-suggested songs beyond Tapestry)
  extrapolated?: boolean;
  manifold_x?: number;
  manifold_y?: number;
  emotional_composition?: Record<string, number>;
  nearby_tapestry_songs?: string[];
}

// Playlist Response
export interface PlaylistResponse {
  journey: UserJourney;
  explanation: string;
  songs: TapestrySong[];
  emotionalArc: string;
}

// User-validated song (for upvoted songs that will be added to Tapestry)
export const userValidatedSongSchema = z.object({
  song: z.object({
    track_id: z.string(),
    artist: z.string(),
    title: z.string(),
    sub_vibe: z.string(),
    meta_vibe: z.string(),
    confidence: z.number(),
    manifold_x: z.number().optional(),
    manifold_y: z.number().optional(),
    emotional_composition: z.record(z.string(), z.number()).optional(),
    extrapolated: z.boolean().optional(),
  }),
  user_journey: userJourneySchema,
  validated_at: z.string().optional(), // ISO timestamp, will be set server-side
});

export type UserValidatedSong = z.infer<typeof userValidatedSongSchema>;

// For storing validated songs persistently
export interface ValidatedSongRecord {
  song: TapestrySong;
  user_journey: UserJourney;
  validated_at: string;
  source: "user_validated";
}

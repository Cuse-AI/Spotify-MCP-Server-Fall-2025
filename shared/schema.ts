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
}

// Playlist Response
export interface PlaylistResponse {
  journey: UserJourney;
  explanation: string;
  songs: TapestrySong[];
  emotionalArc: string;
}

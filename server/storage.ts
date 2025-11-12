import type { UserJourney, PlaylistResponse, TapestrySong } from "@shared/schema";

export interface IStorage {
  generatePlaylist(journey: UserJourney): Promise<PlaylistResponse>;
}

export class MemStorage implements IStorage {
  
  async generatePlaylist(journey: UserJourney): Promise<PlaylistResponse> {
    // PLACEHOLDER: This simulates what Claude would return
    // When ready to integrate Claude API, replace this function with real implementation
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create mock playlist based on the journey
    const mockSongs: TapestrySong[] = [
      {
        track_id: "spotify:track:example1",
        artist: "Bon Iver",
        title: "Holocene",
        sub_vibe: "Introspective - Contemplative",
        meta_vibe: "Introspective",
        confidence: 0.92,
        reddit_context: "Recommended in a thread about reflective morning music",
        ananki_reasoning: "This track captures the contemplative, introspective quality of the user's emotional starting point."
      },
      {
        track_id: "spotify:track:example2",
        artist: "Explosions in the Sky",
        title: "Your Hand in Mine",
        sub_vibe: "Hopeful - Building",
        meta_vibe: "Hopeful",
        confidence: 0.88,
        reddit_context: "User described as 'a journey from quiet contemplation to hopeful resolution'",
        ananki_reasoning: "Creates an emotional bridge, maintaining intimacy while introducing forward movement."
      },
      {
        track_id: "spotify:track:example3",
        artist: "Ólafur Arnalds",
        title: "Near Light",
        sub_vibe: "Peaceful - Morning",
        meta_vibe: "Peaceful",
        confidence: 0.85,
        ananki_reasoning: "Embodies the peaceful, uplifting destination the user is moving toward."
      }
    ];

    return {
      journey,
      explanation: `Based on your journey from "${journey.now}" to "${journey.going}", I've curated a playlist that walks the emotional tapestry. This collection uses real human-sourced recommendations—not algorithm guessing—to create an authentic emotional arc.`,
      emotionalArc: `Starting with introspective, contemplative vibes and gradually building toward peaceful, uplifting resolution.`,
      songs: mockSongs
    };
  }
}

export const storage = new MemStorage();

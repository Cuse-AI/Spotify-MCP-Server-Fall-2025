import Anthropic from "@anthropic-ai/sdk";
import type { UserJourney, PlaylistResponse, TapestrySong } from "@shared/schema";
import * as fs from "fs";
import * as path from "path";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

interface TapestryData {
  songs: Array<{
    track_id: string;
    artist: string;
    title: string;
    sub_vibe: string;
    meta_vibe: string;
    reddit_context?: string;
    ananki_reasoning?: string;
    coordinates?: {
      x: number;
      y: number;
    };
  }>;
}

let tapestryCache: TapestryData | null = null;

function loadTapestryData(): TapestryData | null {
  if (tapestryCache) {
    return tapestryCache;
  }

  // Try multiple potential locations for the tapestry data
  const possiblePaths = [
    path.join(process.cwd(), "data", "tapestry_VALIDATED_ONLY.json"),
    path.join(process.cwd(), "tapestry_VALIDATED_ONLY.json"),
    path.join(process.cwd(), "..", "data", "tapestry_VALIDATED_ONLY.json"),
    path.join(process.cwd(), "server", "data", "tapestry_VALIDATED_ONLY.json"),
  ];

  for (const filePath of possiblePaths) {
    if (fs.existsSync(filePath)) {
      console.log(`✅ Found tapestry data at: ${filePath}`);
      const rawData = fs.readFileSync(filePath, "utf-8");
      tapestryCache = JSON.parse(rawData);
      return tapestryCache;
    }
  }

  // If no file found, return null
  console.warn(
    "⚠️  Tapestry data file not found. Using sample playlist. Please add tapestry_VALIDATED_ONLY.json to the project."
  );
  return null;
}

export async function generatePlaylistWithClaude(
  journey: UserJourney
): Promise<PlaylistResponse> {
  const tapestryData = loadTapestryData();

  if (!tapestryData || tapestryData.songs.length === 0) {
    // Return a helpful message if no data is available
    console.warn("⚠️  No tapestry data available, returning sample playlist");
    return generateSamplePlaylist(journey);
  }

  // Prepare the tapestry database for Claude
  const tapestryJson = JSON.stringify(tapestryData, null, 2);

  // Build the system prompt
  const systemPrompt = `You are an expert emotional music curator that specializes in creating personalized playlists by "walking the Tapestry manifold."

The Tapestry is a database of ${tapestryData.songs.length} songs that have been mapped to 114 emotional sub-vibes using human-sourced recommendations from Reddit discussions, NOT algorithmic keyword matching or Spotify's valence metrics. Each song includes:
- Ananki reasoning: Deep analysis of the emotional qualities
- Reddit context: Real human discussions about when/why this song resonates
- Meta-vibe and sub-vibe classifications for precise emotional mapping

Your task is to create an emotional journey through music that takes the user from their current emotional state to their desired destination.`;

  try {
    // Call Claude API with prompt caching for the tapestry data
    const response = await client.messages.create({
      model: "claude-3-5-sonnet-20241022",
      max_tokens: 4096,
      system: [
        {
          type: "text",
          text: systemPrompt,
        },
        {
          type: "text",
          text: `<tapestry_database>\n${tapestryJson}\n</tapestry_database>`,
          cache_control: { type: "ephemeral" }, // Cache the entire tapestry!
        },
      ],
      messages: [
        {
          role: "user",
          content: `Based on the user's emotional journey, select 8-12 songs from the Tapestry database that create a cohesive emotional arc:

**User's Vibe**: ${journey.vibe}
**Current Emotional State (Now)**: ${journey.now}
**Desired Destination (Going)**: ${journey.going}

Please analyze this journey and:
1. Identify the emotional starting point and destination
2. Map the journey through appropriate sub-vibes in the Tapestry
3. Select songs that create a smooth progression from "now" to "going"
4. Prioritize songs with strong Reddit context and Ananki reasoning that match the emotional beats

Return your response as a JSON object with this exact structure:
{
  "explanation": "A 2-3 sentence explanation of the emotional arc you've created",
  "emotionalArc": "A brief description of the progression (e.g., 'Starting with introspective melancholy, building through hopeful contemplation, arriving at peaceful resolution')",
  "songs": [
    {
      "track_id": "spotify:track:...",
      "artist": "Artist Name",
      "title": "Song Title",
      "sub_vibe": "Sub-Vibe Category",
      "meta_vibe": "Meta-Vibe",
      "confidence": 0.95,
      "reddit_context": "Context from database",
      "ananki_reasoning": "Reasoning from database"
    }
  ]
}

Only include songs that exist in the provided Tapestry database. Return ONLY the JSON object, no additional text.`,
        },
      ],
    });

    // Parse Claude's response
    const firstContent = response.content[0];
    if (firstContent.type !== "text") {
      throw new Error("Unexpected response type from Claude");
    }
    const responseText = firstContent.text;
    
    // Extract JSON from the response (Claude sometimes wraps it in markdown)
    let jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("Could not extract JSON from Claude's response");
    }
    
    const claudeResponse = JSON.parse(jsonMatch[0]);

    // Log cache usage for debugging
    if (response.usage) {
      console.log("📊 Claude API Usage:", {
        input_tokens: response.usage.input_tokens,
        cache_creation_input_tokens: response.usage.cache_creation_input_tokens,
        cache_read_input_tokens: response.usage.cache_read_input_tokens,
        output_tokens: response.usage.output_tokens,
      });
    }

    return {
      journey,
      explanation: claudeResponse.explanation,
      emotionalArc: claudeResponse.emotionalArc,
      songs: claudeResponse.songs,
    };
  } catch (error: any) {
    console.error("❌ Claude API Error:", error);
    
    // Fallback to sample playlist if API fails
    console.warn("⚠️  Falling back to sample playlist due to API error");
    return generateSamplePlaylist(journey);
  }
}

// Fallback function for when Claude API is unavailable or tapestry data is missing
function generateSamplePlaylist(journey: UserJourney): PlaylistResponse {
  const sampleSongs: TapestrySong[] = [
    {
      track_id: "spotify:track:sample1",
      artist: "Bon Iver",
      title: "Holocene",
      sub_vibe: "Introspective - Contemplative",
      meta_vibe: "Introspective",
      confidence: 0.92,
      reddit_context: "Recommended in a thread about reflective morning music",
      ananki_reasoning:
        "This track captures the contemplative, introspective quality of the user's emotional starting point.",
    },
    {
      track_id: "spotify:track:sample2",
      artist: "Explosions in the Sky",
      title: "Your Hand in Mine",
      sub_vibe: "Hopeful - Building",
      meta_vibe: "Hopeful",
      confidence: 0.88,
      reddit_context:
        "User described as 'a journey from quiet contemplation to hopeful resolution'",
      ananki_reasoning:
        "Creates an emotional bridge, maintaining intimacy while introducing forward movement.",
    },
    {
      track_id: "spotify:track:sample3",
      artist: "Ólafur Arnalds",
      title: "Near Light",
      sub_vibe: "Peaceful - Morning",
      meta_vibe: "Peaceful",
      confidence: 0.85,
      ananki_reasoning:
        "Embodies the peaceful, uplifting destination the user is moving toward.",
    },
  ];

  return {
    journey,
    explanation: `Based on your journey from "${journey.now}" to "${journey.going}", I've curated a sample playlist. Note: This is a placeholder until the full Tapestry database is loaded.`,
    emotionalArc: `Starting with introspective, contemplative vibes and gradually building toward peaceful, uplifting resolution.`,
    songs: sampleSongs,
  };
}

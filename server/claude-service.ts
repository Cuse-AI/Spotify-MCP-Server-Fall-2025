import Anthropic from "@anthropic-ai/sdk";
import type { UserJourney, PlaylistResponse, TapestrySong } from "@shared/schema";
import * as fs from "fs";
import * as path from "path";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

interface TapestryComplete {
  vibes: {
    [subVibe: string]: {
      songs: Array<{
        artist: string;
        song: string;
        spotify_id: string;
        spotify_uri: string;
        full_context: string;
        ananki_analysis: string;
        mapped_subvibe: string;
        mapping_confidence: number;
      }>;
    };
  };
}

interface EmotionalManifold {
  metadata: {
    total_sub_vibes: number;
    total_central_vibes: number;
  };
  central_vibes: {
    positions: {
      [vibe: string]: { x: number; y: number };
    };
  };
  sub_vibes: {
    [subVibe: string]: {
      emotional_composition: { [vibe: string]: number };
      coordinates: { x: number; y: number };
      analysis: string;
      proximity_notes: string;
    };
  };
}

let tapestryCache: TapestryComplete | null = null;
let manifoldCache: EmotionalManifold | null = null;

function loadTapestryData(): { tapestry: TapestryComplete; manifold: EmotionalManifold } | null {
  if (tapestryCache && manifoldCache) {
    return { tapestry: tapestryCache, manifold: manifoldCache };
  }

  try {
    const tapestryPath = path.join(process.cwd(), "core", "tapestry.json");
    const manifoldPath = path.join(process.cwd(), "data", "emotional_manifold_COMPLETE.json");

    if (!fs.existsSync(tapestryPath) || !fs.existsSync(manifoldPath)) {
      console.warn("⚠️  Tapestry data files not found");
      return null;
    }

    console.log("✅ Loading Tapestry manifold...");
    tapestryCache = JSON.parse(fs.readFileSync(tapestryPath, "utf-8"));
    manifoldCache = JSON.parse(fs.readFileSync(manifoldPath, "utf-8"));
    
    console.log(`✅ Loaded ${manifoldCache.metadata.total_sub_vibes} sub-vibes across ${manifoldCache.metadata.total_central_vibes} central emotional centers`);
    return { tapestry: tapestryCache, manifold: manifoldCache };
  } catch (error) {
    console.error("❌ Error loading Tapestry data:", error);
    return null;
  }
}

async function identifyRelevantSubVibes(
  journey: UserJourney,
  manifold: EmotionalManifold
): Promise<string[]> {
  // Quick first pass: Ask Claude which sub-vibes are relevant
  // This is MUCH faster than sending all songs
  const subVibesList = Object.keys(manifold.sub_vibes).map(sv => ({
    name: sv,
    coords: manifold.sub_vibes[sv].coordinates,
    composition: manifold.sub_vibes[sv].emotional_composition,
    analysis: manifold.sub_vibes[sv].analysis
  }));

  const response = await client.messages.create({
    model: "claude-sonnet-4-5",
    max_tokens: 1000,
    messages: [{
      role: "user",
      content: `Given this emotional journey:
- Vibe: "${journey.vibe}"
- Current state: "${journey.now}"
- Desired destination: "${journey.going}"

And these ${subVibesList.length} sub-vibes with their coordinates and compositions:
${JSON.stringify(subVibesList, null, 2)}

Identify 15-25 sub-vibes that are most relevant for creating a playlist journey from "${journey.now}" to "${journey.going}".

Consider:
1. Sub-vibes that match the starting emotional state
2. Sub-vibes that match the destination
3. Sub-vibes that form a good path between them
4. The overall vibe "${journey.vibe}"

Return ONLY a JSON array of sub-vibe names, nothing else:
["sub-vibe-1", "sub-vibe-2", ...]`
    }]
  });

  const content = response.content[0];
  if (content.type === 'text') {
    const text = content.text.trim();
    // Extract JSON array from response
    const match = text.match(/\[[\s\S]*\]/);
    if (match) {
      return JSON.parse(match[0]);
    }
  }

  // Fallback: return all sub-vibes if parsing fails
  console.warn("⚠️  Failed to parse relevant sub-vibes, using all");
  return Object.keys(manifold.sub_vibes);
}

export async function generatePlaylistWithClaude(
  journey: UserJourney
): Promise<PlaylistResponse> {
  const data = loadTapestryData();

  if (!data) {
    console.warn("⚠️  No tapestry data available, returning sample playlist");
    return generateSamplePlaylist(journey);
  }

  const { tapestry, manifold } = data;

  // STEP 1: First pass - Ask Claude to identify relevant sub-vibes for the journey
  console.log("🎯 Step 1: Identifying relevant sub-vibes for the journey...");

  const relevantSubVibes = await identifyRelevantSubVibes(journey, manifold);
  console.log(`✅ Found ${relevantSubVibes.length} relevant sub-vibes:`, relevantSubVibes.slice(0, 5).join(', '), '...');

  // STEP 2: Load ALL songs ONLY from relevant sub-vibes
  const relevantSongs: Record<string, any[]> = {};
  let totalSongs = 0;

  for (const subVibe of relevantSubVibes) {
    if (tapestry.vibes[subVibe]) {
      const songs = tapestry.vibes[subVibe].songs
        .sort((a, b) => b.mapping_confidence - a.mapping_confidence)
        .map(song => ({
          artist: song.artist,
          title: song.song,
          spotify_uri: song.spotify_uri,
          sub_vibe: subVibe,
          ananki_reasoning: song.ananki_analysis
        }));
      relevantSongs[subVibe] = songs;
      totalSongs += songs.length;
    }
  }

  console.log(`📚 Loaded ${totalSongs} songs from ${relevantSubVibes.length} relevant sub-vibes (out of 6,081 total)`);

  // Filter out any sub-vibes that don't exist in the manifold (Claude might hallucinate names)
  const validSubVibes = relevantSubVibes.filter(subVibe => {
    if (!manifold.sub_vibes[subVibe]) {
      console.warn(`⚠️  Sub-vibe "${subVibe}" returned by Claude but not found in manifold`);
      return false;
    }
    return true;
  });

  console.log(`✅ Validated ${validSubVibes.length} sub-vibes exist in manifold`);

  // Prepare manifest with ONLY relevant data
  const manifestSummary = {
    manifold: {
      central_vibes: manifold.central_vibes.positions,
      sub_vibes: validSubVibes.map(subVibe => ({
        name: subVibe,
        coordinates: manifold.sub_vibes[subVibe].coordinates,
        emotional_composition: manifold.sub_vibes[subVibe].emotional_composition,
        analysis: manifold.sub_vibes[subVibe].analysis,
        song_count: tapestry.vibes[subVibe]?.songs.length || 0
      }))
    },
    available_songs: relevantSongs
  };

  const manifestJson = JSON.stringify(manifestSummary, null, 2);

  // Build the system prompt
  const systemPrompt = `You are an expert emotional playlist curator that specializes in creating personalized playlists by "walking the Tapestry manifold."

The Tapestry is a 2D emotional manifold mapping ${manifold.metadata.total_sub_vibes} emotional sub-vibes across ${manifold.metadata.total_central_vibes} central emotional centers (${Object.keys(manifold.central_vibes.positions).join(', ')}).

Each sub-vibe has x,y coordinates and is a weighted composition of central vibes. Songs are mapped using TRUE Ananki - AI analysis of human-sourced Reddit discussions, NOT keyword matching.

**EXTRAPOLATION MODE**: You may extrapolate beyond the provided Tapestry songs by using your music knowledge to suggest songs that fit the manifold math. Requirements for extrapolated songs:
1. You MUST calculate and provide exact x,y coordinates on the manifold
2. You MUST specify the emotional composition (% of each central vibe)
3. You MUST name 2-3 nearby Tapestry songs from the manifest to anchor the extrapolation
4. You MUST explain the manifold reasoning (not just genre/keywords)
5. Mark with "extrapolated": true

Aim for 60-70% Tapestry songs + 30-40% extrapolated songs to balance human-sourced data with expanded discovery.

Your task: Create an emotional journey by walking the manifold from the user's current state to their desired destination.`;

  try {
    console.log("🎵 Calling Claude to walk the Tapestry manifold...");
    
    const response = await client.messages.create({
      model: "claude-sonnet-4-5",
      max_tokens: 4096,
      system: [
        {
          type: "text",
          text: systemPrompt,
        },
        {
          type: "text",
          text: `<tapestry_manifest>\n${manifestJson}\n</tapestry_manifest>`,
          cache_control: { type: "ephemeral" }, // Cache the tapestry manifest!
        },
      ],
      messages: [
        {
          role: "user",
          content: `Create an emotional playlist journey based on the user's responses:

**Vibe**: ${journey.vibe}
**Current State (Now)**: ${journey.now}
**Desired Destination (Going)**: ${journey.going}

Instructions:
1. Analyze the emotional arc: identify starting sub-vibe(s) near "${journey.now}" and destination sub-vibe(s) near "${journey.going}"
2. Use the 2D coordinates and emotional compositions to plot a path through the manifold
3. Select 10-12 songs total: ~60-70% from Tapestry manifest, ~30-40% extrapolated from your music knowledge
4. For Tapestry songs: Use those with strong Ananki reasoning that match the path
5. For extrapolated songs: Calculate manifold position, specify emotional composition, and name nearby Tapestry songs
6. Consider the overall vibe "${journey.vibe}" as the journey's emotional character
7. Create a smooth progression - don't just dump extrapolated songs at the end

Return ONLY a JSON object (no markdown, no extra text):
{
  "explanation": "2-3 sentences explaining the emotional journey you created",
  "emotionalArc": "Brief narrative description of the progression through sub-vibes. IMPORTANT: Do NOT include any numeric coordinates or manifold positions in this text - keep it purely descriptive and narrative.",
  "songs": [
    {
      "track_id": "spotify:track:...",
      "artist": "Artist Name",
      "title": "Song Title",
      "sub_vibe": "Sub-Vibe Name",
      "meta_vibe": "Central Vibe",
      "confidence": 0.95,
      "reddit_context": "Brief context from Reddit or user validation",
      "ananki_reasoning": "Why this song fits this moment in the journey",
      "extrapolated": false,
      "manifold_x": 0.23,
      "manifold_y": -0.45,
      "emotional_composition": {"Chill": 60, "Sad": 25, "Night": 15},
      "nearby_tapestry_songs": ["Artist - Song", "Artist - Song"]
    }
  ]
}

Notes:
- For Tapestry songs: extrapolated=false, you can omit manifold coordinates and nearby songs
- For extrapolated songs: extrapolated=true, MUST include manifold_x, manifold_y, emotional_composition, nearby_tapestry_songs
- Intersperse extrapolated songs throughout the journey, not just at beginning/end`,
        },
      ],
    });

    // Parse Claude's response
    const firstContent = response.content[0];
    if (firstContent.type !== "text") {
      throw new Error("Unexpected response type from Claude");
    }
    const responseText = firstContent.text;
    
    // Extract JSON from the response
    let jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      console.error("❌ Could not extract JSON from Claude's response");
      console.log("Response:", responseText.slice(0, 500));
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
      
      const cacheHitRate = response.usage.cache_read_input_tokens 
        ? (response.usage.cache_read_input_tokens / (response.usage.input_tokens + response.usage.cache_read_input_tokens) * 100).toFixed(1)
        : "0";
      console.log(`💾 Cache hit rate: ${cacheHitRate}%`);
    }

    return {
      journey,
      explanation: claudeResponse.explanation,
      emotionalArc: claudeResponse.emotionalArc,
      songs: claudeResponse.songs,
    };
  } catch (error: any) {
    console.error("❌ Claude API Error:", error);
    console.warn("⚠️  Falling back to sample playlist due to API error");
    return generateSamplePlaylist(journey);
  }
}

// Fallback function for when Claude API is unavailable
function generateSamplePlaylist(journey: UserJourney): PlaylistResponse {
  const sampleSongs: TapestrySong[] = [
    {
      track_id: "spotify:track:31CYUJj5f9lbQ0Qqm9PzK5",
      artist: "Julee Cruise",
      title: "Falling",
      sub_vibe: "Night - Contemplative",
      meta_vibe: "Night",
      confidence: 0.92,
      reddit_context: "Recommended for late-night walks after a tough day",
      ananki_reasoning:
        "This track captures the contemplative, floating quality of nighttime introspection",
    },
    {
      track_id: "spotify:track:6MWnAibO1HAEhlrHoH1kNi",
      artist: "Cocteau Twins",
      title: "Lazy Calm",
      sub_vibe: "Chill - Lofi",
      meta_vibe: "Chill",
      confidence: 0.88,
      reddit_context: "Creates dreamy, hazy ambient thought space",
      ananki_reasoning:
        "Provides an emotional bridge through ambient calm, maintaining reflective mood",
    },
    {
      track_id: "spotify:track:5KX2DSPC6aCA0pdDidTmBC",
      artist: "Portishead",
      title: "The Rip",
      sub_vibe: "Sad - Melancholic",
      meta_vibe: "Sad",
      confidence: 0.90,
      reddit_context: "Deep, moody reflection without being overwhelming",
      ananki_reasoning: "Embodies gentle melancholy suitable for contemplative moments",
    },
  ];

  return {
    journey,
    explanation: `Based on your journey from "${journey.now}" to "${journey.going}", I've created a sample playlist. Note: This is using sample data - add your full Tapestry database to data/tapestry_complete.json for AI-powered emotional journeys!`,
    emotionalArc: `Gentle progression through contemplative night vibes, ambient calm, and melancholic reflection.`,
    songs: sampleSongs,
  };
}

import { SpotifyApi } from "@spotify/web-api-ts-sdk";

// Cache for access token
let cachedToken: { token: string; expiresAt: number } | null = null;

async function getClientCredentialsToken(): Promise<string> {
  // Check if we have a valid cached token
  if (cachedToken && cachedToken.expiresAt > Date.now()) {
    return cachedToken.token;
  }

  const clientId = process.env.SPOTIFY_CLIENT_ID;
  const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error('Spotify credentials not configured');
  }

  // Request access token using Client Credentials flow
  const response = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': 'Basic ' + Buffer.from(clientId + ':' + clientSecret).toString('base64'),
    },
    body: 'grant_type=client_credentials',
  });

  if (!response.ok) {
    throw new Error(`Spotify authentication failed: ${response.statusText}`);
  }

  const data = await response.json();
  
  // Cache the token (expires in 1 hour, cache for 50 minutes to be safe)
  cachedToken = {
    token: data.access_token,
    expiresAt: Date.now() + (50 * 60 * 1000),
  };

  return data.access_token;
}

async function getSpotifyClient() {
  const accessToken = await getClientCredentialsToken();
  const clientId = process.env.SPOTIFY_CLIENT_ID!;

  const spotify = SpotifyApi.withAccessToken(clientId, {
    access_token: accessToken,
    token_type: "Bearer",
    expires_in: 3600,
    refresh_token: "",
  });

  return spotify;
}

export interface SpotifyTrackMetadata {
  album_art: string | null;
  preview_url: string | null;
  album_name?: string;
}

export async function enrichTracksWithSpotifyData(trackIds: string[]): Promise<Map<string, SpotifyTrackMetadata>> {
  const metadata = new Map<string, SpotifyTrackMetadata>();
  
  if (trackIds.length === 0) {
    return metadata;
  }
  
  try {
    const spotify = await getSpotifyClient();
    
    // Spotify API allows fetching up to 50 tracks at once
    const batchSize = 50;
    const batches: string[][] = [];
    
    for (let i = 0; i < trackIds.length; i += batchSize) {
      batches.push(trackIds.slice(i, i + batchSize));
    }
    
    for (const batch of batches) {
      const normalizedIds = batch.map(id => id.replace("spotify:track:", ""));
      const tracks = await spotify.tracks.get(normalizedIds);
      
      for (const track of tracks) {
        if (track) {
          const albumArt = track.album.images[0]?.url || null;
          metadata.set(track.id, {
            album_art: albumArt,
            preview_url: track.preview_url,
            album_name: track.album.name,
          });
        }
      }
    }
    
    console.log(`✅ Enriched ${metadata.size} tracks with Spotify metadata`);
  } catch (error) {
    console.error("Error fetching Spotify metadata:", error);
  }
  
  return metadata;
}

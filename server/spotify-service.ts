import { SpotifyApi } from "@spotify/web-api-ts-sdk";

let connectionSettings: any;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    // Return cached token if still valid
    const refreshToken = connectionSettings.settings.oauth.credentials.refresh_token;
    const accessToken = connectionSettings.settings.oauth.credentials.access_token;
    const clientId = connectionSettings.settings.oauth.credentials.client_id;
    const expiresIn = connectionSettings.settings.oauth.credentials.expires_in;
    return {accessToken, clientId, refreshToken, expiresIn};
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found for repl/depl');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=spotify',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);
  
  // IMPORTANT: Use oauth.credentials.access_token (the short-lived token)
  // NOT the top-level access_token (which is actually the refresh token)
  const refreshToken = connectionSettings?.settings?.oauth?.credentials?.refresh_token;
  const accessToken = connectionSettings?.settings?.oauth?.credentials?.access_token;
  const clientId = connectionSettings?.settings?.oauth?.credentials?.client_id;
  const expiresIn = connectionSettings?.settings?.oauth?.credentials?.expires_in;
  
  if (!connectionSettings || (!accessToken || !clientId || !refreshToken)) {
    throw new Error('Spotify not connected');
  }
  
  return {accessToken, clientId, refreshToken, expiresIn};
}

// WARNING: Never cache this client.
// Access tokens expire, so a new client must be created each time.
// Always call this function again to get a fresh client.
async function getUncachableSpotifyClient() {
  const {accessToken, clientId, refreshToken, expiresIn} = await getAccessToken();

  const spotify = SpotifyApi.withAccessToken(clientId, {
    access_token: accessToken,
    token_type: "Bearer",
    expires_in: expiresIn || 3600,
    refresh_token: refreshToken,
  });

  return spotify;
}

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

async function fetchWithRetry(fn: () => Promise<any>, retries = 3, delay = 1000): Promise<any> {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error: any) {
      const isRateLimit = error?.status === 429 || error?.message?.includes('rate limit');
      const isLastAttempt = i === retries - 1;
      
      if (isLastAttempt) {
        throw error;
      }
      
      if (isRateLimit) {
        // For rate limits, wait longer (exponential backoff)
        const waitTime = delay * Math.pow(2, i);
        console.log(`⏳ Rate limited, waiting ${waitTime}ms before retry ${i + 1}/${retries}`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      } else {
        // For other errors, shorter wait
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
}

export async function enrichTracksWithSpotifyData(trackIds: string[]): Promise<Map<string, SpotifyTrackMetadata>> {
  const metadata = new Map<string, SpotifyTrackMetadata>();
  
  if (trackIds.length === 0) {
    return metadata;
  }
  
  try {
    const spotify = await getSpotifyClient();
    
    // Use smaller batch size to reduce rate limit issues (20 instead of 50)
    const batchSize = 20;
    const batches: string[][] = [];
    
    for (let i = 0; i < trackIds.length; i += batchSize) {
      batches.push(trackIds.slice(i, i + batchSize));
    }
    
    for (const batch of batches) {
      try {
        const normalizedIds = batch.map(id => id.replace("spotify:track:", ""));
        
        // Fetch with retry logic
        const tracks = await fetchWithRetry(() => spotify.tracks.get(normalizedIds));
        
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
        
        // Small delay between batches to avoid rate limits
        if (batches.length > 1) {
          await new Promise(resolve => setTimeout(resolve, 200));
        }
      } catch (error) {
        console.error(`Error fetching batch of ${batch.length} tracks:`, error);
        // Continue with other batches even if one fails
      }
    }
    
    console.log(`✅ Enriched ${metadata.size}/${trackIds.length} tracks with Spotify metadata`);
  } catch (error) {
    console.error("Error fetching Spotify metadata:", error);
  }
  
  return metadata;
}

export interface CreatePlaylistParams {
  playlistName: string;
  playlistDescription: string;
  trackUris: string[]; // Spotify URIs like "spotify:track:xxxxx"
}

export async function createSpotifyPlaylist(params: CreatePlaylistParams): Promise<{ playlistId: string; playlistUrl: string }> {
  try {
    const spotify = await getUncachableSpotifyClient();
    
    // Get current user profile
    const user = await spotify.currentUser.profile();
    
    // Create playlist
    const playlist = await spotify.playlists.createPlaylist(user.id, {
      name: params.playlistName,
      description: params.playlistDescription,
      public: false, // Private by default
    });
    
    // Add tracks to playlist (Spotify allows up to 100 tracks per request)
    if (params.trackUris.length > 0) {
      // Normalize URIs to ensure they have the spotify:track: prefix
      const normalizedUris = params.trackUris.map(uri => 
        uri.startsWith('spotify:track:') ? uri : `spotify:track:${uri}`
      );
      
      // Split into batches of 100
      const batchSize = 100;
      for (let i = 0; i < normalizedUris.length; i += batchSize) {
        const batch = normalizedUris.slice(i, i + batchSize);
        await spotify.playlists.addItemsToPlaylist(playlist.id, batch);
      }
    }
    
    console.log(`✅ Created Spotify playlist "${params.playlistName}" with ${params.trackUris.length} tracks`);
    
    return {
      playlistId: playlist.id,
      playlistUrl: playlist.external_urls.spotify,
    };
  } catch (error: any) {
    console.error('Error creating Spotify playlist:', error);
    throw new Error(`Failed to create playlist: ${error.message || 'Unknown error'}`);
  }
}

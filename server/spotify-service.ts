import { SpotifyApi } from "@spotify/web-api-ts-sdk";

let connectionSettings: any;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    // Return full credentials from cache
    const refreshToken = connectionSettings?.settings?.oauth?.credentials?.refresh_token;
    const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;
    const clientId = connectionSettings?.settings?.oauth?.credentials?.client_id;
    const expiresIn = connectionSettings.settings?.oauth?.credentials?.expires_in;
    return {accessToken, clientId, refreshToken, expiresIn};
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
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
  
  const refreshToken = connectionSettings?.settings?.oauth?.credentials?.refresh_token;
  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;
  const clientId = connectionSettings?.settings?.oauth?.credentials?.client_id;
  const expiresIn = connectionSettings.settings?.oauth?.credentials?.expires_in;
  
  if (!connectionSettings || (!accessToken || !clientId || !refreshToken)) {
    throw new Error('Spotify not connected');
  }
  
  return {accessToken, clientId, refreshToken, expiresIn};
}

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
    const spotify = await getUncachableSpotifyClient();
    
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

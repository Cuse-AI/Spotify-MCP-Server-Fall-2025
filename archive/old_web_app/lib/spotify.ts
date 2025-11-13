import SpotifyWebApi from "spotify-web-api-node";

export function makeSpotifyClient(accessToken?: string, refreshToken?: string) {
  const client = new SpotifyWebApi({
    clientId: process.env.SPOTIFY_CLIENT_ID!,
    clientSecret: process.env.SPOTIFY_CLIENT_SECRET!,
    redirectUri: process.env.SPOTIFY_REDIRECT_URI!,
  });
  if (accessToken) client.setAccessToken(accessToken);
  if (refreshToken) client.setRefreshToken(refreshToken);
  return client;
}

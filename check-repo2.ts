import { Octokit } from '@octokit/rest';

let connectionSettings: any;

async function getAccessToken() {
  if (connectionSettings && connectionSettings.settings.expires_at && new Date(connectionSettings.settings.expires_at).getTime() > Date.now()) {
    return connectionSettings.settings.access_token;
  }
  
  const hostname = process.env.REPLIT_CONNECTORS_HOSTNAME;
  const xReplitToken = process.env.REPL_IDENTITY 
    ? 'repl ' + process.env.REPL_IDENTITY 
    : process.env.WEB_REPL_RENEWAL 
    ? 'depl ' + process.env.WEB_REPL_RENEWAL 
    : null;

  if (!xReplitToken) {
    throw new Error('X_REPLIT_TOKEN not found');
  }

  connectionSettings = await fetch(
    'https://' + hostname + '/api/v2/connection?include_secrets=true&connector_names=github',
    {
      headers: {
        'Accept': 'application/json',
        'X_REPLIT_TOKEN': xReplitToken
      }
    }
  ).then(res => res.json()).then(data => data.items?.[0]);

  const accessToken = connectionSettings?.settings?.access_token || connectionSettings.settings?.oauth?.credentials?.access_token;
  if (!connectionSettings || !accessToken) {
    throw new Error('GitHub not connected');
  }
  return accessToken;
}

async function main() {
  const accessToken = await getAccessToken();
  const octokit = new Octokit({ auth: accessToken });
  
  // Server files
  const server = await octokit.repos.getContent({
    owner: 'Cuse-AI',
    repo: 'Spotify-MCP-Server-Fall-2025',
    path: 'code/web/server'
  });
  
  console.log('=== code/web/server/ ===');
  if (Array.isArray(server.data)) {
    server.data.forEach((item: any) => {
      console.log(`  📄 ${item.name}`);
    });
  }
  
  // Client structure
  const client = await octokit.repos.getContent({
    owner: 'Cuse-AI',
    repo: 'Spotify-MCP-Server-Fall-2025',
    path: 'code/web/client/src'
  });
  
  console.log('\n=== code/web/client/src/ ===');
  if (Array.isArray(client.data)) {
    client.data.forEach((item: any) => {
      console.log(`  ${item.type === 'dir' ? '📁' : '📄'} ${item.name}`);
    });
  }
  
  // Components
  const components = await octokit.repos.getContent({
    owner: 'Cuse-AI',
    repo: 'Spotify-MCP-Server-Fall-2025',
    path: 'code/web/client/src/components'
  });
  
  console.log('\n=== code/web/client/src/components/ ===');
  if (Array.isArray(components.data)) {
    components.data.forEach((item: any) => {
      console.log(`  ${item.type === 'dir' ? '📁' : '📄'} ${item.name}`);
    });
  }
  
  // Pages
  const pages = await octokit.repos.getContent({
    owner: 'Cuse-AI',
    repo: 'Spotify-MCP-Server-Fall-2025',
    path: 'code/web/client/src/pages'
  });
  
  console.log('\n=== code/web/client/src/pages/ ===');
  if (Array.isArray(pages.data)) {
    pages.data.forEach((item: any) => {
      console.log(`  📄 ${item.name}`);
    });
  }
}

main().catch(console.error);

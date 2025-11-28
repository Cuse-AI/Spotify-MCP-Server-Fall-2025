import "dotenv/config";
import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";

const app = express();

declare module 'http' {
  interface IncomingMessage {
    rawBody: unknown
  }
}
app.use(express.json({
  verify: (req, _res, buf) => {
    req.rawBody = buf;
  }
}));
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

// Validate required environment variables at startup
function validateEnvironmentVariables(): void {
  const required = [
    { key: "ANTHROPIC_API_KEY", display: "Anthropic API Key" },
    { key: "SPOTIFY_CLIENT_ID", display: "Spotify Client ID" },
    { key: "SPOTIFY_CLIENT_SECRET", display: "Spotify Client Secret" },
  ];

  const missing: string[] = [];
  
  for (const { key, display } of required) {
    if (!process.env[key]) {
      missing.push(`  ❌ ${display} (${key})`);
    }
  }

  if (missing.length > 0) {
    console.error("\n🚨 STARTUP ERROR: Missing required environment variables!\n");
    console.error(missing.join("\n"));
    console.error("\nPlease set these in your .env file:");
    console.error("  1. Get ANTHROPIC_API_KEY from: https://console.anthropic.com/");
    console.error("  2. Get Spotify credentials from: https://developer.spotify.com/dashboard\n");
    process.exit(1);
  }

  console.log("✅ All required environment variables are set\n");
}

(async () => {
  // Validate all required API keys before starting
  validateEnvironmentVariables();

  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // ALWAYS serve the app on the port specified in the environment variable PORT
  // Other ports are firewalled. Default to 5000 if not specified.
  // this serves both the API and the client.
  // It is the only port that is not firewalled.
  const port = parseInt(process.env.PORT || '5000', 10);
  // Use localhost on Windows to avoid ENOTSUP error
  const host = process.platform === 'win32' ? 'localhost' : '0.0.0.0';
  server.listen(port, host, () => {
    log(`serving on port ${port}`);
  });
})();

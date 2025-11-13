# Tapestry - Conversational Vibe Playlist Generator

## Overview

Tapestry is an emotional music discovery application that generates personalized playlists through a conversational interface. The application asks users three sequential questions about their emotional state and journey, then uses AI (Claude) to curate a playlist from a human-sourced music database. The interface is inspired by ChatGPT's conversational design but features a dark, moody aesthetic that reflects emotional depth and intimacy.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework**: React with TypeScript, using Vite as the build tool and development server.

**UI Component Library**: shadcn/ui components built on Radix UI primitives, providing accessible and customizable components with a dark theme aesthetic.

**Styling Approach**: 
- Tailwind CSS for utility-first styling with custom design tokens
- Dark mode enforced by default (`<html class="dark">`)
- Custom color system using CSS variables for theming
- Inter font family for clean, modern typography
- Design guidelines emphasize conversational intimacy with progressive disclosure

**State Management**:
- React Query (@tanstack/react-query) for server state and API interactions
- Local component state for UI flow control
- No global state management library (Redux, Zustand) - keeping it simple

**Routing**: Wouter for lightweight client-side routing (minimal bundle size compared to React Router).

**Key Design Patterns**:
- Progressive disclosure: Questions appear sequentially, one at a time
- Smooth transitions between states (300ms fade animations)
- Centered, single-focus layout (max-w-2xl) for conversational intimacy
- Vertical centering with breathing room for emotional depth

### Backend Architecture

**Runtime**: Node.js with Express framework

**Language**: TypeScript with ES modules

**API Design**:
- RESTful endpoint: `POST /api/generate-playlist`
- Request validation using Zod schemas
- Simple, flat architecture with no complex middleware chains

**Code Organization**:
- `server/index.ts` - Express server setup and request logging
- `server/routes.ts` - API route definitions
- `server/storage.ts` - Business logic abstraction layer
- `server/claude-service.ts` - AI integration for playlist generation

**Development vs Production**:
- Development: Vite middleware for HMR and fast refresh
- Production: Pre-built static assets served from `dist/public`

### Data Storage

**Database**: PostgreSQL via Neon serverless driver (@neondatabase/serverless)

**ORM**: Drizzle ORM for type-safe database queries

**Schema Location**: `shared/schema.ts` defines data models shared between client and server

**Tapestry Music Data**:
- Loaded from `data/tapestry_complete.json` (8,211 songs - recently expanded)
- Loaded from `data/emotional_manifold_COMPLETE.json` (2D coordinate system)
- Contains human-sourced music recommendations with emotional metadata
- Includes 114 sub-vibes across 9 central emotional centers (Sad, Happy, Chill, Energy, Dark, Romantic, Night, Drive, Party)
- Each song includes Reddit context and Ananki reasoning (Claude-analyzed emotional context)
- Claude receives top 15 songs per sub-vibe (~1,710 songs) to reduce API costs while maintaining quality
- Graceful fallback to sample playlists if data files are missing
- **IMPORTANT**: Files are cached on server startup - restart workflow after updating Tapestry data

**Session Management**: 
- Connect-pg-simple for PostgreSQL-backed sessions
- Session data stored in database for persistence across server restarts

### External Dependencies

**AI Service**: Anthropic Claude API for intelligent playlist generation
- **Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5`)
- **Prompt Caching**: Caches 83K+ tokens (condensed Tapestry manifest) for 90% cost reduction
- **First request**: ~45 seconds (creates cache), subsequent requests: ~5-10 seconds
- **Cost**: ~$0.02 per playlist generation with caching
- Analyzes user journey (3 questions) against emotional music database
- Generates 8-12 songs with explanations and emotional arc descriptions
- "Walks the emotional manifold" using 2D coordinates and emotional compositions
- API key required via `ANTHROPIC_API_KEY` environment variable
- **Content Safety**: Sends only Ananki reasoning (not raw Reddit contexts) to avoid content filters

**Database Service**: Neon PostgreSQL (serverless)
- Requires `DATABASE_URL` environment variable
- Serverless architecture for cost-effective scaling

**Third-party UI Libraries**:
- Radix UI - Accessible, unstyled component primitives
- Lucide React - Icon library
- cmdk - Command menu component
- date-fns - Date utility functions
- embla-carousel-react - Carousel functionality
- react-day-picker - Calendar component
- recharts - Chart components
- vaul - Drawer component

**Development Tools**:
- Replit-specific plugins for development banner and error overlay
- Cartographer plugin for Replit integration
- esbuild for production bundling

**Build Process**:
- Development: `tsx` for TypeScript execution with `NODE_ENV=development`
- Production build: Vite builds frontend, esbuild bundles backend
- Database migrations: Drizzle Kit for schema management

**Type Safety**: Full TypeScript coverage with strict mode enabled, shared types between client and server via `shared/` directory.
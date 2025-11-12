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
- Expected to be loaded from `data/tapestry_VALIDATED_ONLY.json`
- Contains human-sourced music recommendations with emotional metadata
- Includes 114 sub-vibes and higher-level meta-vibe categories
- Each song includes Reddit context and emotional reasoning
- Currently supports fallback to sample playlists if data file is missing

**Session Management**: 
- Connect-pg-simple for PostgreSQL-backed sessions
- Session data stored in database for persistence across server restarts

### External Dependencies

**AI Service**: Anthropic Claude API for intelligent playlist generation
- Uses prompt caching for efficient processing of large tapestry dataset
- Analyzes user journey (3 questions) against emotional music database
- Generates playlist with explanations and emotional arc descriptions
- API key required via `ANTHROPIC_API_KEY` environment variable

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
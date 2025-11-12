import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { PlaylistResponse } from "@shared/schema";
import { Music2 } from "lucide-react";

interface PlaylistResultsProps {
  data: PlaylistResponse;
  onStartOver: () => void;
}

export function PlaylistResults({ data, onStartOver }: PlaylistResultsProps) {
  return (
    <div className="min-h-screen px-6 py-12 md:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light mb-4" data-testid="text-results-title">
            Your Emotional Journey
          </h1>
          <p className="text-muted-foreground leading-relaxed max-w-2xl mx-auto" data-testid="text-journey-explanation">
            {data.explanation}
          </p>
          {data.emotionalArc && (
            <p className="text-sm text-muted-foreground/80 mt-4 italic">
              {data.emotionalArc}
            </p>
          )}
        </div>

        {/* Playlist */}
        <Card className="mb-8 overflow-hidden" data-testid="card-playlist">
          <div className="divide-y divide-border">
            {data.songs.map((song, index) => (
              <div
                key={`${song.track_id}-${index}`}
                className="flex items-center gap-4 p-4 hover-elevate transition-all"
                data-testid={`song-item-${index}`}
              >
                <div className="flex-shrink-0 w-12 h-12 bg-card-border rounded flex items-center justify-center">
                  <Music2 className="w-5 h-5 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate" data-testid={`text-song-title-${index}`}>
                    {song.title}
                  </h3>
                  <p className="text-sm text-muted-foreground truncate" data-testid={`text-song-artist-${index}`}>
                    {song.artist}
                  </p>
                  <p className="text-xs text-muted-foreground/60 mt-1">
                    {song.sub_vibe} • {Math.round(song.confidence * 100)}% match
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            size="lg"
            className="px-8"
            data-testid="button-create-spotify-playlist"
            onClick={() => {
              // TODO: Spotify integration
              alert("Spotify integration coming soon!");
            }}
          >
            Create Playlist on Spotify
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="px-8"
            onClick={onStartOver}
            data-testid="button-start-over"
          >
            Start Over
          </Button>
        </div>

        {/* Song Details (Optional Expand) */}
        {data.songs.some((s) => s.ananki_reasoning || s.reddit_context) && (
          <details className="mt-12">
            <summary className="text-sm text-muted-foreground cursor-pointer hover:text-foreground transition-colors text-center">
              View song reasoning & context
            </summary>
            <div className="mt-6 space-y-4">
              {data.songs.map((song, index) => (
                <Card key={`detail-${song.track_id}-${index}`} className="p-4">
                  <h4 className="font-medium mb-2">
                    {song.title} - {song.artist}
                  </h4>
                  {song.ananki_reasoning && (
                    <p className="text-sm text-muted-foreground mb-2">
                      <span className="font-medium text-foreground">Ananki: </span>
                      {song.ananki_reasoning}
                    </p>
                  )}
                  {song.reddit_context && (
                    <p className="text-xs text-muted-foreground/80">
                      <span className="font-medium text-foreground">Context: </span>
                      {song.reddit_context}
                    </p>
                  )}
                </Card>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { PlaylistResponse, TapestrySong, UserJourney } from "@shared/schema";
import { Music2, ThumbsUp } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

interface PlaylistResultsProps {
  data: PlaylistResponse;
  onStartOver: () => void;
}

export function PlaylistResults({ data, onStartOver }: PlaylistResultsProps) {
  const { toast } = useToast();
  const [validatedSongs, setValidatedSongs] = useState<Set<string>>(new Set());

  const handleValidateSong = async (song: TapestrySong) => {
    try {
      await apiRequest("/api/validate-song", {
        method: "POST",
        body: JSON.stringify({
          song: {
            track_id: song.track_id,
            artist: song.artist,
            title: song.title,
            sub_vibe: song.sub_vibe,
            meta_vibe: song.meta_vibe,
            confidence: song.confidence,
            manifold_x: song.manifold_x,
            manifold_y: song.manifold_y,
            emotional_composition: song.emotional_composition,
            extrapolated: song.extrapolated,
          },
          user_journey: data.journey,
        }),
        headers: { "Content-Type": "application/json" },
      });

      setValidatedSongs((prev) => new Set(prev).add(song.track_id));
      
      toast({
        title: "✨ Added to Tapestry!",
        description: `"${song.title}" is now part of the manifold`,
        duration: 3000,
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to add song to Tapestry",
        duration: 3000,
      });
    }
  };

  if (!data || !data.songs || data.songs.length === 0) {
    return (
      <div className="min-h-screen px-6 py-12 md:px-8 flex items-center justify-center">
        <Card className="p-8 max-w-md text-center">
          <h2 className="text-xl font-medium mb-4">No Playlist Generated</h2>
          <p className="text-muted-foreground mb-6">
            We encountered an issue generating your playlist. This might be due to API configuration or connectivity issues.
          </p>
          <Button onClick={onStartOver} data-testid="button-start-over">
            Try Again
          </Button>
        </Card>
      </div>
    );
  }

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
            {data.songs.map((song, index) => {
              const isValidated = validatedSongs.has(song.track_id);
              
              return (
                <div
                  key={`${song.track_id}-${index}`}
                  className="flex items-center gap-4 p-4 hover-elevate transition-all relative"
                  data-testid={`song-item-${index}`}
                >
                  <div className="flex-shrink-0 w-12 h-12 bg-card-border rounded flex items-center justify-center">
                    <Music2 className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0 pr-10">
                    <h3 className="font-medium truncate" data-testid={`text-song-title-${index}`}>
                      {song.title}
                    </h3>
                    <p className="text-sm text-muted-foreground truncate" data-testid={`text-song-artist-${index}`}>
                      {song.artist}
                    </p>
                    <p className="text-xs text-muted-foreground/60 mt-1">
                      {song.sub_vibe} • {Math.round(song.confidence * 100)}% match
                      {song.extrapolated && <span className="ml-2 text-primary">✨ AI extrapolated</span>}
                    </p>
                  </div>
                  
                  {/* Thumbs up button - subtle, bottom-right */}
                  <button
                    onClick={() => handleValidateSong(song)}
                    disabled={isValidated}
                    className={`absolute bottom-3 right-3 p-1.5 rounded-md transition-all ${
                      isValidated
                        ? "text-primary opacity-100"
                        : "text-muted-foreground opacity-40 hover:opacity-100 hover-elevate"
                    }`}
                    data-testid={`button-validate-song-${index}`}
                    title={isValidated ? "Added to Tapestry!" : "Add to Tapestry"}
                  >
                    <ThumbsUp className="w-3.5 h-3.5" fill={isValidated ? "currentColor" : "none"} />
                  </button>
                </div>
              );
            })}
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

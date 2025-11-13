import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { PlaylistResponse, TapestrySong, UserJourney } from "@shared/schema";
import { Music2, ThumbsUp, ThumbsDown, Play, Pause } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useState, useRef, useEffect } from "react";
import { CosmicBackground } from "./cosmic-background";

interface PlaylistResultsProps {
  data: PlaylistResponse;
  onStartOver: () => void;
}

export function PlaylistResults({ data, onStartOver }: PlaylistResultsProps) {
  const { toast } = useToast();
  const [validatedSongs, setValidatedSongs] = useState<Set<string>>(new Set());
  const [downvotedSongs, setDownvotedSongs] = useState<Set<string>>(new Set());
  const [playingTrackId, setPlayingTrackId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handlePlayPreview = (trackId: string, previewUrl: string) => {
    if (playingTrackId === trackId) {
      // Pause current track
      audioRef.current?.pause();
      setPlayingTrackId(null);
    } else {
      // Stop any currently playing track
      audioRef.current?.pause();
      
      // Play new track
      const audio = new Audio(previewUrl);
      audioRef.current = audio;
      audio.play();
      setPlayingTrackId(trackId);
      
      // Reset when track ends
      audio.addEventListener('ended', () => {
        setPlayingTrackId(null);
      });
    }
  };

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      audioRef.current?.pause();
    };
  }, []);

  const handleValidateSong = async (song: TapestrySong) => {
    try {
      const response = await apiRequest("POST", "/api/validate-song", {
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
      });

      const result = await response.json();
      setValidatedSongs((prev) => new Set(prev).add(song.track_id));
      
      toast({
        title: result.boosted ? "⬆️ Confidence boosted!" : "✨ Added to Tapestry!",
        description: result.boosted 
          ? `"${song.title}" validation count increased`
          : `"${song.title}" is now part of the manifold`,
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

  const handleDownvoteSong = async (song: TapestrySong) => {
    try {
      await apiRequest("POST", "/api/downvote-song", {
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
      });

      setDownvotedSongs((prev) => new Set(prev).add(song.track_id));
      
      toast({
        title: "Feedback recorded",
        description: `"${song.title}" flagged for review`,
        duration: 3000,
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to record feedback",
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
    <>
      <CosmicBackground />
      <div className="min-h-screen px-6 py-12 md:px-8 relative z-10">
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
        <Card 
          className="mb-8 overflow-hidden border-2 border-purple-500/20 shadow-[0_0_20px_rgba(168,85,247,0.1)]" 
          data-testid="card-playlist"
        >
          <div className="divide-y divide-border">
            {data.songs.map((song, index) => {
              const isValidated = validatedSongs.has(song.track_id);
              const isDownvoted = downvotedSongs.has(song.track_id);
              
              const isPlaying = playingTrackId === song.track_id;
              
              return (
                <div
                  key={`${song.track_id}-${index}`}
                  className="flex items-center gap-4 p-4 hover-elevate transition-all relative"
                  data-testid={`song-item-${index}`}
                >
                  {/* Album cover or placeholder */}
                  <div className="flex-shrink-0 w-16 h-16 rounded overflow-hidden bg-card-border relative group">
                    {song.album_art ? (
                      <>
                        <img 
                          src={song.album_art} 
                          alt={`${song.title} album cover`}
                          className="w-full h-full object-cover"
                          data-testid={`img-album-${index}`}
                        />
                        {/* Play button overlay on album cover */}
                        {song.preview_url && (
                          <button
                            onClick={() => handlePlayPreview(song.track_id, song.preview_url!)}
                            className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                            data-testid={`button-preview-${index}`}
                            title={isPlaying ? "Pause preview" : "Play preview"}
                          >
                            {isPlaying ? (
                              <Pause className="w-6 h-6 text-white" fill="white" />
                            ) : (
                              <Play className="w-6 h-6 text-white" fill="white" />
                            )}
                          </button>
                        )}
                      </>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Music2 className="w-6 h-6 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0 pr-20">
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
                  
                  {/* Feedback buttons - subtle, bottom-right */}
                  <div className="absolute bottom-3 right-3 flex gap-2">
                    {/* Thumbs up - green outline on hover */}
                    <button
                      onClick={() => handleValidateSong(song)}
                      disabled={isValidated || isDownvoted}
                      className={`p-1.5 rounded-md transition-all border ${
                        isValidated
                          ? "text-green-500 border-green-500 opacity-100"
                          : isDownvoted
                          ? "text-muted-foreground/30 border-transparent opacity-30 cursor-not-allowed"
                          : "text-muted-foreground border-transparent opacity-40 hover:opacity-100 hover:border-green-500 hover:text-green-500"
                      }`}
                      data-testid={`button-validate-song-${index}`}
                      title={isValidated ? "Added to Tapestry!" : isDownvoted ? "Already downvoted" : "Add to Tapestry"}
                    >
                      <ThumbsUp className="w-3.5 h-3.5" fill={isValidated ? "currentColor" : "none"} />
                    </button>
                    
                    {/* Thumbs down - red outline on hover */}
                    <button
                      onClick={() => handleDownvoteSong(song)}
                      disabled={isDownvoted || isValidated}
                      className={`p-1.5 rounded-md transition-all border ${
                        isDownvoted
                          ? "text-red-500 border-red-500 opacity-100"
                          : isValidated
                          ? "text-muted-foreground/30 border-transparent opacity-30 cursor-not-allowed"
                          : "text-muted-foreground border-transparent opacity-40 hover:opacity-100 hover:border-red-500 hover:text-red-500"
                      }`}
                      data-testid={`button-downvote-song-${index}`}
                      title={isDownvoted ? "Flagged for review" : isValidated ? "Already validated" : "Flag as poor match"}
                    >
                      <ThumbsDown className="w-3.5 h-3.5" fill={isDownvoted ? "currentColor" : "none"} />
                    </button>
                  </div>
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
                <Card 
                  key={`detail-${song.track_id}-${index}`} 
                  className="p-4 border-2 border-purple-500/20 shadow-[0_0_15px_rgba(168,85,247,0.08)]"
                >
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
    </>
  );
}

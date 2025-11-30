import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

interface TapestryStats {
  total_tracks: number;
  total_meta_vibes: number;
  total_sub_vibes: number;
}

export function TapestryStatsBanner() {
  const [stats, setStats] = useState<TapestryStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await fetch("/core/tapestry.json");
        if (!response.ok) throw new Error("Failed to load tapestry data");
        
        const tapestry = await response.json();
        
        // Calculate stats directly from the data
        const totalTracks = Object.values(tapestry.vibes || {}).reduce(
          (sum: number, vibe: any) => sum + (vibe.songs?.length || 0),
          0
        );

        setStats({
          total_tracks: totalTracks,
          total_meta_vibes: 9,
          total_sub_vibes: 114,
        });
      } catch (error) {
        console.error("Error loading tapestry stats:", error);
        // Set fallback values
        setStats({
          total_tracks: 0,
          total_meta_vibes: 9,
          total_sub_vibes: 114,
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, []);

  if (isLoading || !stats) {
    return (
      <Card className="px-4 py-3 flex items-center gap-3 min-w-[280px]" data-testid="card-tapestry-stats-loading">
        <div className="w-5 h-5 rounded-full bg-muted animate-pulse" data-testid="skeleton-icon" />
        <div className="flex-1">
          <div className="h-4 w-24 bg-muted rounded animate-pulse mb-1" data-testid="skeleton-track-count" />
          <div className="h-3 w-32 bg-muted rounded animate-pulse" data-testid="skeleton-vibe-counts" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="px-4 py-3 flex items-center gap-3 min-w-[280px]" data-testid="card-tapestry-stats">
      <Sparkles className="w-5 h-5 text-primary flex-shrink-0" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium" data-testid="text-track-count">
          {stats.total_tracks.toLocaleString()} tracks
        </div>
        <div className="text-xs text-muted-foreground flex items-center gap-1.5">
          <span data-testid="text-vibe-counts">
            {stats.total_meta_vibes} metavibes • {stats.total_sub_vibes} subvibes
          </span>
          <span className="text-muted-foreground/40">•</span>
          <span className="text-primary/90 font-medium" data-testid="text-human-sourced">
            100% human-sourced
          </span>
        </div>
      </div>
    </Card>
  );
}

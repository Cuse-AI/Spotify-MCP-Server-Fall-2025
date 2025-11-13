import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import type { TapestryStats } from "@shared/schema";
import { Sparkles } from "lucide-react";

export function TapestryStatsBanner() {
  const { data: stats, isLoading } = useQuery<TapestryStats>({
    queryKey: ["/api/tapestry-stats"],
  });

  if (isLoading || !stats) {
    return (
      <Card className="px-4 py-3 flex items-center gap-3 min-w-[280px]">
        <div className="w-5 h-5 rounded-full bg-muted animate-pulse" />
        <div className="flex-1">
          <div className="h-4 w-24 bg-muted rounded animate-pulse mb-1" />
          <div className="h-3 w-32 bg-muted rounded animate-pulse" />
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

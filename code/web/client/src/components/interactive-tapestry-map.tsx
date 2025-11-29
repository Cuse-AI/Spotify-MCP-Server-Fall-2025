import { useState, useEffect, useRef } from "react";
import { TapestryCanvas } from "./tapestry-canvas";
import { TaperySidePanel } from "./tapestry-side-panel";

interface SubVibeData {
  name: string;
  composition: Record<string, number>;
  analysis: string;
  songs: Array<{
    artist: string;
    song: string;
    comment_text: string;
  }>;
  songCount: number;
}

interface CentralVibeData {
  name: string;
  description: string;
  connectsTo: string[];
}

export function InteractiveTapestryMap() {
  const [manifoldData, setManifoldData] = useState<any>(null);
  const [tapestryData, setTapestryData] = useState<any>(null);
  const [selectedVibe, setSelectedVibe] = useState<SubVibeData | CentralVibeData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load manifold data
        const manifoldRes = await fetch("/core/emotional_manifold_COMPLETE.json");
        const manifold = await manifoldRes.json();
        setManifoldData(manifold);

        // Load tapestry data
        const tapestryRes = await fetch("/core/tapestry.json");
        const tapestry = await tapestryRes.json();
        setTapestryData(tapestry);

        console.log("✅ Loaded manifold and tapestry data");
      } catch (error) {
        console.error("Error loading data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleSubVibeClick = (subVibeName: string) => {
    if (!manifoldData || !tapestryData) return;

    const subVibe = manifoldData.sub_vibes[subVibeName];
    const songs = tapestryData.vibes[subVibeName]?.songs || [];

    // Filter and sort for high-quality display
    const qualitySongs = songs
      .filter((s: any) => {
        // Prefer songs with good human context (30-300 chars)
        const commentLen = (s.comment_text || "").length;
        return commentLen >= 30 && commentLen <= 300;
      })
      .sort((a: any, b: any) => b.mapping_confidence - a.mapping_confidence)
      .slice(0, 3);

    // Fallback to top confidence songs if no quality filter matches
    const displaySongs = qualitySongs.length >= 2 
      ? qualitySongs 
      : songs.sort((a: any, b: any) => b.mapping_confidence - a.mapping_confidence).slice(0, 3);

    const selectedData: SubVibeData = {
      name: subVibeName,
      composition: subVibe.emotional_composition,
      analysis: subVibe.analysis,
      songs: displaySongs.map((s: any) => ({
        artist: s.artist,
        song: s.song,
        // Use ananki_reasoning if comment_text is too long/short, otherwise use comment
        comment_text: (s.comment_text && s.comment_text.length >= 30 && s.comment_text.length <= 300) 
          ? s.comment_text 
          : (s.ananki_reasoning ? s.ananki_reasoning.slice(0, 200) + "..." : s.comment_text || "Quality-mapped to this vibe"),
      })),
      songCount: songs.length,
    };

    setSelectedVibe(selectedData);
  };

  const handleCentralVibeClick = (centralVibeName: string) => {
    if (!manifoldData) return;

    const relationships = manifoldData.central_vibes?.positions || {};
    const description = manifoldData.central_vibes?.descriptions?.[centralVibeName] || "Core emotional center";

    // Find all sub-vibes that have this vibe as dominant
    const connectedSubVibes = Object.entries(manifoldData.sub_vibes)
      .filter(([_, data]: [string, any]) => {
        const dominant = Object.entries(data.emotional_composition)
          .sort((a: any, b: any) => b[1] - a[1])[0]?.[0];
        return dominant === centralVibeName;
      })
      .map(([name]) => name)
      .slice(0, 10);

    const selectedData: CentralVibeData = {
      name: centralVibeName,
      description,
      connectsTo: connectedSubVibes as string[],
    };

    setSelectedVibe(selectedData);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-2">
          <p className="text-muted-foreground">Loading tapestry...</p>
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
        </div>
      </div>
    );
  }

  if (!manifoldData || !tapestryData) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-destructive">Error loading tapestry data</p>
      </div>
    );
  }

  return (
    <div className="flex gap-6 h-full min-h-[600px]">
      {/* Canvas */}
      <div className="flex-1 min-w-0">
        <TapestryCanvas
          manifoldData={manifoldData}
          onSubVibeClick={handleSubVibeClick}
          onCentralVibeClick={handleCentralVibeClick}
        />
      </div>

      {/* Side Panel */}
      <div className="w-80 flex-shrink-0 overflow-y-auto">
        {selectedVibe ? (
          <TaperySidePanel data={selectedVibe} />
        ) : (
          <div className="bg-muted rounded-lg p-4 text-center text-muted-foreground">
            <p className="text-sm">Click on a vibe to explore</p>
          </div>
        )}
      </div>
    </div>
  );
}

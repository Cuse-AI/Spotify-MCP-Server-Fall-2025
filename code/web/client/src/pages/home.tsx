import { useState } from "react";
import { ConversationalFlow } from "@/components/conversational-flow";
import { PlaylistResults } from "@/components/playlist-results";
import type { PlaylistResponse } from "@shared/schema";

export default function Home() {
  const [playlistData, setPlaylistData] = useState<PlaylistResponse | null>(null);

  const handleJourneyComplete = (data: PlaylistResponse) => {
    setPlaylistData(data);
  };

  const handleStartOver = () => {
    setPlaylistData(null);
  };

  return (
    <div className="min-h-screen bg-background relative">
      {/* Subtle background gradient for depth */}
      <div className="fixed inset-0 bg-gradient-radial from-primary/5 via-transparent to-transparent opacity-30 pointer-events-none" />
      
      <div className="relative z-10">
        {!playlistData ? (
          <ConversationalFlow onComplete={handleJourneyComplete} />
        ) : (
          <PlaylistResults data={playlistData} onStartOver={handleStartOver} />
        )}
      </div>
    </div>
  );
}

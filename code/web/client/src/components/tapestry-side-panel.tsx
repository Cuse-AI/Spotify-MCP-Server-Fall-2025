import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from "recharts";

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

interface TaperySidePanelProps {
  data: SubVibeData | CentralVibeData;
}

function isSubVibe(data: any): data is SubVibeData {
  return "songCount" in data;
}

export function TaperySidePanel({ data }: TaperySidePanelProps) {
  if (isSubVibe(data)) {
    // Sub-vibe panel (rich)
    const compositionData = Object.entries(data.composition)
      .sort((a, b) => b[1] - a[1])
      .map(([name, value]) => ({
        name,
        percentage: Math.round(value * 100),
      }));

    return (
      <div className="space-y-6 p-4 bg-muted/30 rounded-lg border border-muted">
        {/* Header */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-primary">{data.name}</h2>
          <p className="text-xs text-muted-foreground">
            {data.songCount.toLocaleString()} songs in this vibe
          </p>
        </div>

        {/* Emotional Composition Bar Chart */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Emotional Composition</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={compositionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" style={{ fontSize: "12px" }} />
              <YAxis stroke="#888" style={{ fontSize: "12px" }} />
              <ChartTooltip
                contentStyle={{
                  backgroundColor: "#1a1a1a",
                  border: "1px solid #333",
                }}
                formatter={(value) => `${value}%`}
              />
              <Bar dataKey="percentage" fill="#FFD700" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Analysis */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">What is this vibe?</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {data.analysis}
          </p>
        </div>

        {/* Quotes from real songs */}
        {data.songs.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">
              💬 What People Say About It
            </h3>
            <div className="space-y-3">
              {data.songs.map((song, idx) => (
                <div
                  key={idx}
                  className="bg-background/50 rounded p-3 border border-muted/50 space-y-2"
                >
                  <p className="text-xs text-muted-foreground italic">
                    "{song.comment_text}"
                  </p>
                  <p className="text-xs font-medium text-primary">
                    — {song.artist} • {song.song}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  } else {
    // Central vibe panel (simple)
    return (
      <div className="space-y-4 p-4 bg-muted/30 rounded-lg border border-muted">
        {/* Header */}
        <div className="space-y-2">
          <h2 className="text-2xl font-bold text-primary">{data.name}</h2>
          <p className="text-sm text-muted-foreground">(Central Emotional Center)</p>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">Overview</h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {data.description}
          </p>
        </div>

        {/* Connected sub-vibes */}
        {data.connectsTo.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold">
              Related Sub-Vibes ({data.connectsTo.length})
            </h3>
            <div className="space-y-1">
              {data.connectsTo.map((subVibe) => (
                <div
                  key={subVibe}
                  className="text-xs bg-background/50 rounded px-2 py-1 text-muted-foreground border border-muted/30"
                >
                  • {subVibe}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
}

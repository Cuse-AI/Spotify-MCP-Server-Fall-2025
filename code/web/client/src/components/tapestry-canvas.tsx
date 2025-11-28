import { useEffect, useRef } from "react";

interface TapestryCanvasProps {
  manifoldData: any;
  onSubVibeClick: (name: string) => void;
  onCentralVibeClick: (name: string) => void;
}

export function TapestryCanvas({
  manifoldData,
  onSubVibeClick,
  onCentralVibeClick,
}: TapestryCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const vibeColors: Record<string, string> = {
    Sad: "#4A5899",
    Happy: "#FFD700",
    Chill: "#87CEEB",
    Anxious: "#FF6B6B",
    Energy: "#FF4500",
    Dark: "#2F2F4F",
    Introspective: "#9370DB",
    Romantic: "#FF69B4",
    Nostalgic: "#DDA0DD",
    Night: "#191970",
    Drive: "#4682B4",
    Party: "#FF1493",
    Angry: "#DC143C",
    Bitter: "#8B4513",
    Hopeful: "#FFA500",
    Excited: "#FFD700",
    Jealous: "#228B22",
    Peaceful: "#E0FFE0",
    Playful: "#FF69B4",
    Chaotic: "#8B0000",
    Bored: "#696969",
    Grateful: "#DAA520",
    Confident: "#FF8C00",
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const scale = 1.1;
    const offsetX = 20;
    const offsetY = 20;

    function toCanvasCoords(x: number, y: number) {
      return {
        x: x * scale + offsetX,
        y: y * scale + offsetY,
      };
    }

    const centralPositions = manifoldData.central_vibes.positions;
    const subVibes = manifoldData.sub_vibes;

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connection lines
      ctx.strokeStyle = "#222";
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.3;

      for (const [vibe, data] of Object.entries(centralPositions) as [
        string,
        any
      ][]) {
        const pos1 = toCanvasCoords(data.x, data.y);

        for (const otherVibe of Object.keys(centralPositions)) {
          if (vibe !== otherVibe) {
            const pos2 = toCanvasCoords(
              (centralPositions[otherVibe] as any).x,
              (centralPositions[otherVibe] as any).y
            );
            ctx.beginPath();
            ctx.moveTo(pos1.x, pos1.y);
            ctx.lineTo(pos2.x, pos2.y);
            ctx.stroke();
          }
        }
      }

      ctx.globalAlpha = 1;

      // Draw sub-vibes (small dots)
      for (const [name, data] of Object.entries(subVibes) as [string, any][]) {
        const pos = toCanvasCoords(data.coordinates.x, data.coordinates.y);
        const dominantVibe = Object.entries(data.emotional_composition)
          .sort((a: any, b: any) => b[1] - a[1])[0]?.[0] as string;
        const color = vibeColors[dominantVibe] || "#FFFFFF";

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }

      // Draw central vibes (large circles)
      for (const [name, pos] of Object.entries(centralPositions) as [
        string,
        any
      ][]) {
        const canvasPos = toCanvasCoords(pos.x, pos.y);
        const color = vibeColors[name] || "#FFFFFF";

        ctx.beginPath();
        ctx.arc(canvasPos.x, canvasPos.y, 15, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = "white";
        ctx.font = "bold 11px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(name, canvasPos.x, canvasPos.y);
      }
    }

    draw();

    // Mouse handlers
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      let hoveredItem: { type: string; name: string } | null = null;

      // Check sub-vibes
      for (const [name, data] of Object.entries(subVibes) as [string, any][]) {
        const pos = toCanvasCoords(data.coordinates.x, data.coordinates.y);
        const dist = Math.sqrt(
          (mouseX - pos.x) ** 2 + (mouseY - pos.y) ** 2
        );

        if (dist < 8) {
          hoveredItem = { type: "subvibe", name };
          canvas.style.cursor = "pointer";
          break;
        }
      }

      // Check central vibes
      if (!hoveredItem) {
        for (const [name, pos] of Object.entries(centralPositions) as [
          string,
          any
        ][]) {
          const canvasPos = toCanvasCoords(pos.x, pos.y);
          const dist = Math.sqrt(
            (mouseX - canvasPos.x) ** 2 + (mouseY - canvasPos.y) ** 2
          );

          if (dist < 20) {
            hoveredItem = { type: "centralvibe", name };
            canvas.style.cursor = "pointer";
            break;
          }
        }
      }

      if (!hoveredItem) {
        canvas.style.cursor = "crosshair";
      }
    };

    const handleClick = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      // Check sub-vibes
      for (const [name, data] of Object.entries(subVibes) as [string, any][]) {
        const pos = toCanvasCoords(data.coordinates.x, data.coordinates.y);
        const dist = Math.sqrt(
          (mouseX - pos.x) ** 2 + (mouseY - pos.y) ** 2
        );

        if (dist < 8) {
          onSubVibeClick(name);
          return;
        }
      }

      // Check central vibes
      for (const [name, pos] of Object.entries(centralPositions) as [
        string,
        any
      ][]) {
        const canvasPos = toCanvasCoords(pos.x, pos.y);
        const dist = Math.sqrt(
          (mouseX - canvasPos.x) ** 2 + (mouseY - canvasPos.y) ** 2
        );

        if (dist < 20) {
          onCentralVibeClick(name);
          return;
        }
      }
    };

    canvas.addEventListener("mousemove", handleMouseMove);
    canvas.addEventListener("click", handleClick);

    return () => {
      canvas.removeEventListener("mousemove", handleMouseMove);
      canvas.removeEventListener("click", handleClick);
    };
  }, [manifoldData, onSubVibeClick, onCentralVibeClick]);

  return (
    <div className="bg-black rounded-lg border border-muted flex items-center justify-center overflow-hidden">
      <canvas
        ref={canvasRef}
        width={800}
        height={800}
        className="max-w-full max-h-full"
      />
    </div>
  );
}

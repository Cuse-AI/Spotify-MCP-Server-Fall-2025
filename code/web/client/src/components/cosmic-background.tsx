import { useEffect, useRef } from "react";

export function CosmicBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const nodes: { x: number; y: number; vx: number; vy: number; connections: number[] }[] = [];
    const nodeCount = 40;
    const connectionDistance = 200;
    const nodeRadius = 1.5;

    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
        connections: [],
      });
    }

    const drawNebula = () => {
      const gradient1 = ctx.createRadialGradient(
        canvas.width * 0.15,
        canvas.height * 0.2,
        0,
        canvas.width * 0.15,
        canvas.height * 0.2,
        canvas.width * 0.4
      );
      gradient1.addColorStop(0, "rgba(147, 51, 234, 0.08)");
      gradient1.addColorStop(0.5, "rgba(147, 51, 234, 0.03)");
      gradient1.addColorStop(1, "rgba(147, 51, 234, 0)");

      const gradient2 = ctx.createRadialGradient(
        canvas.width * 0.85,
        canvas.height * 0.75,
        0,
        canvas.width * 0.85,
        canvas.height * 0.75,
        canvas.width * 0.35
      );
      gradient2.addColorStop(0, "rgba(168, 85, 247, 0.06)");
      gradient2.addColorStop(0.5, "rgba(168, 85, 247, 0.02)");
      gradient2.addColorStop(1, "rgba(168, 85, 247, 0)");

      ctx.fillStyle = gradient1;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = gradient2;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    const animate = () => {
      ctx.fillStyle = "rgba(15, 13, 17, 1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      drawNebula();

      nodes.forEach((node) => {
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

        node.x = Math.max(0, Math.min(canvas.width, node.x));
        node.y = Math.max(0, Math.min(canvas.height, node.y));
      });

      nodes.forEach((nodeA, i) => {
        nodeA.connections = [];
        nodes.forEach((nodeB, j) => {
          if (i === j) return;
          const dx = nodeA.x - nodeB.x;
          const dy = nodeA.y - nodeB.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < connectionDistance) {
            nodeA.connections.push(j);
            const opacity = (1 - distance / connectionDistance) * 0.15;
            ctx.strokeStyle = `rgba(168, 85, 247, ${opacity})`;
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(nodeA.x, nodeA.y);
            ctx.lineTo(nodeB.x, nodeB.y);
            ctx.stroke();
          }
        });
      });

      nodes.forEach((node) => {
        const gradient = ctx.createRadialGradient(
          node.x,
          node.y,
          0,
          node.x,
          node.y,
          nodeRadius * 2
        );
        gradient.addColorStop(0, "rgba(217, 160, 255, 0.9)");
        gradient.addColorStop(1, "rgba(168, 85, 247, 0)");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius * 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "rgba(255, 255, 255, 0.95)";
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 pointer-events-none"
      style={{ background: "#0f0d11" }}
    />
  );
}

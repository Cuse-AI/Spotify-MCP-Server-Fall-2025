import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { X } from "lucide-react";
import { InteractiveTapestryMap } from "./interactive-tapestry-map";

interface TapestryMapModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TapestryMapModal({ isOpen, onClose }: TapestryMapModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>🗺️ The Emotional Tapestry</span>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Every song in Midden is mapped to emotional coordinates on a 2D manifold. 
            Click on any vibe to explore its emotional composition and see what real people say about it.
          </p>

          {/* Interactive Visualization */}
          <InteractiveTapestryMap />

          <div className="space-y-4 pt-4 border-t border-muted">
            <h3 className="font-semibold text-sm">Why This Matters</h3>
            <ul className="space-y-2 text-xs text-muted-foreground">
              <li>✨ <strong>Not keyword matching</strong> - Real emotional understanding from Reddit discussions</li>
              <li>🎵 <strong>5,700+ quality-verified songs</strong> with complete provenance and emotional reasoning</li>
              <li>💭 <strong>Emotional journey mapping</strong> - From where you are to where you want to go</li>
              <li>🤝 <strong>100% human-sourced</strong> - Every song has context from real people describing their feelings</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

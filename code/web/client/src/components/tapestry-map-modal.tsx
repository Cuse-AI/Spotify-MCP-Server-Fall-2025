import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { X } from "lucide-react";

interface TapestryMapModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TapestryMapModal({ isOpen, onClose }: TapestryMapModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>The Emotional Tapestry</span>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="w-4 h-4" />
            </button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          <div className="prose prose-invert max-w-none">
            <p className="text-sm text-muted-foreground">
              Every song in Midden is mapped to emotional coordinates on a 2D manifold. 
              This tapestry captures 114 emotional sub-vibes across 9 meta-vibes, all sourced from real human conversations about music.
            </p>
          </div>

          {/* Placeholder for the interactive visualization */}
          <div className="bg-muted rounded-lg p-8 flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-2">
              <p className="text-muted-foreground">
                🗺️ Interactive Tapestry Visualization
              </p>
              <p className="text-xs text-muted-foreground">
                Coming soon: 2D emotional manifold with interactive exploration
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold">Why This Matters</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>✨ <strong>Not keyword matching</strong> - Real emotional understanding from Reddit discussions</li>
              <li>🎵 <strong>8,726 songs</strong> with complete provenance and emotional reasoning</li>
              <li>💭 <strong>Emotional journey mapping</strong> - From where you are to where you want to go</li>
              <li>🤝 <strong>100% human-sourced</strong> - Every song has context from real people describing their feelings</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

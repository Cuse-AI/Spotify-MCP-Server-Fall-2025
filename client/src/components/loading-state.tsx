export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen px-6">
      <div className="text-center max-w-md">
        <div className="mb-8">
          <div className="inline-flex gap-2">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: "0ms" }}></span>
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: "200ms" }}></span>
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: "400ms" }}></span>
          </div>
        </div>
        <p className="text-xl font-light text-muted-foreground" data-testid="text-loading-message">
          Walking the emotional tapestry...
        </p>
        <p className="text-sm text-muted-foreground/60 mt-4 font-light">
          Finding the perfect songs for your journey
        </p>
      </div>
    </div>
  );
}

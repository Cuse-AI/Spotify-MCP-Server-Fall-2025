"""
Auto-sync watcher for tapestry.json
Watches for changes and automatically runs sync_to_webapp.py
"""

import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TapestryChangeHandler(FileSystemEventHandler):
    def __init__(self, sync_script_path):
        self.sync_script_path = sync_script_path
        self.last_sync = 0
        self.debounce_seconds = 2  # Wait 2 seconds before syncing to avoid multiple triggers

    def on_modified(self, event):
        if event.src_path.endswith('tapestry.json'):
            current_time = time.time()

            # Debounce - only sync if enough time has passed since last sync
            if current_time - self.last_sync < self.debounce_seconds:
                return

            self.last_sync = current_time
            print(f"\n[WATCHER] tapestry.json modified - auto-syncing...")

            try:
                result = subprocess.run(
                    [sys.executable, self.sync_script_path],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print("[WATCHER] ✓ Sync completed successfully")
                else:
                    print(f"[WATCHER] ✗ Sync failed: {result.stderr}")

            except Exception as e:
                print(f"[WATCHER] ✗ Error running sync: {e}")

def main():
    # Get paths
    core_dir = Path(__file__).parent
    tapestry_file = core_dir / 'tapestry.json'
    sync_script = core_dir / 'sync_to_webapp.py'

    if not tapestry_file.exists():
        print(f"[ERROR] tapestry.json not found at {tapestry_file}")
        return

    if not sync_script.exists():
        print(f"[ERROR] sync_to_webapp.py not found at {sync_script}")
        return

    print("=" * 60)
    print("TAPESTRY AUTO-SYNC WATCHER")
    print("=" * 60)
    print(f"Watching: {tapestry_file}")
    print(f"Sync script: {sync_script}")
    print("\nPress Ctrl+C to stop watching\n")
    print("=" * 60)

    # Set up file watcher
    event_handler = TapestryChangeHandler(str(sync_script))
    observer = Observer()
    observer.schedule(event_handler, str(core_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[WATCHER] Stopping...")
        observer.stop()

    observer.join()
    print("[WATCHER] Stopped")

if __name__ == '__main__':
    main()

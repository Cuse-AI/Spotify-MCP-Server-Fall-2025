"""
STAGGERED SCRAPE LAUNCHER
Launches metavibe scrapers with delays to avoid race conditions.

Usage:
    python staggered_launcher.py [target] [quota] [delay_seconds]
    
Example:
    python staggered_launcher.py 30 5000 10
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

METAVIBES = ["Chill", "Dark", "Drive", "Energy", "Happy", "Night", "Party", "Sad", "Uplifting"]

def check_api_keys():
    """Verify all 9 YouTube API keys are configured."""
    missing = []
    for mv in METAVIBES:
        key_name = f"YOUTUBE_API_KEY_{mv.upper()}"
        if not os.getenv(key_name):
            missing.append(key_name)
    
    if missing:
        print("[ERROR] Missing YouTube API keys:")
        for key in missing:
            print(f"  - {key}")
        sys.exit(1)
    
    print("[OK] All 9 YouTube API keys configured")

def launch_staggered(target: int = 30, max_quota: int = 5000, delay: int = 5, vibes_to_run: list = None):
    """Launch scrapers with staggered delays."""
    
    check_api_keys()
    
    script_dir = Path(__file__).parent
    scraper_path = script_dir / "metavibe_scraper.py"
    log_dir = script_dir / "output" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    vibes = vibes_to_run if vibes_to_run else METAVIBES
    
    print("=" * 70)
    print("STAGGERED SCRAPE LAUNCHER")
    print(f"Vibes: {', '.join(vibes)}")
    print(f"Target: {target} songs each | Quota: {max_quota} each")
    print(f"Delay between launches: {delay} seconds")
    print("=" * 70)
    
    processes = []
    
    for i, metavibe in enumerate(vibes):
        if i > 0:
            print(f"\n[WAITING {delay}s before next launch...]")
            time.sleep(delay)
        
        log_file = log_dir / f"{metavibe}_scrape.log"
        
        # Use shell=True and redirect within the command for better compatibility
        cmd = f'python "{scraper_path}" {metavibe} {target} {max_quota} > "{log_file}" 2>&1'
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(script_dir)
        )
        
        processes.append((metavibe, process, log_file))
        print(f"[LAUNCHED] {metavibe} (PID: {process.pid})")
    
    print("\n" + "=" * 70)
    print(f"All {len(vibes)} scrapers launched!")
    print("=" * 70)
    
    return processes

def wait_and_report(processes):
    """Wait for all processes and report results."""
    print("\nWaiting for scrapers to complete...")
    
    for metavibe, process, log_file in processes:
        process.wait()
        
        # Check if output file exists
        pipeline_dir = Path(__file__).parent.parent.parent / "data" / "pipeline" / "1_raw"
        output_files = list(pipeline_dir.glob(f"{metavibe}_*.json"))
        
        if output_files:
            latest = max(output_files, key=lambda f: f.stat().st_mtime)
            print(f"[DONE] {metavibe} -> {latest.name}")
        else:
            print(f"[WARN] {metavibe} - no output file found")
    
    print("\n[ALL COMPLETE]")

if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    max_quota = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    delay = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # Optional: specify which vibes to run
    # e.g., python staggered_launcher.py 30 5000 5 Night Party Sad Uplifting
    vibes_to_run = sys.argv[4:] if len(sys.argv) > 4 else None
    
    processes = launch_staggered(target, max_quota, delay, vibes_to_run)
    
    print("\nPress Enter to wait for completion, or Ctrl+C to let them run in background...")
    try:
        input()
        wait_and_report(processes)
    except KeyboardInterrupt:
        print("\n[Scrapers running in background]")

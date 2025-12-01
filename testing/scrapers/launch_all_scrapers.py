"""
PARALLEL SCRAPE LAUNCHER
Starts 9 metavibe scrapers simultaneously - one per meta-vibe!

Usage:
    python launch_all_scrapers.py [target_per_vibe] [max_quota_per_vibe]
    
Example:
    python launch_all_scrapers.py 50 8000
    
This will launch 9 separate Python processes, each scraping for their meta-vibe.
"""

import subprocess
import sys
import os
from pathlib import Path

METAVIBES = [
    "Chill",
    "Dark", 
    "Drive",
    "Energy",
    "Happy",
    "Night",
    "Party",
    "Sad",
    "Uplifting"
]

def launch_all(target: int = 50, max_quota: int = 8000):
    """Launch all 9 scrapers in parallel."""
    
    script_dir = Path(__file__).parent
    scraper_path = script_dir / "metavibe_scraper.py"
    
    print("="*70)
    print("PARALLEL SCRAPE LAUNCHER")
    print(f"Launching 9 scrapers: {target} songs each, {max_quota} quota each")
    print("="*70)
    
    processes = []
    log_files = []
    
    # Create logs directory
    log_dir = script_dir / "output" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    for metavibe in METAVIBES:
        log_file = log_dir / f"{metavibe}_scrape.log"
        
        # Open log file for writing
        log_handle = open(log_file, 'w', encoding='utf-8')
        log_files.append(log_handle)
        
        # Launch process
        cmd = [sys.executable, str(scraper_path), metavibe, str(target), str(max_quota)]
        
        process = subprocess.Popen(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            cwd=str(script_dir)
        )
        
        processes.append((metavibe, process))
        print(f"  [LAUNCHED] {metavibe} (PID: {process.pid}) -> {log_file.name}")
    
    print("\n" + "="*70)
    print("All 9 scrapers launched!")
    print("Monitor progress with: python check_scrape_status.py")
    print("="*70)
    
    return processes, log_files


def wait_for_all(processes, log_files):
    """Wait for all processes to complete."""
    print("\nWaiting for all scrapers to complete...")
    
    for metavibe, process in processes:
        process.wait()
        print(f"  [DONE] {metavibe} (exit code: {process.returncode})")
    
    # Close log files
    for lf in log_files:
        lf.close()
    
    print("\n[ALL COMPLETE]")


if __name__ == '__main__':
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    max_quota = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    processes, log_files = launch_all(target, max_quota)
    
    # Ask if user wants to wait
    print("\nProcesses are running in background.")
    print("You can close this window - scrapers will continue.")
    print("\nOr press Enter to wait for completion...")
    
    try:
        input()
        wait_for_all(processes, log_files)
    except KeyboardInterrupt:
        print("\n[Scrapers continue in background]")

"""
Check status of all running/completed metavibe scrapes.
Shows songs collected per meta-vibe and total progress.
"""

import json
from pathlib import Path
from datetime import datetime

METAVIBES = ["Chill", "Dark", "Drive", "Energy", "Happy", "Night", "Party", "Sad", "Uplifting"]

def check_status():
    output_dir = Path(__file__).parent / "output" / "metavibe_scrapes"
    log_dir = Path(__file__).parent / "output" / "logs"
    
    print("="*70)
    print("SCRAPE STATUS CHECK")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    total_songs = 0
    status_data = {}
    
    for metavibe in METAVIBES:
        # Count songs from all scrape files for this metavibe
        songs = 0
        latest_file = None
        
        for file in output_dir.glob(f"{metavibe}_*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    songs += data.get('total_songs', 0)
                    latest_file = file
            except:
                pass
        
        # Check if still running by looking at log file modification time
        log_file = log_dir / f"{metavibe}_scrape.log"
        status = "DONE"
        if log_file.exists():
            # Check if log was modified in last 30 seconds
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if (datetime.now() - mtime).seconds < 30:
                status = "RUNNING"
            
            # Check last line of log for completion
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if "[DONE]" in last_line:
                            status = "DONE"
                        elif "QUOTA" in last_line.upper():
                            status = "QUOTA HIT"
                        elif "ERROR" in last_line.upper():
                            status = "ERROR"
            except:
                pass
        
        status_data[metavibe] = {'songs': songs, 'status': status}
        total_songs += songs
        
        # Visual bar
        bar = '█' * (songs // 5) if songs > 0 else ''
        target_marker = '│' if songs < 100 else '✓'
        
        print(f"{metavibe:10} {songs:4} songs [{status:8}] {bar}{target_marker}")
    
    print("="*70)
    print(f"{'TOTAL':10} {total_songs:4} songs")
    print(f"Target: 900 minimum (100 per meta-vibe)")
    print(f"Progress: {total_songs}/900 ({100*total_songs/900:.1f}%)")
    print("="*70)
    
    return status_data

if __name__ == '__main__':
    check_status()

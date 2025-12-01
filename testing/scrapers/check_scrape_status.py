"""
Check status of all running/completed metavibe scrapes.
Shows songs collected per meta-vibe and total progress.
"""

import json
from pathlib import Path
from datetime import datetime

METAVIBES = ["Chill", "Dark", "Drive", "Energy", "Happy", "Night", "Party", "Sad", "Uplifting"]

def check_status():
    # Find project root (go up from testing/scrapers)
    project_root = Path(__file__).parent.parent.parent
    pipeline_dir = project_root / "data" / "pipeline" / "1_raw"
    log_dir = Path(__file__).parent / "output" / "logs"
    
    print("="*70)
    print("SCRAPE STATUS CHECK")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Pipeline: data/pipeline/1_raw/")
    print("="*70)
    
    total_songs = 0
    status_data = {}
    
    for metavibe in METAVIBES:
        # Count songs from all scrape files for this metavibe
        songs = 0
        
        if pipeline_dir.exists():
            for file in pipeline_dir.glob(f"{metavibe}_*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        songs += data.get('total_songs', 0)
                except:
                    pass
        
        # Check if still running by looking at log file modification time
        log_file = log_dir / f"{metavibe}_scrape.log"
        status = "PENDING"
        
        if log_file.exists():
            # Check if log was modified in last 60 seconds
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if (datetime.now() - mtime).seconds < 60:
                status = "RUNNING"
            else:
                status = "DONE"
            
            # Check last lines of log for completion status
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        last_lines = ''.join(lines[-5:])
                        if "[DONE]" in last_lines:
                            status = "DONE"
                        elif "QUOTA" in last_lines.upper():
                            status = "QUOTA HIT"
                        elif "ERROR" in last_lines.upper() or "Traceback" in last_lines:
                            status = "ERROR"
            except:
                pass
        
        if songs > 0 and status == "PENDING":
            status = "DONE"
        
        status_data[metavibe] = {'songs': songs, 'status': status}
        total_songs += songs
        
        # Visual bar (each █ = 5 songs)
        bar = '█' * min(songs // 5, 20) if songs > 0 else ''
        target_marker = ' ✓100' if songs >= 100 else f' →{100-songs}'
        
        status_color = {
            'RUNNING': '🔄',
            'DONE': '✅',
            'QUOTA HIT': '⚠️',
            'ERROR': '❌',
            'PENDING': '⏳'
        }.get(status, '❓')
        
        print(f"{status_color} {metavibe:10} {songs:4} songs {bar}{target_marker}")
    
    print("="*70)
    print(f"{'TOTAL':13} {total_songs:4} songs")
    print(f"\nTarget: 900 minimum (100 per meta-vibe)")
    pct = 100*total_songs/900 if total_songs > 0 else 0
    print(f"Progress: {total_songs}/900 ({pct:.1f}%)")
    
    # Show estimated time remaining
    if total_songs > 0:
        remaining = 900 - total_songs
        # At ~35 songs per vibe per day with 9 keys
        days_remaining = remaining / (35 * 9)
        print(f"Est. days to target: {days_remaining:.1f}")
    
    print("="*70)
    
    return status_data

if __name__ == '__main__':
    check_status()

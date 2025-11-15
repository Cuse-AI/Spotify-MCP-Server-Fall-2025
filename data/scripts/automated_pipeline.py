"""
AUTOMATED TAPESTRY PIPELINE
Monitors 1_raw_scrapes/ and automatically processes new files through the entire workflow:
1. Dedupe (→ 2_deduped/)
2. Ananki Analysis (→ 3_analyzed/mapped/)
3. Inject to Tapestry (→ 4_injected/)

Run this after scraping completes!
"""

import json
import os
import sys
import subprocess
from pathlib import Path
import time
import logging
from datetime import datetime

# Setup detailed logging
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

RAW_DIR = PROJECT_ROOT / '1_raw_scrapes'
DEDUPED_DIR = PROJECT_ROOT / '2_deduped'
ANALYZED_DIR = PROJECT_ROOT / '3_analyzed' / 'mapped'
INJECTED_DIR = PROJECT_ROOT / '4_injected'
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'

def run_command(cmd, desc):
    """Run a command and show output with detailed error logging"""
    logger.info(f"{'='*70}")
    logger.info(f"{desc}")
    logger.info(f"{'='*70}")
    logger.debug(f"Command: {cmd}")

    try:
        # Use Popen for real-time output streaming (no timeout - let Ananki run as long as needed)
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=SCRIPTS_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
            logger.info(line.rstrip())

        # Wait for completion
        returncode = process.wait()

        if returncode != 0:
            logger.error(f"Command failed with exit code {returncode}")
            return False

        logger.info(f"✓ {desc} completed successfully")
        return True

    except Exception as e:
        logger.error(f"Exception running command: {e}", exc_info=True)
        return False

def process_pipeline():
    logger.info("="*70)
    logger.info(" AUTOMATED TAPESTRY PIPELINE STARTING")
    logger.info("="*70)
    logger.info(f"Log file: {log_file}")

    try:
        # Find all files in 1_raw_scrapes/
        raw_files = list(RAW_DIR.glob('*.json'))

        if not raw_files:
            logger.info("No new files in 1_raw_scrapes/ - nothing to process!")
            return

        logger.info(f"Found {len(raw_files)} files to process:")
        for f in raw_files:
            logger.info(f"  - {f.name} ({f.stat().st_size} bytes)")

        logger.info("Starting automated processing...")

        # STEP 1: BATCH DEDUPE
        logger.info("\n" + "="*70)
        logger.info("STEP 1: BATCH DEDUPLICATION")
        logger.info("="*70)

        file_args = ' '.join([f'"{f}"' for f in raw_files])
        dedupe_cmd = f'python batch_dedupe_before_ananki.py {file_args}'

        if not run_command(dedupe_cmd, "Running batch deduplication"):
            logger.error("❌ Deduplication failed - STOPPING PIPELINE")
            return

    except Exception as e:
        logger.error(f"FATAL ERROR in pipeline initialization: {e}", exc_info=True)
        return
    
    # STEP 2: RUN ANANKI ON ALL DEDUPED FILES
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 2: TRUE ANANKI ANALYSIS")
        logger.info("="*70)

        deduped_files = list(DEDUPED_DIR.glob('*_DEDUPED.json'))
        logger.info(f"Found {len(deduped_files)} deduped files")

        # Filter to only files that need processing - check if NEWER than existing MAPPED versions
        need_ananki = []
        for f in deduped_files:
            mapped_file = ANALYZED_DIR / f"{f.stem}_CLAUDE_MAPPED.json"
            injected_file = INJECTED_DIR / f"{f.stem}_CLAUDE_MAPPED.json"

            # Check if ANY mapped version exists
            existing_mapped = None
            if mapped_file.exists():
                existing_mapped = mapped_file
                logger.debug(f"{f.name} - found existing mapped file")
            elif injected_file.exists():
                existing_mapped = injected_file
                logger.debug(f"{f.name} - found existing injected file")

            # If no mapped version exists, OR deduped file is NEWER, process it
            if existing_mapped is None:
                need_ananki.append(f)
                logger.info(f"  ✓ NEW: {f.name}")
            elif f.stat().st_mtime > existing_mapped.stat().st_mtime:
                # Deduped file is newer - this is fresh data!
                need_ananki.append(f)
                logger.info(f"  ✓ UPDATED (deduped file newer than mapped): {f.name}")
            else:
                logger.info(f"  ⊘ SKIP (already processed, mapped file is newer): {f.name}")

        if not need_ananki:
            logger.info("All deduped files already analyzed!")
        else:
            logger.info(f"\nRunning Ananki on {len(need_ananki)} files...")

            for i, f in enumerate(need_ananki, 1):
                logger.info(f"\n[{i}/{len(need_ananki)}] Processing {f.name}")
                ananki_cmd = f'python true_ananki_claude_api.py "{f}"'
                if not run_command(ananki_cmd, f"Analyzing {f.name}"):
                    logger.error(f"❌ Skipping {f.name} due to error")
                    continue

    except Exception as e:
        logger.error(f"FATAL ERROR in Ananki step: {e}", exc_info=True)
        return
    
    # STEP 3: INJECT TO TAPESTRY
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 3: INJECT TO TAPESTRY")
        logger.info("="*70)

        mapped_files = list(ANALYZED_DIR.glob('*_CLAUDE_MAPPED.json'))

        if not mapped_files:
            logger.warning("No mapped files found in 3_analyzed/mapped/")
            logger.warning("This means either:")
            logger.warning("  1. No files were successfully analyzed by Ananki")
            logger.warning("  2. Files were already injected previously")
            return

        logger.info(f"Injecting {len(mapped_files)} files to tapestry...")

        for i, f in enumerate(mapped_files, 1):
            logger.info(f"\n[{i}/{len(mapped_files)}] Injecting {f.name}")
            inject_cmd = f'python inject_to_tapestry.py "{f}"'
            if not run_command(inject_cmd, f"Injecting {f.name}"):
                logger.error(f"❌ Skipping {f.name} due to error")
                continue

            # Move to 4_injected/
            dest = INJECTED_DIR / f.name
            f.rename(dest)
            logger.info(f"✓ Moved to: {dest}")

            # Also move the ambiguous file if it exists
            ambig_file = f.parent.parent / 'ambiguous' / f"{f.stem.replace('_MAPPED', '_AMBIGUOUS')}.json"
            if ambig_file.exists():
                ambig_dest = INJECTED_DIR / ambig_file.name
                ambig_file.rename(ambig_dest)
                logger.debug(f"Moved ambiguous file: {ambig_file.name}")

    except Exception as e:
        logger.error(f"FATAL ERROR in injection step: {e}", exc_info=True)
        return

    # STEP 4: CLEANUP - Move raw files to archive
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 4: CLEANUP")
        logger.info("="*70)

        archive_dir = PROJECT_ROOT / 'archive' / 'processed_scrapes'
        archive_dir.mkdir(parents=True, exist_ok=True)

        for f in raw_files:
            if f.exists():  # Still exists (wasn't moved yet)
                dest = archive_dir / f.name
                f.rename(dest)
                logger.info(f"✓ Archived: {f.name}")

        # Move deduped files too
        for f in DEDUPED_DIR.glob('*.json'):
            if not f.name.endswith('_CHECKPOINT.json'):  # Keep checkpoints
                dest = archive_dir / f.name
                f.rename(dest)
                logger.debug(f"Archived deduped file: {f.name}")

    except Exception as e:
        logger.error(f"ERROR in cleanup step: {e}", exc_info=True)

    # FINAL STATS
    logger.info("\n" + "="*70)
    logger.info(" PIPELINE COMPLETE!")
    logger.info("="*70)

    try:
        tapestry_file = PROJECT_ROOT / 'core' / 'tapestry.json'
        if tapestry_file.exists():
            t = json.load(open(tapestry_file, encoding='utf-8'))
            total = sum(len(v['songs']) for v in t['vibes'].values())
            logger.info(f"\n✓ Tapestry now has: {total:,} songs!")
        logger.info(f"✓ Log saved to: {log_file}")
    except Exception as e:
        logger.error(f"ERROR reading final stats: {e}", exc_info=True)

if __name__ == '__main__':
    try:
        process_pipeline()
    except Exception as e:
        logger.error(f"CATASTROPHIC PIPELINE FAILURE: {e}", exc_info=True)
        sys.exit(1)

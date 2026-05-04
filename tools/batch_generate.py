#!/usr/bin/env python3
"""
Batch Generate Script - Process All YouTube Shorts with Parallel Support
Generates "The Twice-Crowned King" series with "Snippet Stories" branding

Usage (from project root):
    python tools/batch_generate.py
    python tools/batch_generate.py --threads 2
    python tools/batch_generate.py --start 10 --end 20
"""

import os
import subprocess
import time
import sys
import json
import argparse
import shutil
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Prevent Unicode errors on Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Project root is one level up from tools/
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from src import config
except ImportError:
    config = None

state_lock = threading.Lock()

def process_script(script_path, part_num, total, i, state, output_dir, state_file):
    script_name = script_path.name
    progress = f"[{i:3d}/{total}]"
    
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT)

        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "src" / "generate_short.py"), str(script_path), str(part_num)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=None,
            env=env,
            cwd=str(PROJECT_ROOT),
        )

        with state_lock:
            if result.returncode == 0:
                print(f"{progress} ✅ {script_name}")
                if script_name not in state["completed"]:
                    state["completed"].append(script_name)
                if script_name in state["failed"]:
                    state["failed"].remove(script_name)
                success = True
            else:
                print(f"{progress} ❌ {script_name} (non-zero exit)")
                if script_name not in state["failed"]:
                    state["failed"].append(script_name)
                success = False
            
            # Save state
            with open(state_file, "w") as f:
                json.dump(state, f, indent=4)
        
        return success

    except Exception as e:
        with state_lock:
            print(f"{progress} ❌ {script_name} ({str(e)[:40]})")
            if script_name not in state["failed"]:
                state["failed"].append(script_name)
            with open(state_file, "w") as f:
                json.dump(state, f, indent=4)
        return False

def main():
    parser = argparse.ArgumentParser(description="Batch generate YouTube Shorts")
    parser.add_argument("--start", type=int, default=1, help="Start part number")
    parser.add_argument("--end", type=int, default=None, help="End part number (inclusive)")
    parser.add_argument("--threads", type=int, default=None, help="Override parallel threads")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    input_dir = PROJECT_ROOT / "input"
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all part_XXXX.txt files
    script_files = sorted([f for f in input_dir.glob("part_*.txt")])

    if not script_files:
        print("❌ No scripts found in input/ directory")
        print("   Expected: input/part_0001.txt, part_0002.txt, etc.")
        sys.exit(1)

    # Filter by range
    if args.end:
        script_files = script_files[args.start - 1 : args.end]
    elif args.start > 1:
        script_files = script_files[args.start - 1 :]

    # --- State Management ---
    state_file = output_dir / "state.json"
    state = {"completed": [], "failed": []}
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except json.JSONDecodeError:
            pass

    # Filter out already completed scripts if we are resuming
    if not args.start > 1 and not args.end:
        script_files = [f for f in script_files if f.name not in state["completed"]]
        if not script_files:
            print("🎉 All scripts are already completed according to state.json!")
            sys.exit(0)
    
    total = len(script_files)
    num_threads = args.threads or getattr(config, 'MAX_THREADS', 1)
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     🎬 BATCH GENERATE — Snippet Stories YouTube Shorts       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"📝 Scripts to process: {total}")
    print(f"🧵 Parallel threads:  {num_threads}")
    print(f"⏱️  Estimated time: {total * 2.5 / (60 * num_threads):.1f} hours")
    print(f"🎬 Output folder: {output_dir.absolute()}")
    print()

    if not args.yes:
        response = input("Start batch generation? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("Cancelled.")
            sys.exit(0)

    print("\n🎬 Starting parallel generation...\n")

    start_time = time.time()
    
    # Run in parallel
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i, script_path in enumerate(script_files, 1):
            try:
                part_num = int(script_path.stem.split('_')[-1])
            except ValueError:
                part_num = i
            
            futures.append(executor.submit(
                process_script, script_path, part_num, total, i, state, output_dir, state_file
            ))
        
        # Wait for all to complete
        results = [f.result() for f in futures]

    success_count = sum(1 for r in results if r)
    error_count = total - success_count

    # Summary
    elapsed = time.time() - start_time
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                    BATCH GENERATION COMPLETE                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    print(f"✅ Success: {success_count}/{total}")
    print(f"❌ Failed:  {error_count}/{total}")
    print(f"⏱️  Time: {elapsed/3600:.2f} hours ({elapsed/60:.0f} minutes)")
    print()

    if state["failed"]:
        print("Failed scripts:")
        for script in state["failed"][:10]:
            print(f"  - {script}")
        if len(state["failed"]) > 10:
            print(f"  ... and {len(state['failed']) - 10} more")

    print(f"\n📂 Videos saved to: {output_dir}")

    if success_count == total and error_count == 0:
        print("🎉 ALL VIDEOS GENERATED SUCCESSFULLY!")
    elif error_count > 0:
        print(f"⚠️  {error_count} videos failed. Resume batch later or retry failed parts individually.")


if __name__ == "__main__":
    main()

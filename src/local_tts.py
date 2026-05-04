#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  LOCAL_TTS.PY — Kokoro & XTTSv2 Python Integration
#  High-emotion voice cloning & local inference
# ═══════════════════════════════════════════════════════════════

import os
import json
import logging
import subprocess
import sys
import threading
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

sys_path = Path(__file__).parent.parent
try:
    from src import config
except ImportError:
    import config

# Lazy load TTS modules
_kokoro_pipeline = None
_kokoro_worker_process = None
_kokoro_worker_lock = threading.Lock()


def _get_kokoro_worker_script() -> Path:
    return config.BASE_DIR / "src" / "kokoro_worker.py"


def _get_kokoro_runtime_python() -> Path:
    """Return the dedicated Kokoro runtime interpreter if it exists."""
    kokoro_python = config.BASE_DIR / ".kokoro_venv" / "Scripts" / "python.exe"
    if kokoro_python.exists():
        return kokoro_python
    return Path(sys.executable)


def _run_external_kokoro(text: str, voice: str, speed: float, output_path: str) -> float:
    """Synthesize audio in the dedicated Kokoro runtime worker and return duration in seconds."""
    runtime_python = _get_kokoro_runtime_python()
    worker_script = _get_kokoro_worker_script()

    if not runtime_python.exists() or not worker_script.exists():
        raise FileNotFoundError("Kokoro runtime worker is not available")

    return _send_kokoro_worker_request(runtime_python, worker_script, text, voice, speed, output_path)


def _start_kokoro_worker(runtime_python: Path, worker_script: Path) -> subprocess.Popen:
    logger.info(f"   🚀 Starting Kokoro worker: {runtime_python}")
    proc = subprocess.Popen(
        [str(runtime_python), "-u", str(worker_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    logger.info(f"   🚀 Kokoro worker started (PID: {proc.pid})")
    
    # Start a thread to log stderr from the worker
    def log_stderr(pipe):
        for line in pipe:
            try:
                line_str = line.decode('utf-8').strip()
                if line_str:
                    logger.debug(f"   [Kokoro Worker] {line_str}")
            except:
                pass
    
    threading.Thread(target=log_stderr, args=(proc.stderr,), daemon=True).start()
    
    return proc


def _read_line_with_timeout(stream, timeout_seconds: int) -> str:
    container = {"line": None}

    def reader():
        line = stream.readline()
        if isinstance(line, bytes):
            line = line.decode('utf-8')
        container["line"] = line

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout_seconds)
    if thread.is_alive():
        raise TimeoutError(f"Kokoro worker did not respond within {timeout_seconds}s")

    return container["line"] or ""


def _send_kokoro_worker_request(
    runtime_python: Path,
    worker_script: Path,
    text: str,
    voice: str,
    speed: float,
    output_path: str,
) -> float:
    global _kokoro_worker_process

    request = json.dumps(
        {
            "action": "synthesize",
            "text": text,
            "voice": voice,
            "speed": speed,
            "output_path": output_path,
        },
        ensure_ascii=False,
    )

    with _kokoro_worker_lock:
        if _kokoro_worker_process is None or _kokoro_worker_process.poll() is not None:
            logger.info("   🔄 Initializing Kokoro worker (first request — model loading may take ~30s)...")
            _kokoro_worker_process = _start_kokoro_worker(runtime_python, worker_script)
            # Wait for the worker to be ready (model load takes time)
            # Read any initial output lines until we get a response or timeout
            try:
                # Give the model up to 120s to load on first start
                res = _read_line_with_timeout(_kokoro_worker_process.stdout, timeout_seconds=120)
                if res and 'ready' in res:
                    logger.info('   ✔ Kokoro worker ready')
                else:
                    logger.error(f"❌ Kokoro worker failed to start correctly: {res}")
                    _kokoro_worker_process.kill()
                    _kokoro_worker_process = None
                    raise RuntimeError(f"Kokoro worker initialization failed: {res}")
            except TimeoutError:
                logger.warning("⚠️  Kokoro worker timed out during initialization.")
                _kokoro_worker_process.kill()
                _kokoro_worker_process = None
                raise RuntimeError("Kokoro worker initialization timed out")

        if _kokoro_worker_process.stdin is None or _kokoro_worker_process.stdout is None:
            raise RuntimeError("Kokoro worker streams are unavailable")

        _kokoro_worker_process.stdin.write((request + "\n").encode('utf-8'))
        _kokoro_worker_process.stdin.flush()

        response = None
        for _ in range(3):
            response_line = _read_line_with_timeout(_kokoro_worker_process.stdout, timeout_seconds=900)
            if not response_line:
                continue
            try:
                response = json.loads(response_line)
            except json.JSONDecodeError:
                continue
            if response.get("status") == "ready":
                response = None
                continue
            break

        if not response:
            raise RuntimeError("Kokoro worker returned no usable response")

        if response.get("status") != "success":
            raise RuntimeError(response.get("error", "Unknown Kokoro worker error"))

        return float(response["duration"])

def _get_kokoro_pipeline():
    global _kokoro_pipeline
    if _kokoro_pipeline is None:
        try:
            from kokoro import KPipeline
            # Default to American English voicepack pipeline
            _kokoro_pipeline = KPipeline(lang_code='a')
            logger.info("✅ Kokoro TTS Pipeline initialized locally.")
        except ImportError:
            logger.error("❌ Kokoro TTS not installed. Run: pip install kokoro soundfile torch")
            raise
    return _kokoro_pipeline

def generate_kokoro_audio(
    text: str,
    voice: str,
    speed: float,
    output_path: str
) -> List[Dict]:
    """
    Generates high-emotion TTS using local Kokoro-TTS.
    Since Kokoro doesn't output precise word-level offset timings natively,
    we approximate the word timings proportionally based on audio duration.
    Our librosa onset detector in generate_short.py will frame-perfect sync them.
    
    Args:
        text: Input dialogue
        voice: Kokoro voicepack name (e.g. 'af_bella')
        speed: Speed multiplier
        output_path: Where to save the .wav
        
    Returns:
        List of pseudo-timings (word, start, end)
    """
    import soundfile as sf
    import numpy as np
    
    runtime_python = _get_kokoro_runtime_python()

    # Use the dedicated Kokoro runtime worker when available so the main generator can stay on Python 3.13.
    if runtime_python != Path(sys.executable) and runtime_python.exists() and _get_kokoro_worker_script().exists():
        total_duration = _run_external_kokoro(text, voice, speed, output_path)
    else:
        pipeline = _get_kokoro_pipeline()

        # Generate audio inline as a fallback when a compatible runtime is available in-process.
        generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')

        full_audio = []
        sample_rate = 24000

        for _, _, audio in generator:
            if audio is not None:
                full_audio.append(audio)

        if not full_audio:
            logger.warning("⚠️ Kokoro generated empty audio.")
            return []

        final_audio = np.concatenate(full_audio)
        sf.write(output_path, final_audio, sample_rate)
        total_duration = len(final_audio) / sample_rate
    
    # Calculate pseudo word timings for standard subtitle fallbacks
    # (Librosa `onset_detect` overrides this for the frame-perfect system)
    words = text.split()
    timings = []
    
    # Calculate pseudo word timings weighted by character length and punctuation
    if words:
        # Calculate total weight
        total_weight = 0.0
        weights = []
        for w in words:
            # Base weight = length of word
            weight = max(1, len(w))
            # Add extra weight (pause) for punctuation
            if w.endswith(('.', '!', '?')):
                weight += 4  # ~400ms pause equivalent
            elif w.endswith((',', ';', ':')):
                weight += 2  # ~200ms pause equivalent
            weights.append(weight)
            total_weight += weight
        
        # Distribute time proportionally
        curr_time = 0.0
        for i, w in enumerate(words):
            dur = (weights[i] / total_weight) * total_duration
            timings.append({
                "word": w,
                "start": curr_time,
                "end": curr_time + dur
            })
            curr_time += dur
            
    return timings

def generate_xtts_audio(*args, **kwargs):
    """Placeholder for Coqui XTTSv2 integration."""
    logger.info("   ⏭ XTTSv2 not implemented - skipping")
    return []

#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  AUDIO_PROCESSOR.PY — Character-specific audio post-processing
#  Applies unique EQ, reverb, and spatial effects per character
# ═══════════════════════════════════════════════════════════════

import subprocess
import os
import sys
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Handle both direct and module execution
sys.path.insert(0, str(Path(__file__).parent))
try:
    from . import config
except ImportError:
    import config


def apply_character_fx(
    input_audio: str,
    output_audio: str,
    character: str,
) -> str:
    """
    Apply character-specific audio effects to a TTS segment.

    Args:
        input_audio: Path to raw TTS audio file
        output_audio: Path to save processed audio
        character: Character name (maps to config.CHARACTER_AUDIO_FX)

    Returns:
        Path to processed audio file
    """
    if not config.CHARACTER_AUDIO_FX_ENABLED:
        return input_audio

    fx_chain = config.CHARACTER_AUDIO_FX.get(
        character,
        config.CHARACTER_AUDIO_FX.get("_default", "highpass=f=80")
    )
    
    # UPGRADE: Add voice compression/compand for "Emotional Vox"
    # This makes the voice sound more present and professional
    if getattr(config, 'VOICE_COMPRESSION', False):
        compand_val = getattr(config, 'VOICE_COMPAND_STRENGTH', "0.02,0.1 6:-60,-90,-15,-6 -12 -90 0.1")
        fx_chain = f"{fx_chain},compand={compand_val}"

    cmd = [
        "ffmpeg", "-y", "-i", input_audio,
        "-af", fx_chain,
        output_audio
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.warning(
            f"⚠️  Audio FX failed for '{character}', using raw audio"
        )
        return input_audio

    return output_audio


def normalize_audio(input_path: str, output_path: str, target_lufs: float = -14) -> str:
    """
    Normalize audio to YouTube standard loudness (-14 LUFS).

    Args:
        input_path: Input audio file
        output_path: Output normalized audio file
        target_lufs: Target loudness in LUFS (YouTube standard: -14)

    Returns:
        Path to normalized audio
    """
    # First pass: measure loudness
    cmd_measure = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]

    result = subprocess.run(cmd_measure, capture_output=True, text=True)

    # Try to extract loudnorm parameters from stderr
    try:
        # Find the JSON block in stderr
        stderr = result.stderr
        json_start = stderr.rfind("{")
        json_end = stderr.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            import json
            params = json.loads(stderr[json_start:json_end])

            input_i = params.get("input_i", "-24")
            input_tp = params.get("input_tp", "-1.5")
            input_lra = params.get("input_lra", "11")
            input_thresh = params.get("input_thresh", "-34")

            # Second pass: apply normalization
            af = (
                f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:"
                f"measured_I={input_i}:measured_TP={input_tp}:"
                f"measured_LRA={input_lra}:measured_thresh={input_thresh}:"
                f"linear=true"
            )

            cmd_apply = [
                "ffmpeg", "-y", "-i", input_path,
                "-af", af,
                output_path
            ]

            r2 = subprocess.run(cmd_apply, capture_output=True, text=True)
            if r2.returncode == 0:
                return output_path
    except Exception as e:
        logger.debug(f"Loudnorm parsing failed: {e}")

    # Simple fallback: just copy with basic volume normalization
    cmd_simple = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", "volume=0dB",
        output_path
    ]
    r = subprocess.run(cmd_simple, capture_output=True, text=True)
    return output_path if r.returncode == 0 else input_path


def mix_with_ducking(
    voice_path: str,
    music_path: str,
    output_path: str,
    voice_volume: float = 1.0,
    music_volume: float = 0.10,
) -> str:
    """
    Mix voice and background music with dynamic ducking.
    Music volume drops when voice is present, rises during silences.

    Args:
        voice_path: Path to voice audio
        music_path: Path to background music
        output_path: Path to output mixed audio
        voice_volume: Voice volume (0.0-1.0)
        music_volume: Base music volume (0.0-1.0)

    Returns:
        Path to mixed audio
    """
    if not music_path or not os.path.exists(music_path):
        return voice_path

    # Sidechain-style ducking using FFmpeg's sidechaincompress
    filter_complex = (
        f"[0:a]volume={voice_volume}[voice];"
        f"[1:a]volume={music_volume}[music];"
        f"[music][voice]sidechaincompress="
        f"threshold=0.02:ratio=6:attack=50:release=300:level_sc=1[ducked];"
        f"[voice][ducked]amix=inputs=2:weights=1 1:duration=first[out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path,
        "-i", music_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", config.AUDIO_CODEC,
        "-b:a", config.AUDIO_BITRATE,
        "-ar", config.AUDIO_SAMPLE_RATE,
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.warning("⚠️  Ducking mix failed → simple mix fallback")
        return _simple_mix(voice_path, music_path, output_path, music_volume)

    logger.info("   ✅ Audio mixed with dynamic ducking")
    return output_path


def _simple_mix(
    voice_path: str,
    music_path: str,
    output_path: str,
    music_volume: float = 0.10,
) -> str:
    """Simple audio mix without ducking (fallback)."""
    wt = str(1 - music_volume)
    mv = str(music_volume)

    cmd = [
        "ffmpeg", "-y",
        "-i", voice_path, "-i", music_path,
        "-filter_complex",
        f"[0:a][1:a]amix=inputs=2:weights={wt} {mv}:duration=first",
        "-c:a", config.AUDIO_CODEC,
        "-b:a", config.AUDIO_BITRATE,
        output_path
    ]

    r = subprocess.run(cmd, capture_output=True, text=True)
    return output_path if r.returncode == 0 else voice_path


def apply_mood_shaping(audio_path: str, mood: str, output_path: str) -> str:
    """
    Applies high-end cinematic EQ and vocal shaping based on segment mood.
    Ensures high-immersion through frequency balancing.
    """
    # Base filter: High-quality normalization + crystal clear presence
    base_fx = "highpass=f=80,equalizer=f=350:t=q:w=1:g=-2,highshelf=f=4000:g=2"
    
    # Mood-specific modifiers for Cinematic Presence (Keeping it ultra-smooth)
    mood_eq = {
        "epic":    f"{base_fx},equalizer=f=120:t=q:w=1:g=2,aecho=0.8:0.88:40:0.1,highshelf=f=5000:g=2",
        "dark":    f"{base_fx},equalizer=f=80:t=q:w=1:g=3,aecho=0.8:0.9:60:0.1",
        "sad":     f"{base_fx},equalizer=f=400:t=q:w=1:g=-2,aecho=0.8:0.7:100:0.05",
        "mysterious": f"{base_fx},aecho=0.8:0.8:150:0.2",
        "aggressive": f"{base_fx},equalizer=f=2500:t=q:w=1:g=2,volume=1.1",
        "thrill":  f"{base_fx},aecho=0.8:0.8:20:0.1,volume=1.05",
        "neutral": f"{base_fx},equalizer=f=200:t=q:w=1:g=1"
    }
    
    filter_str = mood_eq.get(mood.lower(), base_fx)
    
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-af", filter_str,
        "-c:a", "pcm_s16le",
        output_path
    ]
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return output_path if r.returncode == 0 else audio_path
    except Exception as e:
        print(f"ERROR in apply_mood_shaping: {e}")
        return audio_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Audio processor module loaded")
    print("   Character FX available for:")
    for char in config.CHARACTER_AUDIO_FX:
        print(f"      {char}")
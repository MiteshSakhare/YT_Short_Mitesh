#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  SFX_ENGINE.PY — Sound Effects Generator & Manager
#  Generates mood-based SFX using FFmpeg audio synthesis
#  No external files needed — all SFX created programmatically
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

# ─────────────────────────────────────────────────────────────
#  SFX DEFINITIONS (generated via FFmpeg)
# ─────────────────────────────────────────────────────────────

SFX_RECIPES = {
    # ── Transition SFX ────────────────────────────────────────
    "whoosh": {
        "desc": "Fast swoosh transition",
        "duration": 0.8,
        "aevalsrc": "'0.6*sin(2*PI*(400+4000*t)*t)*exp(-4*t)'",
        "filter": "bandpass=f=2500:w=3000,afade=t=out:st=0.5:d=0.3",
    },
    "whoosh_soft": {
        "desc": "Gentle transition whoosh",
        "duration": 0.6,
        "aevalsrc": "'0.4*sin(2*PI*(500+2500*t)*t)*exp(-5*t)'",
        "filter": "bandpass=f=1800:w=2000,afade=t=out:st=0.3:d=0.3",
    },

    # ── Dramatic SFX ──────────────────────────────────────────
    "boom": {
        "desc": "Deep dramatic boom/impact with mid-range crunch",
        "duration": 1.5,
        "aevalsrc": "'0.7*sin(2*PI*60*t)*exp(-2*t)+0.4*sin(2*PI*200*t)*exp(-4*t)+0.2*(random(0)-0.5)*exp(-10*t)'",
        "filter": "lowpass=f=800,afade=t=out:st=0.8:d=0.7",
    },
    "stinger": {
        "desc": "Dramatic reveal stinger",
        "duration": 1.2,
        "aevalsrc": ("'0.5*sin(2*PI*440*t)*exp(-3*t)"
                     "+0.4*sin(2*PI*660*t)*exp(-4*t)"
                     "+0.3*sin(2*PI*880*t)*exp(-5*t)'"),
        "filter": "lowpass=f=4000,afade=t=in:d=0.05,afade=t=out:st=0.6:d=0.6",
    },
    "sub_drop": {
        "desc": "Sub bass drop (vine boom style) with mid presence",
        "duration": 1.0,
        "aevalsrc": "'0.8*sin(2*PI*(300-150*t)*t)*exp(-2*t)+0.3*sin(2*PI*(600-300*t)*t)*exp(-3*t)'",
        "filter": "lowpass=f=600,afade=t=out:st=0.5:d=0.5",
    },
    "sharp_hit": {
        "desc": "High frequency sharp impact",
        "duration": 0.5,
        "aevalsrc": "'0.8*(random(0)-0.5)*exp(-15*t)+0.5*sin(2*PI*1000*t)*exp(-20*t)'",
        "filter": "highpass=f=500,afade=t=out:st=0.1:d=0.4",
    },

    # ── Emotional / Nature SFX ─────────────────────────────────────────
    "sad_tone": {
        "desc": "Melancholic single note",
        "duration": 2.5,
        "aevalsrc": "'0.4*sin(2*PI*392.0*t)*exp(-0.8*t)+0.25*sin(2*PI*523.25*t)*exp(-1*t)'",
        "filter": "lowpass=f=3000,afade=t=in:d=0.3,afade=t=out:st=1.5:d=1.0",
    },
    "tension_rise": {
        "desc": "Rising tension sweep",
        "duration": 2.0,
        "aevalsrc": "'0.4*sin(2*PI*(300+800*t/2)*t)*exp(-0.5*t)'",
        "filter": "bandpass=f=1200:w=1000,afade=t=in:d=0.2,afade=t=out:st=1.5:d=0.5",
    },
    "heartbeat": {
        "desc": "Rhythmic heartbeat thump with mid click",
        "duration": 3.0,
        "aevalsrc": ("'0.6*sin(2*PI*80*t)*(exp(-15*mod(t,0.8))"
                     "+0.7*exp(-15*max(0,mod(t,0.8)-0.15)))"
                     "+0.2*(random(0)-0.5)*(exp(-30*mod(t,0.8)))'"),
        "filter": "lowpass=f=600,volume=1.5",
    },
    "wind_howl": {
        "desc": "Spooky nature wind howl",
        "duration": 4.0,
        "aevalsrc": "'0.3*(random(0)-0.5)*sin(2*PI*(300+100*sin(2*PI*0.5*t))*t)'",
        "filter": "bandpass=f=800:w=400,afade=t=in:d=1.0,afade=t=out:st=2.5:d=1.5",
    },

    # ── Magic/Mystery SFX ─────────────────────────────────────
    "magic_chime": {
        "desc": "Magical shimmer chime",
        "duration": 1.5,
        "aevalsrc": ("'0.3*sin(2*PI*1760*t)*exp(-3*t)"
                     "+0.2*sin(2*PI*2640*t)*exp(-4*t)"
                     "+0.15*sin(2*PI*3520*t)*exp(-5*t)'"),
        "filter": "aecho=0.6:0.3:50:0.3,highpass=f=800,afade=t=out:st=0.8:d=0.7",
    },
    "whisper_echo": {
        "desc": "Eerie whisper/wind effect",
        "duration": 2.0,
        "aevalsrc": "'0.25*(random(0)-0.5)*sin(2*PI*400*t)*exp(-1*t)'",
        "filter": "bandpass=f=1200:w=800,aecho=0.8:0.7:100:0.5,afade=t=out:st=1.2:d=0.8",
    },
    "ethereal_choir": {
        "desc": "Ethereal angelic choir tone",
        "duration": 3.0,
        "aevalsrc": "'0.2*sin(2*PI*523.25*t)*exp(-0.2*t)+0.2*sin(2*PI*659.25*t)*exp(-0.2*t)+0.2*sin(2*PI*783.99*t)*exp(-0.2*t)'",
        "filter": "aecho=0.8:0.6:150:0.5,afade=t=in:d=0.5,afade=t=out:st=2.0:d=1.0",
    },

    # ── Action/Combat/Nature SFX ─────────────────────────────────────
    "blade_clash": {
        "desc": "Metallic sword clash",
        "duration": 0.8,
        "aevalsrc": "'0.5*sin(2*PI*(1200+600*t)*t)*exp(-10*t)+0.3*random(0)*exp(-20*t)'",
        "filter": "highpass=f=1500,aecho=0.8:0.5:20:0.3,afade=t=out:st=0.3:d=0.4",
    },
    "magic_surge": {
        "desc": "Pulsing arcane energy surge",
        "duration": 2.0,
        "aevalsrc": "'0.4*sin(2*PI*(200+800*sin(2*PI*2*t))*t)*exp(-0.5*t)'",
        "filter": "aphaser=speed=2:decay=0.6,aecho=0.8:0.8:150:0.5,lowpass=f=4000,afade=t=out:st=1.0:d=1.0",
    },

    # ── Battle/Epic SFX ───────────────────────────────────────
    "thunder": {
        "desc": "Thunder crack",
        "duration": 2.0,
        "aevalsrc": "'0.9*(random(0)-0.5)*exp(-4*t)+0.5*sin(2*PI*120*t)*exp(-2*t)'",
        "filter": "lowpass=f=2000,afade=t=out:st=1.0:d=1.0",
    },
    "distant_thunder": {
        "desc": "Rumbling distant thunder",
        "duration": 3.0,
        "aevalsrc": "'0.5*(random(0)-0.5)*exp(-1.5*t)+0.4*sin(2*PI*80*t)*exp(-1*t)'",
        "filter": "lowpass=f=400,afade=t=in:d=0.5,afade=t=out:st=1.5:d=1.5",
    },
    "sword_ring": {
        "desc": "Metallic sword ring",
        "duration": 1.0,
        "aevalsrc": ("'0.5*sin(2*PI*3000*t)*exp(-8*t)"
                     "+0.4*sin(2*PI*4500*t)*exp(-10*t)"
                     "+0.3*sin(2*PI*6000*t)*exp(-12*t)'"),
        "filter": "highpass=f=1000,aecho=0.6:0.4:20:0.2,afade=t=out:st=0.4:d=0.6",
    },

    # ── Surprise/Reveal SFX ───────────────────────────────────
    "gasp_effect": {
        "desc": "Sharp inhale/gasp sound effect",
        "duration": 0.6,
        "aevalsrc": "'0.3*(random(0)-0.5)*exp(-6*t)'",
        "filter": "bandpass=f=2000:w=3000,afade=t=in:d=0.05,afade=t=out:st=0.3:d=0.3",
    },
    "reveal": {
        "desc": "Dramatic reveal hit",
        "duration": 1.5,
        "aevalsrc": ("'0.6*sin(2*PI*110*t)*exp(-2*t)"
                     "+0.4*sin(2*PI*220*t)*exp(-3*t)"
                     "+0.3*(random(0)-0.5)*exp(-4*t)'"),
        "filter": "lowpass=f=1500,afade=t=out:st=0.8:d=0.7",
    },
    "soul_echo": {
        "desc": "Deep ethereal soul effect",
        "duration": 2.5,
        "aevalsrc": "'0.2*sin(2*PI*50*t)*exp(-0.5*t)+0.1*sin(2*PI*100*t)*exp(-1*t)'",
        "filter": "aecho=0.8:0.88:200:0.6,lowpass=f=500,afade=t=out:st=1.5:d=1.0",
    },
    "magic_flare": {
        "desc": "Brilliant arcane flare",
        "duration": 1.8,
        "aevalsrc": "'0.3*sin(2*PI*(440+880*t)*t)*exp(-2*t)'",
        "filter": "aphaser=speed=2:decay=0.8,highpass=f=800,afade=t=out:st=1.0:d=0.8",
    },
    # ── New Story-Specific SFX ────────────────────────────────
    "ancient_seal": {
        "desc": "Resonant metallic seal activation",
        "duration": 2.0,
        "aevalsrc": "'0.5*sin(2*PI*440*t)*exp(-1.5*t)+0.3*sin(2*PI*880*t)*exp(-3*t)'",
        "filter": "aecho=0.8:0.7:100:0.5,lowpass=f=3000,afade=t=out:st=1.0:d=1.0",
    },
    "demon_pulse": {
        "desc": "Low demonic rumble pulse (mid-range for mobile)",
        "duration": 2.5,
        "aevalsrc": "'0.6*sin(2*PI*300*t)*(1+0.4*sin(2*PI*8*t))*exp(-0.5*t)'",
        "filter": "lowpass=f=800,vibrato=f=8:d=0.5,afade=t=out:st=1.5:d=1.0",
    },
    "void_hum": {
        "desc": "Deep unsettling void ambience",
        "duration": 3.0,
        "aevalsrc": "'0.2*random(0)*exp(-0.2*t)+0.1*sin(2*PI*400*t)'",
        "filter": "bandpass=f=600:w=200,aecho=0.8:0.9:250:0.4,afade=t=in:d=0.5,afade=t=out:st=2.0:d=1.0",
    },
    "holy_radiance": {
        "desc": "Shimmering divine light",
        "duration": 2.5,
        "aevalsrc": "'0.15*sin(2*PI*1760*t)*exp(-0.5*t)+0.1*sin(2*PI*2637*t)*exp(-0.8*t)'",
        "filter": "aecho=0.8:0.6:50:0.3,highpass=f=1000,afade=t=in:d=0.4,afade=t=out:st=1.5:d=1.0",
    },
}

# Mood → which SFX to use for transitions and accents
MOOD_SFX_MAP = {
    "dark":      {"transition": "whoosh",       "accent": "distant_thunder"},
    "sad":       {"transition": "whoosh_soft",  "accent": "sad_tone"},
    "thrill":    {"transition": "whoosh",       "accent": "heartbeat"},
    "happy":     {"transition": "whoosh_soft",  "accent": "holy_radiance"},
    "epic":      {"transition": "whoosh",       "accent": "thunder"},
    "surprise":  {"transition": "whoosh",       "accent": "sharp_hit"},
    "mystery":   {"transition": "whoosh_soft",  "accent": "wind_howl"},
    "neutral":   {"transition": "whoosh_soft",  "accent": "stinger"},
}


def generate_sfx(name: str, output_path: str) -> Optional[str]:
    """Generate a single SFX file using FFmpeg synthesis."""
    recipe = SFX_RECIPES.get(name)
    if not recipe:
        logger.warning(f"Unknown SFX: {name}")
        return None

    # Check cache
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
        return output_path

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"aevalsrc={recipe['aevalsrc']}:s=44100:c=mono",
        "-t", str(recipe["duration"]),
        "-af", recipe["filter"],
        "-c:a", "pcm_s16le",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"SFX generation failed for {name}: {result.stderr[-200:]}")
        return None

    logger.debug(f"   🔊 SFX generated: {name} → {output_path}")
    return output_path


def generate_all_sfx(sfx_dir: Path) -> dict:
    """Pre-generate all SFX files. Returns dict of name → path."""
    sfx_dir.mkdir(exist_ok=True)
    paths = {}

    for name in SFX_RECIPES:
        out = str(sfx_dir / f"{name}.wav")
        result = generate_sfx(name, out)
        if result:
            paths[name] = result

    logger.info(f"✅ SFX library ready — {len(paths)} effects generated")
    return paths


def get_mood_sfx(mood: str, sfx_dir: Path) -> dict:
    """
    Get SFX file paths for a given mood.
    Returns: {"transition": path, "accent": path}
    """
    mapping = MOOD_SFX_MAP.get(mood, MOOD_SFX_MAP["neutral"])
    result = {}

    for role, sfx_name in mapping.items():
        path = str(sfx_dir / f"{sfx_name}.wav")
        if not os.path.exists(path):
            generate_sfx(sfx_name, path)
        if os.path.exists(path):
            result[role] = path

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sfx_dir = Path("./sfx")
    paths = generate_all_sfx(sfx_dir)
    for name, path in paths.items():
        size = os.path.getsize(path) / 1024
        print(f"  {name:20s} → {size:.1f} KB")
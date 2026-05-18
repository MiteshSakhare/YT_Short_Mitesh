#!/usr/bin/env python3
import math
import subprocess
import os
import sys
import json
import hashlib
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)
# ─────────────────────────────────────────────────────────────
#  LOCAL IMPORTS & ENVIRONMENT SETUP
# ─────────────────────────────────────────────────────────────
_src_dir = str(Path(__file__).parent.absolute())
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# Initialize config as None to prevent NameError
config = None

try:
    import config
except (ImportError, ModuleNotFoundError):
    try:
        from src import config
    except ImportError:
        try:
            # Absolute fallback
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import config
        except ImportError as e:
            print(f"CRITICAL: background_engine failed to import config: {e}")
            raise

FADE_DUR = getattr(config, 'SCENE_TRANSITION_DUR', 1.2)  # Transition overlap duration (seconds)
LOOP_FADE = getattr(config, 'LOOP_CROSSFADE_DUR', 1.2)


def _proc_solid_color(mood: str, duration: float, out: str) -> bool:
    """Generate a simple solid dark grey background for Tier 0 (No BS mode)."""
    logger.info("   ⬛ Generating solid color background…")
    
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x111111:s={config.VID_WIDTH}x{config.VID_HEIGHT}",
        "-t", str(duration), "-r", str(config.VID_FPS),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0
    except Exception as e:
        logger.error(f"Failed to generate solid background: {e}")
        return False

# ═══════════════════════════════════════════════════════════════
#  TIER 1: PROCEDURAL BACKGROUNDS (FFmpeg)
# ═══════════════════════════════════════════════════════════════

def _proc_plasma_dark(duration: float, out: str) -> bool:
    """Dark purple swirling plasma — great for dark/mystery moods."""
    logger.info("   🎨 Generating dark plasma background…")
    # Use cellular automata with dark fantasy color grading
    life_filter = (
        f"life=size={config.VID_WIDTH}x{config.VID_HEIGHT}:rate={config.VID_FPS}:"
        f"death_color=0x080012:life_color=0x5500aa:mold=80:random_fill_ratio=0.04"
    )
    color_filter = (
        f"scale={config.VID_WIDTH}:{config.VID_HEIGHT},"
        f"colorbalance=bs=0.3:bm=0.2:bh=0.15:rs=-0.15:rm=-0.08,"
        f"curves=r='0/0 0.4/0.12 1/0.5':g='0/0 0.4/0.08 1/0.4':b='0/0 0.4/0.35 1/0.9',"
        f"eq=brightness=-0.1:contrast=1.2:saturation=1.6,"
        f"vignette=PI/3.5,"
        f"gblur=sigma=2"
    )
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", life_filter,
        "-vf", color_filter, "-t", str(duration),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _proc_particles_fire(duration: float, out: str) -> bool:
    """Floating fire ember particles on dark background."""
    logger.info("   🔥 Generating fire particles background…")
    life_filter = (
        f"life=size={config.VID_WIDTH}x{config.VID_HEIGHT}:rate={config.VID_FPS}:"
        f"death_color=0x0a0000:life_color=0xff4400:mold=40:random_fill_ratio=0.02"
    )
    color_filter = (
        f"scale={config.VID_WIDTH}:{config.VID_HEIGHT},"
        f"colorbalance=rs=0.3:rm=0.15:rh=0.1:bs=-0.2:bm=-0.15,"
        f"eq=brightness=-0.12:contrast=1.3:saturation=2.0,"
        f"vignette=PI/3,"
        f"gblur=sigma=3"
    )
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", life_filter,
        "-vf", color_filter, "-t", str(duration),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _proc_particles_magic(duration: float, out: str) -> bool:
    """Glowing blue-white magic particles."""
    logger.info("   ✨ Generating magic particles background…")
    life_filter = (
        f"life=size={config.VID_WIDTH}x{config.VID_HEIGHT}:rate={config.VID_FPS}:"
        f"death_color=0x050510:life_color=0x4488ff:mold=50:random_fill_ratio=0.03"
    )
    color_filter = (
        f"scale={config.VID_WIDTH}:{config.VID_HEIGHT},"
        f"colorbalance=bs=0.25:bm=0.2:rs=-0.1:gs=-0.05,"
        f"eq=brightness=-0.08:contrast=1.15:saturation=1.5,"
        f"vignette=PI/4,"
        f"gblur=sigma=2.5"
    )
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", life_filter,
        "-vf", color_filter, "-t", str(duration),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _proc_gradient_blue(duration: float, out: str) -> bool:
    """Slowly shifting blue-grey gradient for sad moods."""
    logger.info("   🌧 Generating sad blue gradient background…")
    from PIL import Image, ImageDraw
    random.seed(42)

    img = Image.new("RGB", (config.VID_WIDTH, config.VID_HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(config.VID_HEIGHT):
        p = y / config.VID_HEIGHT
        r = int(15 + p * 20)
        g = int(20 + p * 30)
        b = int(50 + p * 60)
        draw.line([(0, y), (config.VID_WIDTH, y)], fill=(r, g, b))

    # Add rain-like dots
    for _ in range(200):
        x = random.randint(0, config.VID_WIDTH)
        y = random.randint(0, config.VID_HEIGHT)
        sz = random.randint(1, 2)
        br = random.randint(60, 120)
        draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(br, br, br+20))

    frame = str(config.TEMP_DIR / "bg_blue.png")
    img.save(frame)

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", frame,
        "-vf", f"vignette=PI/4,eq=brightness=-0.05",
        "-t", str(duration), "-r", str(config.VID_FPS),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _proc_gradient_warm(duration: float, out: str) -> bool:
    """Golden warm gradient for happy/triumph moods."""
    logger.info("   ☀️ Generating warm gradient background…")
    from PIL import Image, ImageDraw
    random.seed(42)

    img = Image.new("RGB", (config.VID_WIDTH, config.VID_HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(config.VID_HEIGHT):
        p = y / config.VID_HEIGHT
        r = int(50 + p * 40)
        g = int(25 + p * 30)
        b = int(5 + p * 15)
        draw.line([(0, y), (config.VID_WIDTH, y)], fill=(r, g, b))

    for _ in range(150):
        x = random.randint(0, config.VID_WIDTH)
        y = random.randint(0, config.VID_HEIGHT)
        sz = random.randint(1, 3)
        br = random.randint(150, 220)
        draw.ellipse([x-sz, y-sz, x+sz, y+sz], fill=(br, br-20, br-60))

    frame = str(config.TEMP_DIR / "bg_warm.png")
    img.save(frame)

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", frame,
        "-vf", f"vignette=PI/4",
        "-t", str(duration), "-r", str(config.VID_FPS),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0


def _proc_flash_dark(duration: float, out: str) -> bool:
    """Flash white then dark — for surprise moments."""
    return _proc_plasma_dark(duration, out)  # Fallback to plasma


# Procedural mode dispatcher
PROCEDURAL_GENERATORS = {
    "plasma_dark":      _proc_plasma_dark,
    "particles_fire":   _proc_particles_fire,
    "particles_magic":  _proc_particles_magic,
    "gradient_blue":    _proc_gradient_blue,
    "gradient_warm":    _proc_gradient_warm,
    "flash_dark":       _proc_flash_dark,
}


def generate_procedural_background(mood: str, duration: float, out: str) -> bool:
    """Generate Tier 1 procedural background based on mood."""
    mode = config.BG_PROCEDURAL_MODES.get(mood, "particles_magic")
    generator = PROCEDURAL_GENERATORS.get(mode, _proc_particles_magic)

    success = generator(duration, out)
    if not success:
        logger.warning(f"⚠️  Procedural bg '{mode}' failed → fallback to static")
        _proc_gradient_blue(duration, out)

    return True


# ═══════════════════════════════════════════════════════════════
#  TIER 2: PEXELS STOCK FOOTAGE with Content Filtering
# ═══════════════════════════════════════════════════════════════

def _filter_background_content(video_obj: Dict) -> bool:
    """
    Filter background videos to exclude:
    - Humans, people, faces
    - 3D particles, CGI, renders
    - Urban/modern content
    - Only allow: nature, wildlife, structures, abstract
    
    Args:
        video_obj: Video object from Pexels API
    
    Returns: True if video passes filters, False otherwise
    """
    if not config.FILTER_BACKGROUND_CONTENT:
        return True
    
    # Get video attributes: tags, id, url, etc
    tags = video_obj.get("tags", [])
    if isinstance(tags, list):
        video_tags = " ".join(tags).lower()
    else:
        video_tags = str(tags).lower()
        
    video_url = str(video_obj.get("url", "")).lower()
    search_text = f"{video_tags} {video_url}"
    video_id = video_obj.get("id", 0)
    
    import re
    
    # Check blacklist (reject these terms)
    # Use word boundaries (\b) to avoid "man" matching "mansion"
    for blacklisted in config.BLACKLIST_BACKGROUND_KEYWORDS:
        pattern = r'\b' + re.escape(blacklisted.lower()) + r'\b'
        if re.search(pattern, search_text):
            logger.debug(f"   ❌ Rejected video {video_id} — contains blacklisted '{blacklisted}'")
            return False
    
    # Check whitelist (prefer these terms)
    allowed = False
    for allowed_term in config.ALLOWED_BACKGROUND_KEYWORDS:
        # For whitelist, we allow partial matches (e.g. "forest" matches "rainforest")
        if allowed_term.lower() in search_text:
            allowed = True
            break
    
    if not allowed:
        logger.debug(f"   ❌ Rejected video {video_id} — no allowed keywords found in metadata")
        return False
    
    logger.debug(f"   ✅ Approved video {video_id}")
    return True



def _search_pexels_video(query: str, orientation: str = "portrait", exclude_ids: set = None) -> Optional[tuple]:
    """Search Pexels for a video and return (video_id, download_url)."""
    try:
        import requests
    except ImportError:
        logger.warning("requests not installed — pip install requests")
        return None

    if not config.PEXELS_API_KEY:
        logger.warning("No Pexels API key configured")
        return None

    headers = {"Authorization": config.PEXELS_API_KEY}
    params = {
        "query": query,
        "orientation": orientation,
        "size": "large",
        "per_page": 40, # Increase pool for variety
    }

    try:
        def _execute_search(q: str) -> Optional[tuple]:
            search_params = params.copy()
            search_params["query"] = q
            resp = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers, params=search_params, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            videos = data.get("videos", [])
            if not videos:
                return None
            
            # Filter videos by content policy
            filtered = [v for v in videos if _filter_background_content(v)]
            
            # EXCLUDE already used IDs
            if exclude_ids:
                filtered = [v for v in filtered if v.get("id") not in exclude_ids]

            if not filtered:
                return None
                
            # Prioritize HD/4K videos
            filtered.sort(key=lambda x: x.get("width", 0) * x.get("height", 0), reverse=True)
            
            # Pick a random one from the top quality matches for variety
            video = random.choice(filtered[:min(8, len(filtered))]) 
            vid_id = video.get("id")
            
            best_file = None
            files = video.get("video_files", [])
            # Priority 1: Portrait and HD+
            for vf in files:
                w, h = vf.get("width", 0), vf.get("height", 0)
                if h >= w and h >= 1920:
                    if best_file is None or h > best_file.get("height", 0):
                        best_file = vf
            
            # Priority 2: Portrait any resolution
            if not best_file:
                for vf in files:
                    w, h = vf.get("width", 0), vf.get("height", 0)
                    if h >= w:
                        if best_file is None or h > best_file.get("height", 0):
                            best_file = vf
            
            # Priority 3: Landscape but High Res (will be cropped)
            if not best_file:
                for vf in files:
                    w, h = vf.get("width", 0), vf.get("height", 0)
                    if best_file is None or w > best_file.get("width", 0):
                        best_file = vf
            
            return (vid_id, best_file.get("link")) if best_file else None

        # Try 1: Original query
        result = _execute_search(query)
        if result: return result

        # Try 2: Remove "nobody"
        if "nobody" in query:
            simpler = query.replace("nobody", "").strip()
            result = _execute_search(simpler)
            if result: return result

        # Try 3: Last resort fallback query
        fallback = "cinematic nature scenery landscape 4k"
        return _execute_search(fallback)

    except Exception as e:
        logger.warning(f"Pexels API error: {e}")

    return None


def _download_file(url: str, output_path: str) -> bool:
    """Download a file."""
    try:
        import requests
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logger.warning(f"Download failed: {e}")
        return False


def _prepare_pexels_video(src: str, duration: float, out: str) -> bool:
    """Crop, scale, and color-grade a Pexels video for Shorts."""
    # UPGRADE: Add Ken Burns (slow zoom) effect for dynamic backgrounds
    # Trim 0.5s from start and end to avoid black frames/fades in stock footage
    try:
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", src
        ]
        source_dur = float(subprocess.check_output(probe_cmd).decode().strip())
        
        # If video is shorter than needed, we will loop it with a crossfade
        # But for now, we trim 0.5s to avoid stock footage watermarks/ends
        trim_filter = "trim=start=0.5,setpts=PTS-STARTPTS"
        
        if source_dur < duration + 2.0:
            # Clip is short, use a crossfade-loop filter if we have enough length
            # Otherwise just use stream_loop
            pass 
    except Exception:
        source_dur = 10.0
        trim_filter = "trim=start=0.5,setpts=PTS-STARTPTS"


    # Robust Scaling + Ken Burns (Slow Zoom) Effect
    # zoompan creates a smooth slow zoom for a cinematic feel
    fps = config.VID_FPS
    vf = (
        f"{trim_filter},"
        f"scale=w=1080:h=1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920:x=(iw-ow)/2:y=(ih-oh)/2,"
        f"zoompan=z='min(zoom+0.0005,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={fps},"
        f"eq=brightness=-0.04:contrast=1.05:saturation=1.1,"
        f"vignette=PI/4,"
        f"fps={fps},"
        f"setsar=1/1,"
        f"format=yuv420p"
    )
    
    cmd = ["ffmpeg", "-y"]
    if config.USE_HWACCEL:
        cmd += ["-hwaccel", "auto"]

    cmd += [
        "-stream_loop", "-1", "-i", src,
        "-vf", vf,
        "-t", str(duration),
        "-r", str(config.VID_FPS),
        "-vsync", "cfr",
        "-c:v", config.VIDEO_CODEC,
        "-preset", "ultrafast",
        "-crf", "18",
        "-an",
        "-sn",
        "-avoid_negative_ts", "make_zero",
        "-map_metadata", "-1",
        "-pix_fmt", "yuv420p",
        out
    ]
    
    # UPGRADE: If looping is likely to be visible, we add a very subtle 
    # periodic fade to black/vignette to hide the cut point
    # But a better way is to use xfade on the whole timeline in generate_scene_backgrounds
    # For a single clip, we'll just ensure it's long enough and has a smooth feel.
    # Increased timeout to 300s for robust generation of longer clips
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        logger.error(f"Pexels preparation failed: {r.stderr[-500:]}")
    return r.returncode == 0


def generate_pexels_background(mood: str, duration: float, out: str) -> bool:
    """Generate Tier 2 Pexels background based on mood."""
    search_terms = config.PEXELS_SEARCH_TERMS.get(mood, config.PEXELS_SEARCH_TERMS["neutral"])
    query = random.choice(search_terms)

    # Check cache first
    cache_key = hashlib.md5(query.encode()).hexdigest()[:12]
    cached_raw = str(config.CACHE_DIR / f"pexels_{cache_key}.mp4")

    if not os.path.exists(cached_raw):
        logger.info(f"   🔍 Searching Pexels: '{query}'…")
        url = _search_pexels_video(query)
        if not url:
            logger.warning(f"   ⚠️  No Pexels results for '{query}' → trying fallback…")
            # Try another term
            for term in search_terms:
                if term != query:
                    url = _search_pexels_video(term)
                    if url:
                        break

        if not url:
            logger.warning("   ⚠️  Pexels failed → falling back to procedural")
            return generate_procedural_background(mood, duration, out)

        logger.info(f"   ⬇  Downloading Pexels video…")
        if not _download_file(url, cached_raw):
            return generate_procedural_background(mood, duration, out)

    logger.info(f"   🎥 Preparing Pexels background…")
    success = _prepare_pexels_video(cached_raw, duration, out)

    if not success:
        logger.warning("   ⚠️  Pexels video prep failed → fallback to procedural")
        return generate_procedural_background(mood, duration, out)

    logger.info("   ✅ Pexels background ready!")
    return True


# ═══════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════


def generate_scene_backgrounds(
    segments: List[Dict],
    total_duration: float,
    output_path: str,
) -> str:
    """
    Generate a background video that switches clips whenever the mood changes.

    Fixes problem: single video looping the entire short.

    How it works:
      1. Group consecutive segments by mood
      2. Allocate each group a proportional duration
      3. Fetch a unique Pexels clip per mood group
      4. FFmpeg-concat them into one seamless background

    Args:
        segments: List of segment dicts (each has 'mood' key from mood_detector)
        total_duration: Total video duration in seconds
        output_path: Where to write the stitched background

    Returns: Path to the stitched background video
    """
    if not segments:
        generate_background("neutral", total_duration, output_path)
        return output_path

    # ── Step 1: Group segments by mood and explicit location ──────────
    groups: List[Dict] = []
    for seg in segments:
        mood = seg.get("mood", "neutral")
        txt = seg.get("text", "").lower()
        
        # Detect explicit location trigger by exact phrase match
        detected_loc = None
        for loc_key in getattr(config, "LOCATION_KEYWORDS", {}).keys():
            if loc_key.lower() in txt:
                detected_loc = loc_key
                break
                
        # Group if mood AND location match previous
        if groups and groups[-1]["mood"] == mood and groups[-1].get("location") == detected_loc:
            groups[-1]["word_count"] += len(seg.get("text", "").split())
            groups[-1]["text"] += " " + seg.get("text", "")
        else:
            groups.append({
                "mood":       mood,
                "location":   detected_loc,
                "word_count": len(seg.get("text", "").split()) or 1,
                "text":       seg.get("text", ""),
            })

    # Collapse tiny groups (< 5% of total) into neighbours to avoid flash cuts
    # UNLESS they have an explicit location trigger!
    total_words = sum(g["word_count"] for g in groups) or 1
    merged: List[Dict] = []
    for g in groups:
        is_tiny = (g["word_count"] / total_words) < 0.05
        has_loc = g.get("location") is not None
        
        # Don't merge if it's the very first group (merged is empty)
        if is_tiny and not has_loc and merged:
            merged[-1]["word_count"] += g["word_count"]
            merged[-1]["text"] += " " + g["text"]
        else:
            merged.append(g)
    groups = merged

    # ── Step 1.5: Force splitting of long groups to ensure "multiple and different unique clips" ──
    # Even if mood is same, we want visual variety.
    MAX_CLIP_DURATION = 8.0  # Max seconds per clip to ensure variety
    split_groups: List[Dict] = []
    
    # Calculate initial total words to determine threshold
    total_words = sum(g["word_count"] for g in groups) or 1
    
    for g in groups:
        # Estimated duration of this group
        est_dur = total_duration * (g["word_count"] / total_words)
        
        if est_dur > MAX_CLIP_DURATION:
            # Split into roughly equal chunks of ~MAX_CLIP_DURATION
            num_splits = math.ceil(est_dur / MAX_CLIP_DURATION)
            words = g["text"].split()
            words_per_split = len(words) // num_splits
            
            for s in range(num_splits):
                start_idx = s * words_per_split
                end_idx = (s + 1) * words_per_split if s < num_splits - 1 else len(words)
                chunk_text = " ".join(words[start_idx:end_idx])
                split_groups.append({
                    "mood":       g["mood"],
                    "location":   g.get("location"),
                    "word_count": len(chunk_text.split()) or 1,
                    "text":       chunk_text,
                })
        else:
            split_groups.append(g)
    
    # ENSURE AT LEAST 3 CLIPS for the Loop (First, Middle(s), Last)
    # If we have 1 or 2 clips, split the largest one until we have 3.
    while len(split_groups) < 3 and total_duration > 5.0:
        # Find largest group to split
        largest_idx = 0
        for idx, sg in enumerate(split_groups):
            if sg["word_count"] > split_groups[largest_idx]["word_count"]:
                largest_idx = idx
        
        target = split_groups[largest_idx]
        if target["word_count"] < 2: break # Can't split further
        
        words = target["text"].split()
        mid = len(words) // 2
        t1 = " ".join(words[:mid])
        t2 = " ".join(words[mid:])
        
        split_groups[largest_idx] = {
            "mood": target["mood"],
            "word_count": len(t1.split()) or 1,
            "text": t1
        }
        split_groups.insert(largest_idx + 1, {
            "mood": target["mood"],
            "word_count": len(t2.split()) or 1,
            "text": t2
        })

    groups = split_groups
    total_words = sum(g["word_count"] for g in groups) or 1

    # ── Step 2: Allocate durations (proportional + xfade overhead) ──
    n = len(groups)
    FADE_DUR = getattr(config, 'SCENE_TRANSITION_DUR', 1.2)

    for i, g in enumerate(groups):
        base = max(2.5, total_duration * (g["word_count"] / total_words))
        g["duration"] = base + FADE_DUR if i < n - 1 else base

    target_sum = sum(g["duration"] for g in groups)
    logger.info(f"🎬 Scene backgrounds: {n} mood group(s) | Total: {total_duration:.1f}s (internal {target_sum:.1f}s)")
    for i, g in enumerate(groups):
        logger.info(f"   [{i+1}] mood={g['mood']:<10} dur={g['duration']:.1f}s")

    # ── Step 3: Generate one clip per group ───────────────────
    clip_paths: List[str] = []
    used_video_ids: set = set()
    first_clip_raw = None

    # Determine max duration needed for the looping first clip
    loop_clip_dur = groups[0]["duration"]
    if len(groups) > 1:
        loop_clip_dur = max(groups[0]["duration"], groups[-1]["duration"])

    for i, group in enumerate(groups):
        clip_path = str(config.TEMP_DIR / f"scene_bg_{i:03d}.mp4")
        mood      = group["mood"]
        
        # Override duration for start/end loop clip
        if i == 0 or i == len(groups) - 1:
            dur = loop_clip_dur
        else:
            dur = group["duration"]
            
        txt       = group.get("text", "").lower()

        # 🔄 LOOP EFFECT: Re-use exact same generated scene_bg_000.mp4
        if i == len(groups) - 1 and len(groups) > 1 and len(clip_paths) > 0:
            clip_paths.append(clip_paths[0])
            logger.info(f"   [{i+1}] 🔁 LOOP CLIP: Reusing exactly scene_bg_000.mp4 for seamless start/end match")
            continue

        if config.PEXELS_API_KEY:
            quality_suffix = "wilderness cinematic 4k"
            
            def _clean_query(base: str, suffix: str) -> str:
                suffix_words = suffix.split()
                base_lower = base.lower()
                to_add = [w for w in suffix_words if w.lower() not in base_lower]
                return f"{base} {' '.join(to_add)}".strip()

            candidates = [
                _clean_query(q, quality_suffix)
                for q in config.PEXELS_SEARCH_TERMS.get(mood, config.PEXELS_SEARCH_TERMS["neutral"])
            ]

            location_candidates = []
            if group.get("location"):
                loc_key = group["location"]
                loc_query = getattr(config, "LOCATION_KEYWORDS", {}).get(loc_key)
                if loc_query:
                    location_candidates.append(_clean_query(loc_query, quality_suffix))
                    logger.info(f"   [{i+1}] 📍 Detected Location: {loc_key}")
            else:
                # Fallback: strictly check text
                for loc_key, loc_query in getattr(config, "LOCATION_KEYWORDS", {}).items():
                    if loc_key.lower() in txt:
                        location_candidates.append(_clean_query(loc_query, quality_suffix))
                        logger.info(f"   [{i+1}] 📍 Detected Location (fallback): {loc_key}")
                        break

            if location_candidates:
                candidates = location_candidates

            query = random.choice(candidates)
            
            # ── CURATED BACKGROUND LIBRARY OVERRIDE ──
            local_clip = None
            curated_dir = Path("assets/backgrounds")
            if curated_dir.exists():
                search_terms = [mood] + [k.replace(" ", "_") for k in getattr(config, "LOCATION_KEYWORDS", {}).keys()]
                for term in search_terms:
                    term_dir = curated_dir / term
                    if term_dir.exists():
                        local_files = list(term_dir.glob("*.mp4"))
                        if local_files:
                            # Try to pick a local clip not used in first/prev
                            local_clip = str(random.choice(local_files))
                            logger.info(f"   [{i+1}] 📁 Curated library clip: {local_clip}")
                            break
            
            if local_clip:
                if i == 0: first_clip_raw = local_clip
                if _prepare_pexels_video(local_clip, dur, clip_path):
                    clip_paths.append(clip_path)
                    continue

            # ── PEXELS SEARCH ──
            logger.info(f"   [{i+1}] 🔍 Pexels Search: '{query}'...")
            res = _search_pexels_video(query, exclude_ids=used_video_ids)
            
            if res:
                vid_id, url = res
                used_video_ids.add(vid_id)
                cache_key = hashlib.md5(str(vid_id).encode()).hexdigest()[:12]
                cached_raw = str(config.CACHE_DIR / f"pexels_{cache_key}.mp4")

                if not os.path.exists(cached_raw):
                    if not _download_file(url, cached_raw):
                        url = None

                if url and os.path.exists(cached_raw):
                    if i == 0: first_clip_raw = cached_raw
                    if _prepare_pexels_video(cached_raw, dur, clip_path):
                        clip_paths.append(clip_path)
                        logger.info(f"   [{i+1}] ✅ Unique clip ready (ID: {vid_id})")
                        continue

            logger.warning(f"   [{i+1}] ⚠️  Unique Pexels failed → procedural fallback")

        # Fallback: procedural
        generate_procedural_background(mood, dur, clip_path)
        clip_paths.append(clip_path)

    if not clip_paths:
        generate_background("neutral", total_duration, output_path)
        return output_path

    if len(clip_paths) == 1:
        # Just trim to exact duration
        _trim_clip(clip_paths[0], total_duration, output_path)
        return output_path

    # ── Step 4: Stitch clips with crossfade ───────────────────
    return _crossfade_concat(clip_paths, groups, total_duration, output_path)


def _trim_clip(src: str, duration: float, output: str) -> str:
    """Trim a video clip to an exact duration."""
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-t", str(duration),
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
        "-pix_fmt", "yuv420p", output,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return output if r.returncode == 0 else src


def _crossfade_concat(
    clip_paths: List[str],
    groups: List[Dict],
    total_duration: float,
    output_path: str,
) -> str:
    """
    Crossfade-concatenate multiple clips using FFmpeg xfade filter.
    Falls back to hard cut concat if xfade fails.
    """
    FADE_DUR = getattr(config, 'SCENE_TRANSITION_DUR', 1.2)
    try:
        # Build xfade filter chain - using smooth transitions as requested
        # 'fade' is the most stable and smooth for cinematic backgrounds
        dopamine_transitions = [
            "fade",           # Classic dissolve
            "fadeblack",      # Fade through black
            "fadegrays",      # Fade through greys (cinematic)
            "dissolve",       # Pixel dissolve
        ]
        
        n = len(clip_paths)
        filter_parts = []

        # Pre-process all inputs to strictly ensure identical resolution, timebase, and framerate
        fps = config.VID_FPS
        for i in range(n):
            filter_parts.append(
                f"[{i}:v]scale={config.VID_WIDTH}:{config.VID_HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={config.VID_WIDTH}:{config.VID_HEIGHT},"
                f"fps={fps},"
                f"setsar=1/1,"
                f"format=yuv420p[v_norm_{i}]"
            )

        if n == 1:
            filter_parts.append(f"[v_norm_0]setsar=1/1,format=yuv420p[vout]")
        else:
            # The xfade filter takes 'offset' as the time relative to the START of the FIRST input.
            # When chaining, each new clip adds (duration - FADE_DUR) to the total timeline.
            current_timeline_dur = groups[0]["duration"]
            last_out = "[v_norm_0]"
            
            for i in range(1, n):
                trans = random.choice(dopamine_transitions)
                dur_next = groups[i]["duration"]
                
                # The transition starts FADE_DUR before the end of the CURRENT accumulated video
                xfade_offset = current_timeline_dur - FADE_DUR
                logger.info(f"   🎬 XFade {i}: offset={xfade_offset:.2f}s, trans={trans}")
                
                # Safety: ensure offset is valid (not negative, not beyond current duration)
                xfade_offset = max(0.1, min(xfade_offset, current_timeline_dur - 0.2))
                
                out_pad = f"[v_xfade_{i}]"
                filter_parts.append(f"{last_out}[v_norm_{i}]xfade=transition={trans}:duration={FADE_DUR}:offset={xfade_offset:.3f}{out_pad}")
                
                # Update the total duration of the accumulated stream
                current_timeline_dur = xfade_offset + dur_next
                last_out = out_pad

            # Final pass — clean up SAR and pixel format
            filter_parts.append(f"{last_out}setsar=1/1,format=yuv420p[vout]")

        filter_complex = "; ".join(filter_parts)

        inputs = []
        for p in clip_paths:
            inputs += ["-i", p]

        cmd = (
            ["ffmpeg", "-y"] + inputs
            + ["-filter_complex", filter_complex,
               "-map", "[vout]",
               "-t", f"{total_duration:.3f}",
               "-r", str(config.VID_FPS),
               "-vsync", "cfr",
               "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast",
               "-pix_fmt", "yuv420p", output_path]
        )

        # Increased timeout for long video assembly (300s)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if r.returncode == 0:
            logger.info(f"✅ Scene backgrounds stitched with crossfade ({n} clips)")
            return output_path

        logger.warning(f"xfade concat failed — using robust re-encoded hard-cut fallback.")
    except Exception as e:
        logger.warning(f"xfade transition error: {e}. Falling back to hard-cut.")
    
    # ── Robust Hard-cut fallback (Re-encoded) ─────────────────
    concat_file = str(config.TEMP_DIR / "bg_concat.txt")
    with open(concat_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd_fallback = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-t", str(total_duration),
        "-r", str(config.VID_FPS),
        "-vf", f"fps={config.VID_FPS},settb=1/60,setpts=N/60/TB,format=yuv420p",
        "-c:v", config.VIDEO_CODEC, "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", output_path
    ]
    r_f = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=180)
    
    if r_f.returncode != 0:
        logger.error(f"❌ Hard-cut fallback failed: {r_f.stderr[-300:]}")
        # Final desperate fallback: Just use the first clip trimmed
        _trim_clip(clip_paths[0], total_duration, output_path)
    
    return output_path


# ────────────────────────────────────────────────────────────────
#  REPLACE generate_background() with this version
#  (keeps all existing logic, adds scene routing)
# ────────────────────────────────────────────────────────────────

def generate_background(
    mood: str,
    duration: float,
    out: str,
    segments: list = None,   # ← NEW optional param
) -> None:
    """
    Generate background video.

    UPGRADED:
      If segments are provided (from generate_short pipeline), call
      generate_scene_backgrounds() for per-scene clip switching.
      Otherwise behaves exactly as before.

    Args:
        mood:     Overall mood string (used as fallback when no segments)
        duration: Total duration in seconds
        out:      Output file path
        segments: Optional list of segment dicts with 'mood' keys
    """
    # Custom video override
    if config.BG_CUSTOM_VIDEO and os.path.exists(config.BG_CUSTOM_VIDEO):
        logger.info(f"🎥 Using custom background: {config.BG_CUSTOM_VIDEO}")
        _prepare_pexels_video(config.BG_CUSTOM_VIDEO, duration, out)
        return

    # Multi-scene path (NEW)
    if segments and len(segments) > 1 and config.BG_TIER > 0:
        generate_scene_backgrounds(segments, duration, out)
        return

    # Single-mood path (original behaviour)
    tier = config.BG_TIER
    if tier >= 2 and config.PEXELS_API_KEY:
        if generate_pexels_background(mood, duration, out):
            return

    if tier >= 1:
        generate_procedural_background(mood, duration, out)
        return
        
    # Tier 0 (or fallback for all): Solid Color Background
    _proc_solid_color(mood, duration, out)
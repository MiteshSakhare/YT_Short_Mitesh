#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  SUBTITLE_SYNC.PY — Frame-Perfect Audio/Subtitle Synchronization
#  Fixes sync issues using precise audio timing detection
# ═══════════════════════════════════════════════════════════════

import subprocess
import logging
import sys
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


def get_audio_duration_accurate(audio_file: str) -> float:
    """Get accurate audio duration using ffprobe JSON output."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1:noesc=1",
                audio_file
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Could not get audio duration: {e}")
        return 0.0


def detect_speech_segments(audio_file: str) -> List[Tuple[float, float]]:
    """
    Detect speech/silence segments using FFmpeg's silencedetect filter.
    Returns list of (start_time, end_time) tuples for speech segments.
    """
    try:
        # Use silencedetect to find silence periods
        cmd = [
            "ffmpeg", "-i", audio_file,
            "-af", "silencedetect=n=-40dB:d=0.3",
            "-f", "null", "-"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse silencedetect output for timing
        segments = []
        lines = result.stderr.split('\n')
        
        silence_starts = []
        silence_ends = []
        
        for line in lines:
            if "silence_start:" in line:
                try:
                    time_str = line.split("silence_start:")[1].strip()
                    time = float(time_str)
                    silence_starts.append(time)
                except:
                    pass
            elif "silence_end:" in line:
                try:
                    time_str = line.split("silence_end:")[1].strip().split()[0]
                    time = float(time_str)
                    silence_ends.append(time)
                except:
                    pass
        
        # Build speech segments from silence boundaries
        total_duration = get_audio_duration_accurate(audio_file)
        
        if not silence_ends:
            # No silence detected, assume whole file is speech
            return [(0.0, total_duration)]
        
        speech_segments = []
        current_time = 0.0
        
        # FFmpeg silencedetect output is always in order: start, end, start, end...
        # We want the gaps between (0 to first_start), (first_end to second_start), etc.
        for i in range(len(silence_starts)):
            s_start = silence_starts[i]
            if s_start > current_time + 0.1:  # At least 100ms of speech
                speech_segments.append((current_time, s_start))
            
            if i < len(silence_ends):
                current_time = silence_ends[i]
            else:
                # Silence started but never ended before EOF
                current_time = total_duration
                break
        
        # Handle the remaining part after the last silence end
        if current_time < total_duration - 0.1:
            speech_segments.append((current_time, total_duration))
        
        return speech_segments
        
    except Exception as e:
        logger.warning(f"Speech detection failed: {e}")
        return []


def align_segments_to_speech(segments: List[Dict], audio_file: str) -> List[Dict]:
    """
    Align text segments to detected speech boundaries.
    This ensures subtitles start exactly when speech starts.
    
    Args:
        segments: List of {text, speaker, start_time, duration} dicts
        audio_file: Path to audio file
    
    Returns: Updated segments with corrected timing
    """
    try:
        # Get speech segments
        speech_segments = detect_speech_segments(audio_file)
        
        if not speech_segments:
            logger.warning("No speech detected, using original timing")
            return segments
        
        # Align each text segment to nearest speech boundary
        aligned_segments = []
        
        for i, seg in enumerate(segments):
            original_start = seg.get("start_time", 0.0)
            original_duration = seg.get("duration", 2.0)
            
            # Find nearest speech segment
            best_match = None
            min_distance = float('inf')
            
            for speech_start, speech_end in speech_segments:
                distance = abs(speech_start - original_start)
                if distance < min_distance and speech_start <= original_start + original_duration:
                    min_distance = distance
                    best_match = (speech_start, speech_end)
            
            if best_match:
                # Align to speech boundaries
                aligned_start, aligned_end = best_match
                aligned_duration = aligned_end - aligned_start
                
                seg["start_time"] = aligned_start
                seg["duration"] = aligned_duration
                seg["_aligned"] = True
                
                logger.debug(
                    f"Aligned segment {i}: {original_start:.2f}s → {aligned_start:.2f}s"
                )
            
            aligned_segments.append(seg)
        
        return aligned_segments
        
    except Exception as e:
        logger.warning(f"Segment alignment failed: {e}")
        return segments


def sec_to_ass(t: float) -> str:
    """Convert seconds to ASS subtitle format (H:MM:SS.CC)."""
    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    centiseconds = int((t % 1) * 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def create_synced_subtitles(
    segments: List[Dict],
    output_ass: str,
    video_duration: float = 60.0
) -> str:
    """
    Create properly synced subtitles from aligned segments.
    
    Args:
        segments: Aligned segment list with timing info
        output_ass: Output ASS file path
        video_duration: Total video duration
    
    Returns: Path to ASS file
    """
    try:
        # ASS header
        ass_lines = [
            "[Script Info]",
            "Title: The Twice-Crowned King",
            "ScriptType: v4.00+",
            "WrapStyle: 1",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "PlayDepth: 0",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: Default,Arial Black,75,&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,105,105,0,0,1,4,3,2,60,60,550,1",
            "Style: Narrator,Arial Black,75,&H0000FFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,105,105,0,0,1,4,3,2,60,60,550,1",
            "Style: Intro,Impact,100,&H0000D7FF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,110,110,0,0,1,8,6,5,40,40,500,1",
            "Style: Outro,Impact,100,&H0000FFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,110,110,0,0,1,8,6,5,40,40,500,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        # Add subtitle events
        num_segments = len(segments)
        for idx, seg in enumerate(segments):
            text = seg.get("text", "").replace('\n', ' ').strip()
            if not text:
                continue

            start_time = seg.get("start_time", 0.0)
            duration = seg.get("duration", 3.0)
            end_time = min(video_duration, start_time + duration)
            speaker = seg.get("speaker", "narrator")

            # Determine style
            if idx == 0:
                style = "Intro"
            elif idx == num_segments - 1:
                style = "Outro"
            else:
                style = "Narrator" if speaker.lower() == "narrator" else "Default"

            start_str = sec_to_ass(start_time)
            end_str = sec_to_ass(end_time)
            ass_line = (
                f"Dialogue: 0,{start_str},{end_str},"
                f"{style},,0,0,0,,"
                f"{text}"
            )
            ass_lines.append(ass_line)
        
        # Write ASS file
        with open(output_ass, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ass_lines))
        
        logger.info(f"✅ Synced subtitles created: {output_ass}")
        return output_ass
        
    except Exception as e:
        logger.error(f"Failed to create synced subtitles: {e}")
        raise


def verify_audio_subtitle_sync(audio_file: str, ass_file: str) -> Dict:
    """
    Analyze sync quality between audio and subtitles.
    
    Returns: {
        "valid": bool,
        "total_segments": int,
        "sync_quality": "PERFECT" | "GOOD" | "FAIR" | "POOR",
        "issues": [list of problems]
    }
    """
    try:
        audio_duration = get_audio_duration_accurate(audio_file)
        
        # Parse ASS file
        subtitle_events = []
        with open(ass_file, 'r', encoding='utf-8') as f:
            in_events = False
            for line in f:
                if line.startswith("[Events]"):
                    in_events = True
                    continue
                if in_events and line.startswith("Dialogue:"):
                    parts = line.split(',', 9)
                    if len(parts) >= 9:
                        try:
                            # Helper to parse ASS time (H:MM:SS.cc or MM:SS.cc)
                            def parse_ass_time(ts):
                                t_parts = ts.split(':')
                                if len(t_parts) == 3:
                                    return int(t_parts[0])*3600 + int(t_parts[1])*60 + float(t_parts[2])
                                return int(t_parts[0])*60 + float(t_parts[1])

                            start = parse_ass_time(parts[1])
                            end = parse_ass_time(parts[2])
                            subtitle_events.append((start, end))
                        except Exception as e:
                            logger.debug(f"Skipping malformed dialogue line: {e}")
        
        issues = []
        
        # Check for gaps
        for i in range(len(subtitle_events) - 1):
            _, curr_end = subtitle_events[i]
            next_start, _ = subtitle_events[i + 1]
            gap = next_start - curr_end
            if gap > 0.5:  # More than 500ms gap
                issues.append(f"Gap of {gap:.1f}s between subtitle {i} and {i+1}")
        
        # Check for overlaps
        for i in range(len(subtitle_events) - 1):
            _, curr_end = subtitle_events[i]
            next_start, _ = subtitle_events[i + 1]
            if curr_end > next_start:
                issues.append(f"Subtitle {i} overlaps with subtitle {i+1}")
        
        # Check duration match
        if subtitle_events:
            last_end = subtitle_events[-1][1]
            duration_diff = abs(audio_duration - last_end)
            if duration_diff > 2.0:
                issues.append(
                    f"Final subtitle ends at {last_end:.1f}s, "
                    f"but audio is {audio_duration:.1f}s"
                )
        
        # Determine quality
        if not issues:
            quality = "PERFECT"
        elif len(issues) <= 2:
            quality = "GOOD"
        elif len(issues) <= 5:
            quality = "FAIR"
        else:
            quality = "POOR"
        
        return {
            "valid": len(issues) == 0,
            "total_segments": len(subtitle_events),
            "audio_duration": audio_duration,
            "sync_quality": quality,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Sync verification failed: {e}")
        return {
            "valid": False,
            "sync_quality": "ERROR",
            "issues": [str(e)]
        }

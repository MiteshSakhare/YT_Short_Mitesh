#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  PATCH 03 — split_story_v2.py
#  Full replacement for split_story.py in the project root.
#
#  Fixes problem: story divided by TEXT not CONTEXT
#  → Shorts no longer feel unfinished mid-sentence
#
#  KEY CHANGES from original:
#    • Never cuts mid-paragraph
#    • Never cuts mid-sentence
#    • Each Short ends at a natural dramatic beat
#    • Detects "hook sentences" (dramatic questions/reveals) to prefer
#      ending shorts just BEFORE them (creates open loop → keeps viewers coming back)
#    • Target 200–270 words, but paragraph integrity wins over word count
# ═══════════════════════════════════════════════════════════════

from docx import Document
from pathlib import Path
import re

# Project root is one level up from tools/
PROJECT_ROOT = Path(__file__).parent.parent

# ─────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────
STORY_PATH    = str(PROJECT_ROOT / 'story' / 'The Twice-Crowned King.docx')
INPUT_DIR     = PROJECT_ROOT / 'input'
MIN_WORDS     = 150      # Don't cut a segment shorter than this
MAX_WORDS     = 290      # Upper hard cap (one extra long para is OK)
TARGET_WORDS  = 230      # Ideal length

# Signals that a sentence should OPEN a new Short (viewer already invested)
# Cliffhanger trigger: if a para ends with these patterns, end the Short here
CLIFFHANGER_ENDS = re.compile(
    r'(\.{3}|—|\?|!\s*"|\bwould\s+never\b|\bno\s+one\s+knew\b|\bwas\s+about\s+to\b'
    r'|\bthat\s+changed\s+everything\b|\bhe\s+froze\b|\bshe\s+froze\b'
    r'|\bthe\s+truth\b.*\.$|\bimpossible\b.*\.$|\bnobody\b.*saw\b)',
    re.IGNORECASE
)

# Patterns that mark chapter / section headers (skip from TTS)
CHAPTER_HEADER = re.compile(r'^(Part\s+\d+|Chapter\s+\d+|═+|─+|\*\*\*)', re.IGNORECASE)
END_MARKER = re.compile(r'(?i)^end\s+of\s+part\s+\d+.*$', re.IGNORECASE)


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

def _word_count(text: str) -> int:
    return len(text.split())


def _is_cliffhanger(para: str) -> bool:
    """Return True if this paragraph ends at a good break point."""
    return bool(CLIFFHANGER_ENDS.search(para.rstrip()))


def _format_short(paragraphs: list, chapter_title: str, short_num: int) -> str:
    """
    Format a group of paragraphs as a Short script.
    Adds NARRATOR: prefix so the existing parse_script() works unchanged.
    """
    title_line = f"# {chapter_title}" if chapter_title else f"# Part {short_num}"
    body = "\n\n".join(paragraphs)
    return f"{title_line}\n\nNARRATOR:\n{body}"


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("📖 Extracting story from DOCX (context-aware split)…")

    doc = Document(STORY_PATH)
    all_paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    print(f"   ✓ {len(all_paras)} paragraphs extracted")

    INPUT_DIR.mkdir(exist_ok=True)

    shorts          = []
    current_paras   = []
    current_words   = 0
    chapter_title   = ""
    short_num       = 1

    def _flush(reason: str = ""):
        nonlocal current_paras, current_words, short_num
        if not current_paras:
            return
        content = _format_short(current_paras, chapter_title, short_num)
        shorts.append({
            "number":  short_num,
            "content": content,
            "words":   current_words,
            "reason":  reason,
        })
        short_num    += 1
        current_paras = []
        current_words = 0

    for para in all_paras:
        # ── Skip chapter headers and end markers ──────────────
        if END_MARKER.match(para):
            continue
            
        if CHAPTER_HEADER.match(para):
            # Flush current accumulation before new chapter
            if current_words >= MIN_WORDS:
                _flush("chapter_break")
            chapter_title = para
            continue

        para_words = _word_count(para)

        # Skip near-empty lines
        if para_words < 3:
            continue

        # ── Decide whether to flush BEFORE adding this para ──
        projected = current_words + para_words

        should_flush = False
        flush_reason = ""

        if projected > MAX_WORDS and current_words >= MIN_WORDS:
            # Hard cap hit — flush before this paragraph
            should_flush  = True
            flush_reason  = "max_words"

        elif current_words >= TARGET_WORDS and _is_cliffhanger(
            current_paras[-1] if current_paras else ""
        ):
            # We're at a good length AND the previous paragraph is a cliffhanger
            # → End here for maximum viewer retention
            should_flush  = True
            flush_reason  = "cliffhanger_beat"

        if should_flush:
            _flush(flush_reason)

        current_paras.append(para)
        current_words += para_words

    # Don't lose the last group
    if current_words >= MIN_WORDS // 2:
        _flush("end_of_story")
    elif current_paras and shorts:
        # Merge tiny tail into last Short
        shorts[-1]["content"] += "\n\n" + "\n\n".join(current_paras)
        shorts[-1]["words"]   += current_words

    # ── Write output files ────────────────────────────────────
    print(f"\n📝 Writing {len(shorts)} input files…\n")
    for short in shorts:
        filename = INPUT_DIR / f"part_{short['number']:04d}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(short['content'])
        print(f"   ✓ {filename.name}  ({short['words']} words)  [{short['reason']}]")

    # ── Summary ───────────────────────────────────────────────
    avg   = sum(s['words'] for s in shorts) // max(len(shorts), 1)
    total = sum(s['words'] for s in shorts)
    cliffhangers = sum(1 for s in shorts if s['reason'] == 'cliffhanger_beat')

    print("\n" + "="*60)
    print("✅ Context-aware split complete")
    print(f"   Total Shorts : {len(shorts)}")
    print(f"   Avg words    : {avg}")
    print(f"   Total words  : {total:,}")
    print(f"   Cliffhangers : {cliffhangers} Shorts end on dramatic beat")
    print("="*60)
    print("\nNext: python batch_generate.py  (or range test with part_0001.txt)")


if __name__ == "__main__":
    main()
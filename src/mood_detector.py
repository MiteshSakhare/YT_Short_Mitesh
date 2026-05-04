#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  MOOD_DETECTOR.PY — Analyzes script text to detect mood/emotion
#  Returns mood classification per segment for background/SFX matching
# ═══════════════════════════════════════════════════════════════

import re
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────────────────────
#  MOOD KEYWORD DATABASE
# ─────────────────────────────────────────────────────────────
MOOD_KEYWORDS = {
    "dark": [
        "shadow", "darkness", "dark", "ominous", "curse", "cursed", "whispered",
        "creeping", "sinister", "malice", "evil", "demon", "demonic", "void",
        "black", "night", "nightmare", "dread", "tomb", "death", "dead",
        "corpse", "bone", "skull", "grave", "poison", "venom", "serpent",
        "betrayal", "betrayed", "traitor", "corrupt", "twisted", "wicked",
        "demon emperor", "obsidian fortress", "reincarnation", "soul", "black flame",
        "soul-eater", "forbidden art", "necrotic", "abyss", "suffocating",
    ],
    "sad": [
        "tears", "wept", "crying", "sorrow", "loss", "grief", "mourned",
        "farewell", "goodbye", "alone", "lonely", "abandoned", "broken",
        "dying", "sacrifice", "regret", "pain", "suffering", "hopeless",
        "defeated", "fallen", "exiled", "forgotten", "lost", "despair",
        "melancholy", "heartbreak", "silent", "empty", "cold",
        "unraveled", "final thought", "last bow", "faded",
        "pathetic", "useless", "shame", "pitiful",
    ],
    "thrill": [
        "danger", "fight", "fought", "blood", "chase", "escape", "trembled",
        "heart pounded", "racing", "running", "attack", "ambush", "trapped",
        "panic", "urgent", "hurry", "fast", "blade", "strike", "clash",
        "dodged", "ducked", "slammed", "crashed", "explosion", "shattered",
        "screamed", "chaos", "volatile", "pulse", "adrenaline",
        "holy sword", "heart driven", "agony", "wrenching", "tearing",
        "parried", "bloodlust", "lethal", "lightning", "impact",
    ],
    "happy": [
        "smiled", "laughed", "laughter", "triumph", "victory", "celebrated",
        "joy", "joyful", "grinned", "warm", "warmth", "bright", "light",
        "sunrise", "dawn", "hope", "hopeful", "free", "freedom", "peace",
        "peaceful", "gentle", "kind", "kindness", "beauty", "beautiful",
        "love", "embrace", "comfort", "safe", "something that mattered",
    ],
    "epic": [
        "army", "armies", "battle", "war", "sword", "swords", "kingdom",
        "throne", "crown", "crowned", "emperor", "king", "queen", "power",
        "powerful", "mighty", "unstoppable", "legendary", "destiny", "fate",
        "prophecy", "ancient", "empire", "conquer", "conquered", "rise",
        "arose", "march", "marched", "champion", "glory", "glorious",
        "ten thousand", "fortress", "siege", "dragon",
        "demon emperor", "three great realms", "merciless strategy",
        "kaelen", "dragomir", "ducal", "grand duke", "imperial army", "divine",
    ],
    "surprise": [
        "gasped", "impossible", "revealed", "reveal", "secret", "suddenly",
        "unexpected", "shocked", "stunned", "speechless", "frozen", "twist",
        "unbelievable", "what", "how", "no way", "turned out", "truth",
        "discovered", "unveiled", "realization", "understood", "realized",
        "recognized", "stared", "disbelief", "astonished", "jaw dropped",
        "child's hands", "small weak", "not his own",
    ],
    "mystery": [
        "mystery", "mysterious", "unknown", "hidden", "concealed", "riddle",
        "puzzle", "enigma", "fog", "mist", "veil", "cloak", "unseen",
        "watching", "lurking", "waiting", "careful", "cautious", "wary",
        "strange", "peculiar", "odd", "eerie", "unsettling", "quiet",
        "silence", "faint", "flickering", "glimmer", "ancient",
        "masked", "slumbering", "sealed", "locked",
    ],
}

# Intensity modifiers — words that amplify mood
INTENSITY_AMPLIFIERS = [
    "very", "extremely", "incredibly", "absolutely", "utterly",
    "completely", "totally", "overwhelmingly", "deeply", "immensely",
    "terribly", "violently", "fiercely", "intensely", "desperately",
]

def detect_mood(text: str) -> Dict[str, float]:
    """
    Analyze text and return mood scores (0.0–1.0 for each mood).
    Returns dict: {"dark": 0.7, "sad": 0.3, ...}
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    total_words = max(len(words), 1)

    scores = {}
    for mood, keywords in MOOD_KEYWORDS.items():
        count = 0
        for kw in keywords:
            if " " in kw:
                count += text_lower.count(kw)
            else:
                count += words.count(kw)
        # Normalize to 0-1 range
        raw = count / total_words
        scores[mood] = min(1.0, raw * 5.0)  # Reduced scale factor to prevent over-triggering

    # Check for intensity amplifiers
    amp_count = sum(1 for w in words if w in INTENSITY_AMPLIFIERS)
    if amp_count > 0:
        amp_boost = 1.0 + (amp_count * 0.1)
        for mood in scores:
            scores[mood] = min(1.0, scores[mood] * amp_boost)

    return scores


def get_primary_mood(text: str) -> Tuple[str, float]:
    """
    Return the dominant mood and its intensity.
    Returns: (mood_name, intensity)
    """
    # 1. MOOD OVERRIDE: Check for explicit [MOOD: xxx] tag
    override_match = re.search(r'\[MOOD:\s*(\w+)\]', text, re.IGNORECASE)
    if override_match:
        mood = override_match.group(1).lower()
        if mood in MOOD_KEYWORDS or mood in ["neutral", "gloomy"]:
            return mood, 1.0

    scores = detect_mood(text)

    if not scores or max(scores.values()) < 0.05:
        return "neutral", 0.5

    primary = max(scores, key=scores.get)
    intensity = scores[primary]

    # 2. TWO-TIER FALLBACK: Use a milder variant for low-intensity dark moods
    if primary == "dark" and intensity < 0.4:
        primary = "gloomy"

    return primary, intensity


def get_segment_moods(segments: List[Dict]) -> List[Dict]:
    """
    Analyze each segment and add mood information.
    Takes list of segment dicts, returns enriched list with 'mood' key.
    """
    enriched = []
    for seg in segments:
        mood, intensity = get_primary_mood(seg.get("text", ""))
        seg_copy = seg.copy()
        seg_copy["mood"] = mood
        seg_copy["mood_intensity"] = intensity
        enriched.append(seg_copy)
    return enriched


def get_overall_mood(segments: List[Dict]) -> str:
    """
    Determine the overall mood of the entire script from all segments.
    Uses weighted voting — later segments count slightly more (climax bias).
    """
    mood_votes = {}
    total = len(segments)

    for i, seg in enumerate(segments):
        text = seg.get("text", "")
        mood, intensity = get_primary_mood(text)
        # Weight: later segments matter more (climax of the part)
        weight = 0.5 + (i / max(total, 1)) * 0.5
        mood_votes[mood] = mood_votes.get(mood, 0) + (intensity * weight)

    if not mood_votes:
        return "neutral"

    return max(mood_votes, key=mood_votes.get)


if __name__ == "__main__":
    # Quick test
    test_texts = [
        "He drew his sword and charged into the army. Blood sprayed as blades clashed.",
        "She wept silently, alone in the tower. The farewell had broken something inside her.",
        "Something moved in the shadows. A whisper. A flicker. Someone was watching.",
        "The crowd roared as he lifted the crown. Victory. Glory. He had conquered them all.",
        "She gasped. It was impossible. The truth was right there, and no one had seen it.",
    ]
    for text in test_texts:
        mood, intensity = get_primary_mood(text)
        print(f"[{mood:>10} {intensity:.2f}] {text[:70]}...")

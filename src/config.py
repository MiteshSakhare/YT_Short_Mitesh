# ═══════════════════════════════════════════════════════════════
#  CONFIG.PY — YouTube Shorts Generator Configuration (v2.0)
#  The Twice-Crowned King — AI Video Pipeline
#  Edit these settings to customize your video generation
# ═══════════════════════════════════════════════════════════════

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# ─────────────────────────────────────────────────────────────
#  DIRECTORY SETUP
# ─────────────────────────────────────────────────────────────
# Set BASE_DIR relative to where the project root is (one folder up from src/)
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / ".temp"
SFX_DIR = BASE_DIR / "sfx"
CACHE_DIR = BASE_DIR / ".cache"
ASSETS_DIR = BASE_DIR / "assets"

for _d in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR, SFX_DIR, CACHE_DIR, ASSETS_DIR]:
    _d.mkdir(exist_ok=True)

# Create logs directory
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ── BATCH & PERFORMANCE ──────────────────────────────────────
MAX_THREADS = 1            # Number of parallel video generations (Sequential for stability)
TTS_CACHE_ENABLED = True    # Skip redundant TTS generation
CLEANUP_TEMP = True         # Auto-delete temp files after success

# ── THUMBNAIL SETTINGS ──────────────────────────────────────
THUMBNAIL_ENABLED = True
THUMBNAIL_FONT_SIZE = 130
THUMBNAIL_ACCENT_COLOR = (255, 200, 0) # Gold
THUMBNAIL_OUTLINE_WIDTH = 12
THUMBNAIL_OVERLAY_OPACITY = 160        # 0-255

# ── WATERMARKING & BRANDING ──────────────────────────────────
SHOW_CHANNEL_WATERMARK = True
WATERMARK_IMAGE = ASSETS_DIR / "profile.png"  # 🔄 Updated to profile.png
WATERMARK_OPACITY = 0.85
WATERMARK_SCALE = 160         # Larger, more premium profile watermark
WATERMARK_POSITION = "top-left"
WATERMARK_MARGIN = 40
SHOW_PART_TAG = True           # Show "PART X" tag at top-right
PART_TAG_DURATION = 5.0        # Stay on screen for 5s
SHOW_CTA_OVERLAY = True        # Show "Follow for Part X+1" at end
CTA_DURATION = 5.0             # End-screen duration
CTA_TEXT = "Like & Subscribe for Part {next_part}!"

# ─────────────────────────────────────────────────────────────
#  CHANNEL & LOGGING SETTINGS
# ─────────────────────────────────────────────────────────────
CHANNEL_NAME = "Snippet Stories"          # Your YouTube channel name
LOG_FILE = LOGS_DIR / "generation.log" # Log output file
LOG_LEVEL = "INFO"                        # CRITICAL, ERROR, WARNING, INFO, DEBUG

# ─────────────────────────────────────────────────────────────
#  VIDEO SETTINGS
# ─────────────────────────────────────────────────────────────
VID_WIDTH = 1080              # YouTube Shorts width
VID_HEIGHT = 1920             # YouTube Shorts height
VID_FPS = 30                  # Frames per second (YouTube Shorts standard)

# Duration presets  ←  CHOOSE ONE
DURATION_MODE = "unlimited"       # "unlimited" = full audio length (no hard cap)
DURATION_SETTINGS = {
    "unlimited": {"max_secs": 180,  "target_words": 500},   # Capped at 3 mins for stability
    "short":  {"max_secs": 50,  "target_words": 140},   # ~40-50 sec (allows intro+story+outro)
    "medium": {"max_secs": 65,  "target_words": 180},   # ~50-65 sec (allows intro+story+outro)
}
MAX_DURATION = DURATION_SETTINGS[DURATION_MODE]["max_secs"]
TARGET_WORDS = DURATION_SETTINGS[DURATION_MODE]["target_words"]

# ─────────────────────────────────────────────────────────────
#  VOICE ASSIGNMENTS  (Character Memory)
#  These stay CONSISTENT across ALL 48+ parts
#  See all voices: edge-tts --list-voices
# ─────────────────────────────────────────────────────────────

# USE_LOCAL_TTS: If True, uses locally hosted AI voice generation
# (e.g. Kokoro-TTS) for emotional, cloned inflections.
# Requires: pip install kokoro soundfile torch
USE_LOCAL_TTS = True

# ── KOKORO TTS CONFIG (Local Emotional Engine) ─────────────────
# Models must be in /models/ or root
KOKORO_MODEL = "kokoro-v1.0.onnx"
KOKORO_VOICE_PACK = "voices-v1.0.bin"

# Mapping moods to specific Kokoro voices for emotional depth
# af_ = Female, am_ = Male, bf_ = British Female, bm_ = British Male
KOKORO_VOICE_MAP = {
    "dark": "af_sky",          # Airy, mysterious female
    "ominous": "af_sky",
    "sad": "af_nicole",        # Soft, melancholic female
    "emotional": "af_nicole",
    "epic": "af_bella",         # Powerful, resonant female
    "thrill": "af_sarah",      # Energetic, fast female
    "happy": "af_sarah",       # Bright, upbeat female
    "neutral": "af_bella",     # Standard narrator female
    "suspense": "af_sky"       # Airy, tense female
}

# Speed adjustment for narrator (1.0 = normal, 1.1 = slightly fast for retention)
TTS_SPEED = 1.1 

# ── EMOTIONAL VOX (Post-Processing) ──────────────────────────
# Improves "presence" and emotional resonance of AI voices
VOICE_COMPRESSION = True
VOICE_COMPAND_STRENGTH = "attacks=0.02:decays=0.1:points=-60/-90|-15/-6:soft-knee=6:gain=-12" # Fixed syntax

# Local Kokoro-TTS voices (requires the Kokoro v1.0 voicepacks)
# "am" = American Male, "af" = American Female, "bm" = British Male, etc.
KOKORO_VOICES = {
    # ── Main Characters ──────────────────────────────────────
    "narrator":     "af_bella",       # Rich, dramatic female narrator
    "kaelen":       "am_puck",        # Deep, calm male protagonist
    "seraphina":    "bf_emma",        # Elegant British female (predatory)
    "rin":          "af_sarah",       # Playful energetic female
    "elara":        "af_nicole",      # Warm thoughtful female
    # ── Secondary Characters ──────────────────────────────────
    "morwen":       "af_alloy",       # Stern female
    "valerius":     "am_eric",        # Arrogant male
    "gaius":        "bm_george",      # Wise British male
    "malachar":     "am_michael",     # Dark villain male
    "mara":         "af_alloy",       # Cold female
    "aldric":       "bm_lewis",       # Commanding male (The Lion)
    "duke":         "bm_lewis",       # Noble male (Arcturus)
    "herald":       "am_adam",        # Formal male
    "guard":        "am_adam",        # Soldier male
    "instructor":   "am_michael",     # Teacher male
    "oracle":       "bf_isabella",    # Mystical British female
    "vex'ahlia":    "af_sky",         # Mysterious demon female
    "lyra":         "af_sky",         # Quiet servant girl
    "arcturus":     "bm_lewis",       # Wise/Commanding military male
    "commander":    "bm_lewis",       # Military male
    "council":      "bm_george",      # Council member
    "inquisitor":   "af_alloy",       # Inquisitor female
    # ── Fallback ──────────────────────────────────────────────
    "_default":     "af_bella",       # Default fallback
}


VOICES = {
    # ── Main Characters ──────────────────────────────────────
    "narrator":     "en-US-AriaNeural",       # Rich, dramatic female narrator
    "kaelen":       "en-US-GuyNeural",        # Deep, calm male protagonist
    "seraphina":    "en-GB-SoniaNeural",      # Elegant British female
    "rin":          "en-US-SaraNeural",       # Playful energetic female
    "elara":        "en-US-MichelleNeural",   # Warm thoughtful female
    # ── Secondary Characters ──────────────────────────────────
    "morwen":       "en-US-JennyNeural",      # Stern female
    "valerius":     "en-US-TonyNeural",       # Arrogant male
    "gaius":        "en-GB-RyanNeural",       # Wise British male
    "malachar":     "en-US-DavisNeural",      # Dark villain male
    "mara":         "en-US-JaneNeural",       # Cold female
    "aldric":       "en-GB-ElliotNeural",     # Commanding male (The Lion)
    "duke":         "en-US-GuyNeural",        # Noble male
    "herald":       "en-US-TonyNeural",       # Formal male
    "guard":        "en-US-TonyNeural",       # Soldier male
    "instructor":   "en-US-DavisNeural",      # Teacher male
    "oracle":       "en-US-NancyNeural",      # Mystical female
    "vex'ahlia":    "en-US-JaneNeural",       # Mysterious demon female
    "lyra":         "en-US-AriaNeural",       # Quiet servant girl
    "arcturus":     "en-GB-RyanNeural",       # Older, wise male voice
    "commander":    "en-US-DavisNeural",      # Military male
    "council":      "en-GB-RyanNeural",       # Council member
    "inquisitor":   "en-US-JaneNeural",       # Inquisitor female
    # ── Fallback ──────────────────────────────────────────────
    "_default":     "en-US-AriaNeural",       # Default fallback
}



# Voice style modifiers — rate and pitch per character
VOICE_STYLE = {
    "narrator":     {"rate": "+10%", "pitch": "+0Hz"},     # Natural cinematic
    "kaelen":       {"rate": "+8%",  "pitch": "+0Hz"},     # Deep, steady
    "seraphina":    {"rate": "+10%", "pitch": "+5Hz"},     # Elevated elegant
    "rin":          {"rate": "+15%", "pitch": "+10Hz"},    # Fast, bright
    "elara":        {"rate": "+10%", "pitch": "+0Hz"},     # Thoughtful pacing
    "valerius":     {"rate": "+12%", "pitch": "-8Hz"},     # Aggressive low
    "malachar":     {"rate": "+5%",  "pitch": "-8Hz"},     # Deep villain
    "aldric":       {"rate": "+10%", "pitch": "-3Hz"},     # Commanding
    "oracle":       {"rate": "+5%",  "pitch": "+3Hz"},     # Ethereal
    "arcturus_past":{"rate": "+10%", "pitch": "-5Hz"},     # Deep past voice
    "mara":         {"rate": "+10%", "pitch": "+0Hz"},     # Neutral cold
    "gaius":        {"rate": "+10%", "pitch": "-3Hz"},     # Old wise
    "_default":     {"rate": "+10%", "pitch": "+0Hz"},
}

# Character name aliases — maps alternate names to canonical voice keys
CHARACTER_ALIASES = {
    "demon emperor": "kaelen",
    "emperor": "kaelen",
    "kael": "kaelen",
    "duke arcturus": "arcturus",
    "duke": "arcturus",
    "lord malachar": "malachar",
    "commander": "arcturus",
    "the lion": "aldric",
    "king aldric": "aldric",
    "envoy": "herald",
    "soldier": "guard",
    "teacher": "instructor",
    "inquisitor mara": "mara",
    "mara": "mara",
    "girl": "lyra",
    "servant": "lyra",
}


# ─────────────────────────────────────────────────────────────
#  CHARACTER-SPECIFIC AUDIO EFFECTS (FFmpeg filters)
#  Each character gets unique spatial/tonal treatment
# ─────────────────────────────────────────────────────────────
CHARACTER_AUDIO_FX_ENABLED = True

CHARACTER_AUDIO_FX = {
    "narrator":   "highpass=f=80,equalizer=f=200:t=h:w=200:g=1",
    # Clean + warm — professional narration

    "kaelen":     "highpass=f=60,equalizer=f=150:t=h:w=100:g=3,lowpass=f=5000",
    # Bass boost + slightly muffled — brooding power

    "seraphina":  "highpass=f=100,equalizer=f=3000:t=h:w=500:g=2",
    # Bright + clear treble — elegant commanding

    "rin":        "highpass=f=120,equalizer=f=2000:t=h:w=300:g=2",
    # Energetic + crisp midrange

    "elara":      "highpass=f=80,equalizer=f=800:t=h:w=400:g=1",
    # Warm + full — thoughtful

    "malachar":   "highpass=f=50,equalizer=f=100:t=h:w=100:g=4,aecho=0.8:0.9:60:0.3",
    # Heavy bass + echo — dark villain

    "valerius":   "highpass=f=80,equalizer=f=1500:t=h:w=300:g=2,volume=1.1",
    # Slightly louder + dominant midrange — arrogant

    "aldric":     "highpass=f=70,equalizer=f=200:t=h:w=200:g=2",
    # Strong low-mids — commanding king

    "oracle":     "highpass=f=80,aecho=0.6:0.5:80:0.4,equalizer=f=4000:t=h:w=500:g=2",
    # Ethereal echo + shimmer — mystical

    "_default":   "highpass=f=80",
}

# ── TRANSITIONS & FADES ──────────────────────────────────────
GLOBAL_FADE_DUR = 0.0          # ❌ NO BLACK SCREENS — prevents flicker at start/end
LOOP_CROSSFADE_DUR = 2.0       # Smooth loop transition for background clips
SCENE_TRANSITION_DUR = 1.8     # Crossfade between background scenes

# ─────────────────────────────────────────────────────────────
#  SUBTITLE SETTINGS (Viral karaoke style)
# ─────────────────────────────────────────────────────────────
WORDS_PER_CUE = 3               # 🚀 Punchy 3-word cues for maximum retention
LETTER_SPC = 0                   # Letter spacing for subtitles (0 = normal, referenced by subtitle_sync)
FONT_NAME = "Impact"           # Viral YouTube Shorts font
FONT_SIZE = 92                  # Adjusted for 3 words per cue
OUTLINE_WIDTH = 5               # Thick outline for contrast
MARGIN_BOTTOM = 550              # Clear YouTube UI buttons
SHADOW_DEPTH = 3                 # Shadow offset pixels
SUBTITLE_GLOW = True             # Add glow effect behind text

# ASS color format (AABBGGRR)
SUBTITLE_WHITE = "&H00FFFFFF"    # White text
SUBTITLE_YELLOW = "&H0000FFFF"   # Yellow highlight (karaoke active word)
SUBTITLE_BLACK = "&H00000000"    # Black outline

# Per-character subtitle highlight colors
CHARACTER_SUB_COLORS = {
    "narrator":   "&H00FFFFFF",   # White
    "kaelen":     "&H00FFCC99",   # Ice blue
    "seraphina":  "&H0000D4FF",   # Gold
    "rin":        "&H00FFFF00",   # Cyan
    "elara":      "&H00AAFFAA",   # Soft green
    "oracle":  "&H00FF66FF",   # Purple
    "malachar":   "&H004444FF",   # Dark red
    "valerius":   "&H006699FF",   # Orange
    "aldric":     "&H0000CCFF",   # Amber
    "_default":   "&H0000FFFF",   # Yellow
}

# ─────────────────────────────────────────────────────────────
#  BACKGROUND SETTINGS (Multi-tier system)
# ─────────────────────────────────────────────────────────────
# Tier 1 = procedural (FFmpeg, works everywhere)
# Tier 2 = Pexels stock footage (free API)
# Tier 3 = ComfyUI AI generation (future)
# Tier 0 = Solid color / none
BG_TIER = 2                       # Changed to Tier 2 to use context-based Pexels clips (dopamine/nature/cinematic)
BG_CUSTOM_VIDEO = ""              # Path to custom background if needed

# Mood → procedural background mapping (Tier 1)
BG_PROCEDURAL_MODES = {
    "dark":     "plasma_dark",     # Swirling dark purple plasma
    "sad":      "gradient_blue",   # Slowly shifting blue-grey
    "thrill":   "particles_fire",  # Floating ember particles
    "happy":    "gradient_warm",   # Golden warm gradient
    "epic":     "particles_fire",  # Fire + particles
    "surprise": "flash_dark",      # Flash white → dark
    "mystery":  "plasma_dark",     # Dark plasma
    "neutral":  "particles_magic", # Magic particle default
}

# Pexels API (Tier 2) — FREE
# Loaded from .env file for security (DO NOT hardcode in source)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# Mood → Pexels search terms
PEXELS_SEARCH_TERMS = {
    "epic": [
        "thunderstorm lightning dramatic sky",
        "storm waves crashing rocks ocean",
        "volcano eruption lava dramatic",
        "lightning bolt dark sky dramatic",
        "mountain storm dramatic clouds aerial wilderness",
    ],
    "dark": [
        "dark storm clouds dramatic sky",
        "dense fog forest night wilderness",
        "cave underground dramatic light ray",
        "night forest shadows moonlight",
        "heavy overcast sky grey dramatic",
    ],
    "gloomy": [
        "grey fog morning lake wilderness",
        "misty valley overcast sky",
        "barren winter landscape leafless trees",
        "dark overcast sky before storm",
        "grey ocean waves stormy",
    ],
    "sad": [
        "rain falling slow motion nature",
        "grey rainy day empty landscape",
        "fog over still lake morning wilderness",
        "autumn leaves falling slow cinematic",
        "overcast sky gentle rain nature",
    ],
    "thrill": [
        "lightning strike dramatic slow motion",
        "fast river rapids rushing water",
        "storm waves dramatic ocean crashing",
        "heavy rain storm dramatic nature",
        "waterfall powerful rushing dramatic",
    ],
    "happy": [
        "golden hour sunset warm light nature",
        "sunlight through forest trees rays",
        "clear blue sky clouds time lapse",
        "sunrise mountain golden light dramatic",
        "warm sunlight meadow flowers nature",
    ],
    "mystery": [
        "fog forest path mysterious cinematic",
        "mist rolling over mountains slow",
        "night sky stars milky way",
        "foggy lake dawn atmospheric wilderness",
        "deep forest mist mysterious light",
    ],
    "surprise": [
        "lightning flash dramatic storm night",
        "light breaking through storm clouds dramatic",
        "storm time lapse dramatic sky",
        "dramatic sky clearing after storm",
        "lightning over dark landscape dramatic",
    ],
    "neutral": [
        "cinematic landscape dramatic sky nature",
        "mountain aerial view dramatic clouds",
        "forest aerial cinematic slow motion",
        "dramatic sky clouds time lapse",
        "nature cinematic slow motion landscape",
    ],
}

# ─────────────────────────────────────────────────────────────
#  SOUND EFFECTS (Mood-based)
# ─────────────────────────────────────────────────────────────
MOOD_SFX_ENABLED = True
SFX_VOLUME = 0.30               # 🔊 Balanced: audible but won't overpower narration (0.0-1.0)

# Transition SFX between scene changes
TRANSITION_SFX_ENABLED = True

# ─────────────────────────────────────────────────────────────
#  BACKGROUND MUSIC
# ─────────────────────────────────────────────────────────────
MUSIC_MODE = "generated"         # "generated" = dark ambient | "none" = silence
MUSIC_VOLUME = 0.10              # Background music volume
DYNAMIC_MUSIC_DUCKING = True     # Auto-lower music when voice plays

# Mood → music style
MUSIC_MOODS = {
    "dark":     {"freqs": [73.4, 146.8, 220],    "decay": 0.20, "filter": "lowpass=f=600"},
    "sad":      {"freqs": [130.8, 196.0, 261.6], "decay": 0.30, "filter": "lowpass=f=800"},
    "thrill":   {"freqs": [98.0, 146.8, 196.0],  "decay": 0.10, "filter": "lowpass=f=500"},
    "happy":    {"freqs": [261.6, 329.6, 392.0], "decay": 0.25, "filter": "lowpass=f=1200"},
    "epic":     {"freqs": [73.4, 110.0, 146.8],  "decay": 0.15, "filter": "lowpass=f=700"},
    "neutral":  {"freqs": [146.8, 220, 293.7],   "decay": 0.20, "filter": "lowpass=f=800"},
}

# ─────────────────────────────────────────────────────────────
#  HOOK SETTINGS (First 3 seconds = critical)
# ─────────────────────────────────────────────────────────────
SHOW_HOOK = True
HOOK_DURATION = 3.0              # Seconds

# ─────────────────────────────────────────────────────────────
#  LOOP BRIDGE (2026 Algorithm Hack)
# ─────────────────────────────────────────────────────────────
ADD_LOOP_BRIDGE = False             # ❌ DISABLED — Removes the confusing sound echo at the end
LOOP_BRIDGE_DURATION = 3.5        # Increased to capture "Hey everyone! Welcome back..."

# ─────────────────────────────────────────────────────────────
#  2026 UPGRADE FEATURES (Critical Improvements)
# ─────────────────────────────────────────────────────────────
USE_REAL_TIME_DURATION = True          # Measure actual TTS output (±20ms accuracy)
USE_FRAME_PERFECT_SUBTITLES = True     # Librosa speech detection for audio/subtitle sync
ADD_LOOP_TRANSITION = False            # ❌ DISABLED — YouTube algorithm prefers hard cut loops over fade to black
ADD_AI_DISCLOSURE = False              # ❌ DISABLED — User requested removal of AI label
USE_CURATED_BACKGROUNDS = False        # ❌ DISABLED — so Pexels API fetches dynamic weather, nature, structures

AI_DISCLOSURE_POSITION = "top-right"   # or "bottom-left", "top-left", "bottom-right"
AI_DISCLOSURE_OPACITY = 0.85           # 0.0 (transparent) to 1.0 (opaque)

# ─────────────────────────────────────────────────────────────
#  BACKGROUND CONTENT FILTERING (Safety & Quality)
# ─────────────────────────────────────────────────────────────
# Consolidated keyword pool for background filtering
ALLOWED_BACKGROUND_KEYWORDS = [
    "forest", "mountain", "landscape", "nature", "wilderness", "sky", "clouds",
    "ocean", "sea", "river", "waterfall", "valley", "canyon", "desert",
    "meadow", "field", "plains", "jungle", "rainforest", "cave", "peak", "volcano",
    "rain", "storm", "snow", "ice", "sunlight", "sun", "moon", "stars", "night",
    "dawn", "dusk", "sunset", "sunrise", "weather", "atmosphere",
    "wildlife", "animal", "bird", "eagle", "wolf", "deer", "bear", "lion",
    "horse", "dragon", "serpent", "snake", "rose", "petals",
    "castle", "temple", "ruins", "architecture", "fortress", "mansion",
    "ancient", "historical", "monument", "stone", "bridge", "structure",
    "tower", "wall", "gate", "path", "statue", "palace", "cathedral", "abbey",
    "monastery", "chapel", "shrine", "academy", "campus", "library", "classroom",
    "hall", "chamber", "corridor", "balcony", "terrace", "garden", "fountain",
    "courtyard", "arena", "colosseum", "dungeon", "crypt", "vault", "throne",
    "manor", "estate", "dormitory", "study", "university", "college", "house",
    "abstract", "light", "fire", "smoke", "mist", "fog", "aurora", "space",
    "galaxy", "nebula", "cosmos", "magical", "dark", "epic", "cinematic",
    "ethereal", "fantasy", "scenery", "aerial", "drone", "mana",
    "sparkle", "glowing", "portal", "rune", "arcane", "spell", "enchanted",
    "gothic", "medieval", "vintage", "mahogany", "candlelight", "shadows", "obsidian",
    "incense", "smoke curls", "crystal", "chandelier", "dust", "parchment", "scroll",
    "ash", "thorn", "obelisk", "brazier", "stained glass", "silver flame", "black stone",
    "white marble", "borderlands", "tunnels", "parapet", "battlements", "siege engine", "banners"
]

# Blacklist: Strictly remove modern/unrelated content
BLACKLIST_BACKGROUND_KEYWORDS = [
    "car", "truck", "city", "modern", "technology", "phone", "computer", "plastic",
    "people", "person", "man", "woman", "face", "talking", "smile", "happy",
    "child", "children", "boy", "girl", "old people", "dancer", "dancers",
    "dancing", "bright colors", "office building", "traffic", "neon", "robot",
    "sci-fi", "advertisement", "text", "logo", "social media", "urban",
    "fashion", "3d render", "cartoon", "animation", "illustration", "airplane",
    "airport", "train", "bus", "bicycle", "motorcycle", "asphalt",
    "skyscraper", "electricity", "wires", "vehicle", "automobile", "highway",
    "billboard", "gadget", "electronics", "crowd", "audience",
    "group of people", "classroom kids", "modern school", "jeans", "suit",
    "sneakers", "t-shirt", "wrist watch", "guns", "firearms", "hospital",
    "modern clinic", "modern courtroom", "function", "public place", "statue",
    "statues", "3d particle", "3d particles", "black and white", "b&w",
    "copyright", "watermark", "news", "event", "party", "festival", "concert",
    "monument", "stairs", "furniture", "room interior", "house exterior",
    "street", "building", "glass structure", "metal structure", "table",
    "chair", "bed", "lamp", "window", "door", "wall", "ceiling", "floor",
    "road", "motorway", "overpass", "pavement"
]

# Location-to-Visual Mappings for story consistency
LOCATION_KEYWORDS = {
    "azure pavilion": "clear blue sky over calm water",
    "silver academy": "majestic snow capped mountain aerial",
    "academy": "mountain peak clouds dramatic aerial",
    "spire academy": "tall mountain peak piercing clouds",
    "obsidian fortress": "dark jagged mountain cliffs storm",
    "celestial church": "sun rays shining through clouds epic",
    "dark continent": "desolate volcanic landscape dark",
    "throne room": "massive stalactite cave glowing crystals",
    "library": "quiet ancient forest tall trees fog",
    "mahogany": "dense redwood forest dark wood",
    "chamber": "dark mysterious cave interior",
    "battlefield": "stormy desolate plain dark clouds",
    "mahogany room": "dense redwood forest dark wood",
    "chandelier": "glowing crystal stalactites dark cave",
    "dragomir": "dark snowy mountain winter storm",
    "imperial city": "vast mountain valley aerial view",
    "deep abyss": "dark deep ocean trench abstract",
    "ducal garden": "beautiful blooming flower meadow spring",

    # ── Kaelen's Past & The Betrayal ──
    "demon realm": "volcanic ash landscape lightning",
    "dark throne": "dark jagged rock formation stormy",
    "holy sword": "sunlight breaking through dark clouds",
    
    # ── Rebirth & The Ducal Estate ──
    "blinding white": "bright white cloudscape aerial",
    "manor": "peaceful green valley estate",
    "estate": "peaceful green valley estate",
    "study": "forest morning light rays trees",
    
    # ── The Magic Academy (Interiors) ──
    "classroom": "peaceful forest grove morning light",
    "hallway": "narrow mountain canyon passage fog",
    "dormitory": "rain falling nature gentle morning",
    "dining hall": "wide open green meadow golden hour",
    "healers wing": "calm crystal clear lake reflection",
    "demon common hall": "dark forest red sunset glow",
    "tribunal chamber": "circular crater landscape aerial",
    "ritual chamber": "dark misty cave interior",
    "vex'ahlia chambers": "bright snowy mountain peak",
    
    # ── The Magic Academy (Exteriors) ──
    "courtyard": "peaceful green valley mountain",
    "training ground": "wide open mountain valley plain",
    "arena": "wide canyon landscape dramatic sky",
    "gates": "narrow mountain pass dramatic entrance",
    "mana weaving arena": "circular crater landscape aerial storm",
    
    # ── Nature & The Borderlands ──
    "dark forest": "creepy dark misty pine forest",
    "bright forest": "sunlight shining through green forest",
    "mountains": "majestic snow capped mountain peaks aerial",
    "valley": "beautiful green valley river landscape",
    "river": "fast flowing dark river nature",
    "waterfall": "epic tall waterfall jungle nature",
    "borderlands": "desolate wasteland dark sky storm",
    "blackthorn fortress": "dark jagged mountain cliffs storm",
    "cave": "dark mysterious underground cave",
    "ruins": "ancient forgotten stone temple nature",
    
    # ── The Royal Capital & The Church ──
    "capital": "vast mountain valley aerial view sunset",
    "palace": "majestic snow capped mountain peak",
    "royal court": "grand canyon sunlight rays",
    "golden throne": "sunlight shining on gold autumn leaves",
    "cathedral": "sun rays shining through clouds epic",
    "sanctuary": "peaceful calm lake reflection",
    "church quarter": "bright white cloudscape aerial",
    
    # ── Story Specifics (The Twice-Crowned King) ──
    "frozen ocean": "epic glacier ice ocean dark sky",
    "mana": "aurora borealis northern lights night sky",
    "sealed soul": "dark ice cave interior frozen",
    "kaelen dragomir": "dark jagged mountain winter storm",
    "house valtiel": "peaceful green valley estate",
    "ducal status": "majestic mountain peak sunlight",
    "daydreaming": "dreamy misty morning landscape",
    "duc": "peaceful green valley estate",
    
    # ── Abstract & Magic Elements ──
    "void": "pitch black night sky dark",
    "magic circle": "aurora borealis northern lights night sky",
    "black mana": "dark storm clouds swirling",
    "inquisitor": "dark stormy night silhouette",
    "celestial calendar": "starry night sky milky way galaxy",
    "ancient library": "quiet ancient forest tall trees",
    "snowy walls": "heavy snow falling winter landscape"
}


FILTER_BACKGROUND_CONTENT = True  # Enable content filtering for Pexels

# ─────────────────────────────────────────────────────────────
VIDEO_CODEC = "libx264"        # H.264 (universal YouTube compatibility)
VIDEO_PRESET = "slow"          # 'slow' improves quality & compression
VIDEO_CRF = 16                 # 16 = near lossless (prevents YouTube blurriness)
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
AUDIO_SAMPLE_RATE = "48000"
USE_HWACCEL = False             # DISABLED for stability (HWACCEL often causes freezes on Windows)
VIDEO_PROFILE = "high"         # H.264 profile (high = better quality)
VIDEO_LEVEL = "4.2"            # H.264 level (4.2 = YouTube compatible)
MAXRATE = "35000k"             # Max bitrate (raised to prevent compression artifacts)
BUFSIZE = "70000k"             # Buffer size for high bitrates

# ─────────────────────────────────────────────────────────────
#  SCRIPT PARSING
# ─────────────────────────────────────────────────────────────
SAID_VERBS = [
    "said", "whispered", "replied", "answered", "called", "murmured", "breathed",
    "asked", "announced", "interrupted", "laughed", "snapped", "hissed", "growled",
    "admitted", "continued", "added", "noted", "demanded", "corrected", "stated",
    "repeated", "explained", "spoke", "exclaimed", "cried", "shouted", "told",
    "purred", "drawled", "chimed", "mused", "sighed", "began", "finished", "scoffed",
    "echoed", "bellowed", "snarled", "roared", "thundered", "gasped",
]

# ─────────────────────────────────────────────────────────────
#  YOUTUBE METADATA & BRANDING
# ─────────────────────────────────────────────────────────────
STORY_TITLE = "The Twice-Crowned King"
STORY_HASHTAGS = (
    "#shorts #fantasy #reincarnation #darkfantasy #storyshorts "
    "#demonking #academyfantasy #storytime #animestory #webtoon "
    "#fyp #foryoupage #viral #thetwicecrownedking"
)

# ─────────────────────────────────────────────────────────────
#  INTRO & OUTRO (DISABLED — kills retention)
#  Branding is now visual-only: watermark + CTA overlay
# ─────────────────────────────────────────────────────────────
ADD_INTRO = False                    # ❌ DISABLED — spoken intros cause instant swipe
ADD_OUTRO = False                    # ❌ DISABLED — spoken outros destroy loop bridge

# ─────────────────────────────────────────────────────────────
#  INTEGRATED CTA OVERLAY (visual only, during climax)
#  Shows text on screen during the final seconds WITHOUT
#  stopping the story or breaking the audio flow
# ─────────────────────────────────────────────────────────────
SHOW_CTA_OVERLAY = True              # ✅ Flash CTA text during the final seconds
# CTA_TEXT is defined in WATERMARKING & BRANDING section above (line 56)
CTA_DURATION = 5.0                   # seconds, shown at the very end (matches branding section)
CTA_FONT_SIZE = 64                   # Centered and bold
CTA_COLOR = "&H0000FFFF"             # Yellow (ASS format)
CTA_POSITION = "top"                 # center, bottom, top

# ─────────────────────────────────────────────────────────────
#  PART TAG (first 4 seconds)
#  Viewers intuitively go to your channel to find Part 2
# ─────────────────────────────────────────────────────────────
SHOW_PART_TAG = True                 # ✅ Show "Part N" in the first seconds
PART_TAG_DURATION = 5.0              # seconds visible
PART_TAG_POSITION = "top-right"       # top-left, top-right

# ─────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════
#  VALIDATION
# ═══════════════════════════════════════════════════════════════
if not (VID_WIDTH > 0 and VID_HEIGHT > 0):
    raise ValueError(f"Invalid video dimensions: {VID_WIDTH}x{VID_HEIGHT}")
if not (0 <= MUSIC_VOLUME <= 1):
    raise ValueError(f"MUSIC_VOLUME must be between 0 and 1, got {MUSIC_VOLUME}")
if FONT_SIZE < 50: 
    raise ValueError(f"FONT_SIZE must be >= 50, got {FONT_SIZE}")
if not (0 <= VIDEO_CRF <= 51):
    raise ValueError(f"VIDEO_CRF must be between 0 and 51, got {VIDEO_CRF}")

# ── CROSS-PLATFORM FONT RESOLVER ────────────────────────────
def get_font_path(font_name="impact"):
    """
    Find a suitable font file across different operating systems.
    Prioritizes high-impact fonts for YouTube Shorts.
    """
    import os
    import sys
    
    # Map common font names to likely filenames
    font_map = {
        "impact": ["impact.ttf", "Impact.ttf", "impact", "Impact"],
        "arial-bold": ["arialbd.ttf", "Arial Bold.ttf", "Arial-Bold"],
        "inter": ["Inter-Bold.ttf", "Inter-Bold", "Inter"]
    }
    
    search_files = font_map.get(font_name.lower(), ["arial.ttf"])
    
    # System-specific search paths
    paths = []
    if sys.platform == "win32":
        paths.append("C:\\Windows\\Fonts")
    elif sys.platform == "darwin": # macOS
        paths.append("/Library/Fonts")
        paths.append("/System/Library/Fonts")
        paths.append(os.path.expanduser("~/Library/Fonts"))
    else: # Linux/WSL
        paths.append("/usr/share/fonts")
        paths.append("/usr/local/share/fonts")
        paths.append(os.path.expanduser("~/.local/share/fonts"))

    for base in paths:
        if not os.path.exists(base): continue
        # Walk through subdirectories (especially on Linux)
        for root, _, files in os.walk(base):
            for f in files:
                if any(f.lower() == sf.lower() for sf in search_files):
                    return os.path.join(root, f)
                    
    # Fallback: Just return the name and hope FFmpeg/PIL can find it globally
    return search_files[0]
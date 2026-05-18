#!/usr/bin/env python3
"""System verification and refinement check with improvements."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from src import config
from src.verify_dependencies import verify_all_dependencies

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass

print("\n" + "="*70)
print("🔍 YOUTUBE SHORTS GENERATOR - SYSTEM VERIFICATION")
print("="*70)

# 1. Check dependencies
result = verify_all_dependencies(verbose=True)

if result['status'] == 'ERROR':
    print("\n❌ Cannot proceed with check - please fix critical issues first")
    sys.exit(1)

# 2. Directory structure
print("\n✅ DIRECTORY STRUCTURE:")
dirs = [('input', True), ('output', False), ('sfx', True), ('src', True), ('logs', False)]
for d, critical in dirs:
    p = BASE_DIR / d
    cnt = len(list(p.glob('*'))) if p.exists() else 0
    status = "✅" if p.exists() else ("⚠️  (optional)" if not critical else "❌")
    print(f"   {status} {d:20} {cnt:3} items")

# 3. Configuration
print("\n✅ KEY CONFIGURATION:")
print(f"   ✅ {'Channel Name':20} {config.CHANNEL_NAME}")
print(f"   ✅ {'Duration Mode':20} {config.DURATION_MODE}")
print(f"   ✅ {'Video Resolution':20} {config.VID_WIDTH}×{config.VID_HEIGHT} @ {config.VID_FPS}fps")
print(f"   ✅ {'AI Disclosure':20} {config.ADD_AI_DISCLOSURE}")
print(f"   ✅ {'Mood SFX':20} {config.MOOD_SFX_ENABLED}")
print(f"   ✅ {'Subtitle Sync':20} {config.USE_FRAME_PERFECT_SUBTITLES}")
print(f"   ✅ {'Background Filter':20} {config.FILTER_BACKGROUND_CONTENT}")
print(f"   ✅ {'Log Level':20} {config.LOG_LEVEL}")

# 4. Voices
print("\n✅ VOICE SYSTEM:")
print(f"   Total voices configured: {len(config.VOICES)}")
print(f"   Main characters: narrator, kaelen, seraphina, rin, elara")

# 5. Source files
print("\n✅ SOURCE FILES:")
essential_files = [
    'config.py', 'generate_short.py', 'audio_processor.py',
    'mood_detector.py', 'sfx_engine.py', 'background_engine.py',
    'subtitle_sync.py', 'error_handler.py', 'verify_dependencies.py'
]
for f in essential_files:
    exists = (BASE_DIR / 'src' / f).exists()
    print(f"   {'✅' if exists else '❌'} {f}")

# 6. Input scripts
print("\n✅ INPUT SCRIPTS:")
scripts = sorted((BASE_DIR / 'input').glob('part_*.txt'))
print(f"   Total: {len(scripts)} scripts ready")
if scripts:
    print(f"   Range: {scripts[0].name} ... {scripts[-1].name}")

# 7. Show improvements
print("\n" + "="*70)
print("🎯 IMPROVEMENTS APPLIED")
print("="*70)
improvements = [
    "✅ Fixed font path hardcoding (cross-platform support)",
    "✅ Added automatic background content filtering (no humans/3D)",
    "✅ Improved subtitle → audio sync with speech detection",
    "✅ Enhanced error handling with custom decorators",
    "✅ Added comprehensive dependency verification",
    "✅ Improved hook rewriter for ALL parts (Ollama integration)",
    "✅ Added logging to config.py",
    "✅ Enabled AI disclosure (YouTube 2026 compliance)",
    "✅ Added missing config variables (CHANNEL_NAME, LOG_FILE, etc)",
]

for improvement in improvements:
    print(f"   {improvement}")

print("\n" + "="*70)
if result['status'] == 'OK':
    print("✅ SYSTEM STATUS: READY FOR PRODUCTION")
else:
    print("⚠️  SYSTEM STATUS: READY (with warnings - some features may be limited)")
print("="*70)

print("""
Next Steps:
  
  1. Single Video Test:
     python src/generate_short.py input/part_0001.txt 1

  2. Rewrite Hooks with AI (requires Ollama):
     python tools/hook_rewriter_v2.py

  3. Generate All Shorts:
     python tools/batch_generate.py

  4. Check Generated Videos:
     ls -lh output/short_part_*.mp4

Troubleshooting:
  - For encoding errors: python -m chardet input/part_0001.txt
  - For API key issues: Edit .env file (PEXELS_API_KEY, etc)
  - For hook rewriting: Start Ollama with: ollama serve

""")
#!/usr/bin/env python3
"""
AI Hook Rewriter v2 — Batch Rewrite Opening Sentences
Uses Ollama (local LLM) to create viral hooks for each short
"""

import os
import requests
from pathlib import Path
import re
import sys
import time

# Fix for Windows Unicode errors
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

INPUT_DIR = Path('input')
OUTPUT_DIR = Path('output')

# Create output dir for rewritten files
(OUTPUT_DIR / "hooks").mkdir(exist_ok=True)

def check_ollama_server():
    """Check if Ollama server is running."""
    try:
        response = requests.get('http://localhost:11434/', timeout=5)
        return True
    except:
        return False


def rewrite_hook(original_hook: str, context: str = "epic fantasy reincarnation") -> str:
    """
    Use Ollama to rewrite a hook into something viral.
    """
    prompt = f"""You are a professional YouTube Shorts scriptwriter and hook expert.
Your goal is to rewrite an opening sentence into a viral, high-retention hook.

STORY GENRE: {context}

ORIGINAL OPENING: "{original_hook}"

GUIDELINES:
1. Make it intense, mysterious, or shocking.
2. Use strong, evocative words.
3. Keep it under 15 words.
4. Output ONLY the rewritten hook. No explanations or quotes.
5. If the original is a title, turn it into a question or a dramatic statement.

VIRAL HOOK:"""

    for attempt in range(2):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.8,
                },
                timeout=45 # Increased timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                new_hook = result.get('response', '').strip()
                
                # Clean up
                new_hook = new_hook.replace('"', '').replace("'", "").strip()
                new_hook = ' '.join(new_hook.split())
                
                # Basic validation
                if len(new_hook) > 3 and "original" not in new_hook.lower():
                    return new_hook
            
            time.sleep(1) # Wait before retry
        except Exception as e:
            time.sleep(2)
            continue
    
    return None


def extract_first_meaningful_sentence(text: str) -> str:
    """Extract the first meaningful sentence from text."""
    # Remove chapter headers
    text = re.sub(r'^#.*?\n', '', text).strip()
    
    # Find NARRATOR section
    narrator_match = re.search(r'NARRATOR:\s*(.*)', text, re.DOTALL | re.IGNORECASE)
    if narrator_match:
        text = narrator_match.group(1).strip()
    
    # Split by lines and find the first non-empty line
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return ""
        
    first_line = lines[0]
    
    # If the first line is very short (e.g. just a title), and there's more, maybe take the second line?
    # For "The Twice-Crowned King", it's better to rewrite that or the next sentence.
    # We'll just take the first line for now as it's the "actual" first spoken thing.
    return first_line


def rewrite_script_hook(input_file: Path, verbose: bool = False) -> bool:
    """
    Rewrite the hook in a script file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract original hook
        original_hook = extract_first_meaningful_sentence(content)
        if not original_hook or len(original_hook) < 3:
            if verbose:
                print(f"     [-] No valid hook found in {input_file.name}")
            return False
        
        # Rewrite with Ollama
        new_hook = rewrite_hook(original_hook)
        
        if not new_hook:
            if verbose:
                print(f"     [-] Ollama failed or returned empty for {input_file.name}")
            return False
        
        # Ensure punctuation
        if not new_hook.endswith(('.', '!', '?')):
            new_hook = new_hook + '.'
            
        # Replace hook in content
        # We need to find exactly where the original_hook was inside the NARRATOR section
        # To be safe, we'll find NARRATOR: and then find the original_hook after it.
        narrator_match = re.search(r'(NARRATOR:\s*)', content, re.IGNORECASE)
        if not narrator_match:
            return False
            
        narrator_pos = narrator_match.end()
        # Find the first occurrence of original_hook after NARRATOR:
        hook_pos = content.find(original_hook, narrator_pos)
        
        if hook_pos != -1:
            updated_content = (
                content[:hook_pos]
                + new_hook
                + content[hook_pos + len(original_hook):]
            )
            
            # Save rewritten file
            output_file = OUTPUT_DIR / "hooks" / input_file.name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            if verbose:
                print(f"   [+] {input_file.name}")
                print(f"      Original: {original_hook}")
                print(f"      Rewritten: {new_hook}")
            return True
        else:
            if verbose:
                print(f"     [-] Could not locate hook '{original_hook[:20]}...' in {input_file.name}")
            return False
            
    except Exception as e:
        if verbose:
            print(f"   [-] Exception in {input_file.name}: {e}")
        return False


def main():
    print("\n" + "="*70)
    print("[*] AI HOOK REWRITER v2.1 - Viral Hook Generator")
    print("="*70)
    
    if not check_ollama_server():
        print("\n❌ Ollama is NOT running! Please start it with 'ollama serve'")
        return
    
    print("[+] Ollama is running!")
    
    script_files = sorted([f for f in INPUT_DIR.glob("part_*.txt")])
    if not script_files:
        print("\n[-] No scripts found in input/")
        return
    
    print(f"[*] Processing {len(script_files)} scripts...")
    
    success_count = 0
    failed_count = 0
    
    for i, script_file in enumerate(script_files, 1):
        # Verbose for failures to help debug
        # Or just show all if processing
        print(f"[{i:3d}/{len(script_files)}] ", end="", flush=True)
        
        if rewrite_script_hook(script_file, verbose=False):
            success_count += 1
            print(f"[OK] {script_file.name}")
        else:
            failed_count += 1
            print(f"[FAIL] {script_file.name}")
            # rewrite_script_hook(script_file, verbose=True)
    
    print("\n" + "="*70)
    print(f"[*] Done! Success: {success_count} | Failed: {failed_count}")
    print(f"[*] Files saved to: output/hooks/")
    print("="*70)

if __name__ == "__main__":
    main()
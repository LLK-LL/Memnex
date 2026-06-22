#!/usr/bin/env python3
"""Generate all voiceover audio for AI Tech News Flash video using edge-tts."""

import asyncio
import subprocess
import sys
import os

VOICE = "zh-CN-YunxiNeural"
RATE = "+30%"  # Fast pace for news flash style
OUTPUT_DIR = "assets/audio"

# Script template - edit these for each episode
# Rule: NO "绗琗鏉?, NO time filler words, just content directly
SCRIPTS = {
    "intro": "AI蹇姤锛寋date}锛屾渶鐑祫璁€?,
    "card1": "{headline1}銆倇desc1}",
    "card2": "{headline2}銆倇desc2}",
    "card3": "{headline3}銆倇desc3}",
    "card4": "{headline4}銆倇desc4}",
    "card5": "{headline5}銆倇desc5}",
    "outro": "浠ヤ笂灏辨槸鏈湡 AI 蹇姤銆傚叧娉ㄦ嫇鎵戝悓瀛︼紝涓嬫湡瑙併€?,
}

async def generate_audio(text, output_path, voice=VOICE, rate=RATE):
    """Generate a single audio file with edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
    print(f"  Generated: {output_path}")

def get_duration(filepath):
    """Get audio duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", filepath],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # TODO: Replace with actual episode content
    date = "2026骞?鏈?鏃?
    headlines = {
        "1": ("Anthropic 璁?Claude 瀛︿細浜嗗仛姊?, "Claude 鍙湪浼氳瘽闂撮殭鍥為【鍘嗗彶璁板綍锛屽彂鐜拌嚜韬敊璇ā寮忓苟鑷垜鏀硅繘"),
        "2": ("xAI 骞跺叆 SpaceX 鏀瑰悕 SpaceXAI", "Elon Musk 瀹ｅ竷 xAI 涓嶅啀鐙珛锛屽悓鏃朵笌 Anthropic 杈炬垚绠楀姏鍚堜綔"),
        "3": ("OpenAI 鑱斿悎 AMD 鍜?NVIDIA 鍙戝竷 MRC 鍗忚", "鎻愬崌澶ц妯?AI 璁粌闆嗙兢鐨?GPU 缃戠粶鎬ц兘涓庡脊鎬?),
        "4": ("Musk 璇?Altman 搴鍏抽敭璇佷汉闃舵", "Zilis 鍑哄涵浣滆瘉锛岄偖浠舵洕鍏?Musk 鏇捐鍒掑皢 OpenAI 绾冲叆 Tesla"),
        "5": ("43% 缇庡浗浜鸿涓烘暟鎹腑蹇冩帹楂樹簡鐢佃垂", "Pew Research 璋冩煡鏄剧ず鏁版嵁涓績鑳借€楀凡鎴愪袱鍏氬叡璇嗚棰?),
    }

    # Generate all audio files
    tasks = []

    intro_text = SCRIPTS["intro"].format(date=date)
    tasks.append(generate_audio(intro_text, f"{OUTPUT_DIR}/intro.mp3"))

    for i, (headline, desc) in headlines.items():
        card_text = SCRIPTS[f"card{i}"].format(**{f"headline{i}": headline, f"desc{i}": desc})
        tasks.append(generate_audio(card_text, f"{OUTPUT_DIR}/card{i}.mp3"))

    tasks.append(generate_audio(SCRIPTS["outro"], f"{OUTPUT_DIR}/outro.mp3"))

    await asyncio.gather(*tasks)

    # Print durations for timing reference
    print("\n馃搳 Audio durations (for HyperFrames timing):")
    total = 0
    for name in ["intro", "card1", "card2", "card3", "card4", "card5", "outro"]:
        path = f"{OUTPUT_DIR}/{name}.mp3"
        if os.path.exists(path):
            dur = get_duration(path)
            total += dur
            print(f"  {name}: {dur:.1f}s")
    print(f"  TOTAL: {total:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())

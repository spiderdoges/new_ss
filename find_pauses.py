import subprocess
import re
import datetime

# 👇 Apni file ka naam yahan daal
INPUT_FILE = "slowproductivity.m4a"
MIN_CHAPTER_GAP = 180  # 🔥 3 minute (180 seconds) ka minimum gap rule

def format_time(seconds):
    """Seconds ko proper HH:MM:SS format mein convert karta hai"""
    return str(datetime.timedelta(seconds=int(seconds)))

def find_timeline_silences(filename, min_silence_len=2.5, silence_thresh="-35dB"):
    print(f"🕵️‍♂️ Bhai, file scan ho rahi hai... Thoda wait kar!")
    
    # FFmpeg command to detect silence
    cmd = [
        "ffmpeg",
        "-i", filename,
        "-af", f"silencedetect=noise={silence_thresh}:d={min_silence_len}",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stderr

    silences = []
    matches = re.finditer(r"silence_start:\s+([\d\.]+).*?silence_duration:\s+([\d\.]+)", output, re.DOTALL)
    
    for match in matches:
        start_time = float(match.group(1))
        duration = float(match.group(2))
        silences.append({"start": start_time, "duration": duration})

    if not silences:
        print("⚠️ Koi lamba pause nahi mila bhai! Threshold adjust karni padegi.")
        return

    # CHRONOLOGICAL SORTING (Start se End tak)
    timeline_silences = sorted(silences, key=lambda x: x["start"])

    # 🔥 THE 3-MINUTE FILTER LOGIC 🔥
    valid_chapters = []
    last_valid_time = 0.0

    for s in timeline_silences:
        gap = s["start"] - last_valid_time
        if gap >= MIN_CHAPTER_GAP:
            valid_chapters.append(s)
            last_valid_time = s["start"]  # Update kar diya naye chapter ka time

    print(f"\n✅ Total {len(valid_chapters)} Legit Chapters mile (3 Min rule passed).")
    print("-" * 80)
    
    for i, s in enumerate(valid_chapters):  
        proper_time = format_time(s['start'])
        
        # Ye line batayegi ki pichle cut se ye chapter kitna lamba tha
        if i == 0:
            chapter_length = format_time(s["start"])
        else:
            chapter_length = format_time(s["start"] - valid_chapters[i-1]["start"])
            
        print(f"Chapter {i+1:02d} Start ✂️: {proper_time} | Chapter Size: ~{chapter_length} | Pause Lamba Kitna: {s['duration']:5.2f} sec")

if __name__ == "__main__":
    find_timeline_silences(INPUT_FILE)
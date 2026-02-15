#!/usr/bin/env python3
"""
Sync TTS audio to subtitle timing
Usage: sync_tts.py <translated_srt> <work_dir> <tts_engine> <target_lang>
"""
import sys
import os
import json
import re
import subprocess

def parse_srt(srt_file):
    """Parse SRT file and return segments with timing"""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    segments = []
    for i, block in enumerate(content.strip().split('\n\n')):
        lines = block.split('\n')
        if len(lines) >= 3:
            text = '\n'.join(lines[2:]).strip()
            m = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', lines[1])
            if m:
                h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
                start = h1*3600 + m1*60 + s1 + ms1/1000
                end = h2*3600 + m2*60 + s2 + ms2/1000
                duration = end - start
                segments.append({
                    'index': i,
                    'text': text,
                    'start': start,
                    'end': end,
                    'duration': duration
                })
    return segments

def generate_tts(seg, work_dir, tts_engine, target_lang, voice_profile=None):
    """Generate TTS for a single segment"""
    output_file = f"{work_dir}/raw_{seg['index']:03d}.wav"

    if tts_engine == 'voicebox' and voice_profile:
        # Use voicebox for voice cloning
        voicebox_script = os.path.expanduser("~/.claude/skills/voicebox/scripts/voicebox.py")
        subprocess.run(
            ['uv', 'run', voicebox_script, 'generate', voice_profile, seg['text'], '--quality', 'high'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        import shutil
        shutil.copy('/tmp/voicebox_output.wav', output_file)
    elif tts_engine == 'kokoro':
        kokoro_py = os.path.expanduser("~/miniconda3/envs/kokoro/bin/python3")
        kokoro_script = os.path.expanduser("~/.claude/skills/tts/scripts/kokoro_tts.py")
        subprocess.run(
            [kokoro_py, kokoro_script, seg['text'], 'zf_001'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.run(['mv', '/tmp/kokoro_out.wav', output_file], check=True)
    else:
        voice_map = {
            'chinese': 'zh-CN-YunxiNeural', 'zh': 'zh-CN-YunxiNeural',
            'spanish': 'es-ES-AlvaroNeural', 'es': 'es-ES-AlvaroNeural',
            'french': 'fr-FR-HenriNeural', 'fr': 'fr-FR-HenriNeural',
            'japanese': 'ja-JP-KeitaNeural', 'ja': 'ja-JP-KeitaNeural',
            'german': 'de-DE-ConradNeural', 'de': 'de-DE-ConradNeural',
            'italian': 'it-IT-DiegoNeural', 'it': 'it-IT-DiegoNeural',
            'portuguese': 'pt-BR-AntonioNeural', 'pt': 'pt-BR-AntonioNeural',
            'korean': 'ko-KR-InJoonNeural', 'ko': 'ko-KR-InJoonNeural',
            'russian': 'ru-RU-DmitryNeural', 'ru': 'ru-RU-DmitryNeural'
        }
        voice = voice_map.get(target_lang, 'zh-CN-YunxiNeural')
        temp_mp3 = f"{work_dir}/temp_{seg['index']:03d}.mp3"
        subprocess.run(
            ['edge-tts', '--voice', voice, '--text', seg['text'], '--write-media', temp_mp3],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ['ffmpeg', '-i', temp_mp3, output_file, '-y'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        os.remove(temp_mp3)

    return output_file

def get_audio_duration(audio_file):
    """Get audio duration in seconds"""
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', audio_file],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def sync_audio(raw_file, target_duration, work_dir, index):
    """Sync audio to target duration using speed adjustment"""
    actual_duration = get_audio_duration(raw_file)
    synced_file = f"{work_dir}/synced_{index:03d}.wav"
    speed_factor = actual_duration / target_duration

    if speed_factor > 1.05 or speed_factor < 0.95:  # More than 5% difference
        if speed_factor > 2.0:
            atempo1, atempo2 = 2.0, speed_factor / 2.0
            filter_str = f"atempo={atempo1},atempo={atempo2}"
        elif speed_factor < 0.5:
            atempo1, atempo2 = 0.5, speed_factor / 0.5
            filter_str = f"atempo={atempo1},atempo={atempo2}"
        else:
            filter_str = f"atempo={speed_factor}"

        subprocess.run(
            ['ffmpeg', '-i', raw_file, '-filter:a', filter_str, synced_file, '-y'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f"  Segment {index+1}: Adjusted speed {speed_factor:.2f}x ({actual_duration:.2f}s → {target_duration:.2f}s)")
    else:
        subprocess.run(['cp', raw_file, synced_file])
        print(f"  Segment {index+1}: Perfect timing ({actual_duration:.2f}s ≈ {target_duration:.2f}s)")

    # Trim to exact duration
    final_file = f"{work_dir}/final_{index:03d}.wav"
    subprocess.run(
        ['ffmpeg', '-i', synced_file, '-t', str(target_duration), '-ar', '44100', '-ac', '2', final_file, '-y'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return final_file

def build_timeline(segments, work_dir):
    """Build timeline with silence gaps"""
    # Get absolute path for work_dir
    abs_work_dir = os.path.abspath(work_dir)
    concat_file = f"{abs_work_dir}/concat_list.txt"

    with open(concat_file, 'w') as f:
        last_end = 0
        for seg in segments:
            gap = seg['start'] - last_end
            if gap > 0.01:
                silence_file = f"{abs_work_dir}/silence_{seg['index']:03d}.wav"
                subprocess.run(
                    ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo',
                     '-t', str(gap), silence_file, '-y'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                f.write(f"file '{silence_file}'\n")
                print(f"  Added {gap:.2f}s silence before segment {seg['index']+1}")

            # Use absolute path for final file
            abs_final_file = os.path.abspath(seg['final_file'])
            f.write(f"file '{abs_final_file}'\n")
            last_end = seg['end']

    print(f"✅ Timeline built with {len(segments)} segments")
    return concat_file

def main():
    if len(sys.argv) < 5:
        print("Usage: sync_tts.py <translated_srt> <work_dir> <tts_engine> <target_lang> [voice_profile]")
        print("  tts_engine: kokoro, edge-tts, or voicebox")
        print("  voice_profile: (optional) voicebox profile name for voice cloning")
        sys.exit(1)

    srt_file = sys.argv[1]
    work_dir = sys.argv[2]
    tts_engine = sys.argv[3]
    target_lang = sys.argv[4]
    voice_profile = sys.argv[5] if len(sys.argv) > 5 else None

    if tts_engine == 'voicebox' and not voice_profile:
        print("❌ Error: voicebox engine requires voice_profile parameter")
        sys.exit(1)

    print("📝 Parsing subtitles with timing...")
    segments = parse_srt(srt_file)
    print(f"✅ Found {len(segments)} segments\n")

    if tts_engine == 'voicebox':
        print(f"🎙️  Generating TTS segments with voice: {voice_profile}...")
    else:
        print("🎙️  Generating TTS segments...")

    for seg in segments:
        print(f"  Segment {seg['index']+1}/{len(segments)}: {seg['text'][:40]}...")
        seg['raw_file'] = generate_tts(seg, work_dir, tts_engine, target_lang, voice_profile)

    print("\n✅ All TTS generated\n")

    print("⏱️  Syncing audio to subtitle timing...")
    for seg in segments:
        seg['final_file'] = sync_audio(seg['raw_file'], seg['duration'], work_dir, seg['index'])

    print("\n✅ All segments synced\n")

    print("🎼 Building timeline with silence gaps...")
    concat_file = build_timeline(segments, work_dir)

    # Save segments info
    with open(f"{work_dir}/segments.json", 'w') as f:
        json.dump(segments, f, ensure_ascii=False)

    print(f"\n✅ Ready for concatenation")

if __name__ == "__main__":
    main()

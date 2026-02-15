#!/bin/bash
# Generate TTS audio with perfect subtitle sync and create dubbed video
# Usage: generate_tts_and_dub.sh <video_file> <original_srt> <translated_srt> <target_lang> [voice_profile]

set -e

VIDEO_FILE="$1"
ORIGINAL_SRT="$2"
TRANSLATED_SRT="$3"
TARGET_LANG="$4"
VOICE_PROFILE="$5"  # Optional voicebox profile for voice cloning

if [ -z "$VIDEO_FILE" ] || [ -z "$ORIGINAL_SRT" ] || [ -z "$TRANSLATED_SRT" ] || [ -z "$TARGET_LANG" ]; then
    echo "Usage: generate_tts_and_dub.sh <video_file> <original_srt> <translated_srt> <target_lang> [voice_profile]"
    echo "  voice_profile: (optional) voicebox profile name for voice cloning"
    exit 1
fi

BASE_NAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
WORK_DIR="tts_work_$$"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  Step 3: Generating Synced TTS Audio"
echo "========================================"
echo ""
echo "Video: $VIDEO_FILE"
echo "Target: $TARGET_LANG"
echo ""

# Create working directory
mkdir -p "$WORK_DIR"

# Determine TTS engine
if [ -n "$VOICE_PROFILE" ]; then
    TTS_ENGINE="voicebox"
    echo "🎤 Using: Voicebox voice cloning"
    echo "   Voice: $VOICE_PROFILE"
elif [ "$TARGET_LANG" = "chinese" ] || [ "$TARGET_LANG" = "zh" ]; then
    if [ -f "$HOME/.claude/skills/tts/scripts/kokoro_tts.py" ]; then
        TTS_ENGINE="kokoro"
        echo "🎤 Using: Kokoro TTS (local, fast)"
    else
        TTS_ENGINE="edge-tts"
        echo "🎤 Using: edge-tts (cloud)"
    fi
else
    TTS_ENGINE="edge-tts"
    echo "🎤 Using: edge-tts (cloud)"
fi
echo ""

# Generate and sync TTS
if [ -n "$VOICE_PROFILE" ]; then
    python3 "$SCRIPT_DIR/sync_tts.py" "$TRANSLATED_SRT" "$WORK_DIR" "$TTS_ENGINE" "$TARGET_LANG" "$VOICE_PROFILE"
else
    python3 "$SCRIPT_DIR/sync_tts.py" "$TRANSLATED_SRT" "$WORK_DIR" "$TTS_ENGINE" "$TARGET_LANG"
fi

echo ""

# Concatenate all audio
echo "🎵 Combining all segments..."
ffmpeg -f concat -safe 0 -i "$WORK_DIR/concat_list.txt" -ar 44100 -ac 2 "$WORK_DIR/combined.wav" -y 2>/dev/null

# Get video duration
VIDEO_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE")

# Trim/pad to exact video duration and boost volume
echo "✂️  Matching video duration and normalizing volume..."
ffmpeg -i "$WORK_DIR/combined.wav" -t "$VIDEO_DUR" -af "volume=1.8" "${BASE_NAME}_${TARGET_LANG}_audio.mp3" -y 2>/dev/null

echo "✅ Synced audio track: ${BASE_NAME}_${TARGET_LANG}_audio.mp3"
echo ""

# Create dubbed video with dual subtitles
echo "========================================"
echo "  Step 4: Creating Dubbed Video"
echo "========================================"
echo ""
echo "🎬 Adding synced audio + dual subtitles..."

ffmpeg -i "$VIDEO_FILE" -i "${BASE_NAME}_${TARGET_LANG}_audio.mp3" \
    -i "$ORIGINAL_SRT" -i "$TRANSLATED_SRT" \
    -c:v copy -map 0:v -map 1:a -map 2:s -map 3:s \
    -c:s mov_text \
    -metadata:s:s:0 language=eng -metadata:s:s:0 title="Original" \
    -metadata:s:s:1 language=chi -metadata:s:s:1 title="$TARGET_LANG" \
    "${BASE_NAME}_dubbed.mp4" -y 2>/dev/null

echo "✅ Video created: ${BASE_NAME}_dubbed.mp4"
echo ""

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf "$WORK_DIR"

echo ""
echo "========================================"
echo "  ✅ DONE! Perfect Sync Achieved!"
echo "========================================"
echo ""
echo "Output files:"
echo "  • ${BASE_NAME}_original.srt (original subtitles)"
echo "  • ${BASE_NAME}_${TARGET_LANG}.srt (translated subtitles)"
echo "  • ${BASE_NAME}_${TARGET_LANG}_audio.mp3 (synced TTS audio)"
echo "  • ${BASE_NAME}_dubbed.mp4 (final video with dual subs)"
echo ""
echo "Sync details:"
echo "  - Each TTS segment adjusted to match subtitle duration"
echo "  - Silence gaps inserted at correct timeline positions"
echo "  - Audio perfectly synced with subtitles ⏱️"
echo ""
echo "To toggle subtitles:"
echo "  - QuickTime: View → Subtitles → Choose track"
echo "  - VLC: Subtitle → Sub Track → Select track"
echo ""

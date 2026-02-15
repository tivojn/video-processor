# Video/Audio Processor Skill

Comprehensive media processing: transcribe, translate, summarize, and dub videos/audio with professional TTS.

## Features

✅ **Audio + Video support** (MP4, MP3, WAV, M4A, and more)
✅ **URL download** (YouTube, Twitter, TikTok, 1000+ sites via yt-dlp)
✅ Ultra-fast transcription (Groq Whisper Large V3)
✅ Natural translation (context-aware, preserves technical terms)
✅ **Segment-by-segment TTS** (precise timing per subtitle)
✅ **Perfect audio sync** (automatic speed adjustment per segment)
✅ **Voice cloning support** (use any voicebox profile)
✅ Translation review (edit before TTS generation)
✅ **Auto subtitle embedding** (always adds original language subs)
✅ Dual subtitle support (original + translated)
✅ Multi-language TTS (Kokoro + edge-tts + voicebox)
✅ Intelligent summaries (with timestamps and key points)
✅ **Language-aware detection** (auto-detects request language)

## Supported Formats

### Video Files
MP4, MKV, AVI, MOV, WebM, FLV

### Audio Files
MP3, M4A, WAV, FLAC, OGG, AAC

### URLs
YouTube, Twitter/X, TikTok, Instagram, and 1000+ sites via yt-dlp

## Modes

### 1. Transcription Only
Extract transcript with timestamps from video/audio.

**Usage:**
```
/video-transcribe video.mp4
/video-transcribe podcast.mp3
/video-transcribe https://youtube.com/watch?v=xxx
```

**Output:**
- `{name}_transcript.srt` - Transcript with timestamps
- `{name}_transcript.txt` - Plain text transcript

### 2. Translation
Transcribe + translate to target language (subtitles only, no TTS).

**Usage:**
```
/video-translate video.mp4 spanish
/video-translate https://youtube.com/watch?v=xxx chinese
```

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- Side-by-side review before saving

### 3. Dubbing (Full Pipeline)
Transcribe, translate, review, TTS, create dubbed video.

**Usage:**
```
/video-dub video.mp4 chinese
/video-dub podcast.mp3 spanish
/video-dub https://youtube.com/watch?v=xxx french

# With voice cloning
/video-dub video.mp4 chinese --voice "Trump_Voice"
```

**Output:**
- `{name}_original.srt` - Original transcript
- `{name}_{target_lang}.srt` - Translated subtitles
- `{name}_{target_lang}_audio.mp3` - Synced TTS audio
- `{name}_dubbed.mp4` - Final dubbed video with dual subs

### 4. Summary
Transcribe video/audio and generate comprehensive summary.

**Usage:**
```
/video-summary video.mp4
/video-summary podcast.mp3
/video-summary https://youtube.com/watch?v=xxx

# In different languages (auto-detected)
"总结这段视频" video.mp4        # Chinese summary
"résumez cette vidéo" video.mp4  # French summary
"resume este video" video.mp4    # Spanish summary
```

**Output:**
- `{name}_summary.md` - Comprehensive summary:
  - Overview (2-3 sentences)
  - Key points (bullet list)
  - Detailed summary
  - Important timestamps
  - Action items (if applicable)

**Language Detection:**
- Detects request language and generates summary in that language
- "What's this video about?" → English summary
- "总结这段视频" → Chinese summary
- Can override with explicit parameter: `/video-summary video.mp4 spanish`

## Installation

### Dependencies

```bash
# Python packages
pip install groq edge-tts

# System tools (macOS with Homebrew)
brew install ffmpeg yt-dlp

# Optional: Kokoro TTS for Chinese (local, fast)
# Already configured if you have ~/.claude/skills/tts/

# Optional: Voicebox for voice cloning
# Already configured if you have ~/.claude/skills/voicebox/
```

### API Keys

- **Groq API Key** (free): [console.groq.com](https://console.groq.com)
  - Set as environment variable: `export GROQ_API_KEY=gsk_xxx`
  - Or pass as parameter when using skill

## Technical Details

### Segment-by-Segment TTS Processing

The dubbing system uses a sophisticated segment-by-segment approach for perfect timing:

1. **Parse SRT** - Each subtitle entry becomes a separate TTS generation
2. **Generate per segment** - TTS generated for each segment independently
3. **Speed adjustment** - Each segment's speed adjusted to match exact subtitle duration
   - Uses ffmpeg `atempo` filter (supports 0.5x - 2.0x range)
   - Handles >2x speeds with double atempo filters
4. **Add silence gaps** - Inserts precise silence between segments
5. **Combine** - All segments concatenated to match original video duration

**Benefits:**
- Perfect timing sync (no drift over time)
- Maintains original video duration
- Preserves natural speech rhythm
- Works with any TTS engine (Kokoro, edge-tts, voicebox)

### Voice Cloning Support

Use any voicebox profile for dubbing:

```bash
# Dub with cloned voice
video_dubber.py video.mp4 chinese --voice "Trump_Voice"
```

Available when voicebox skill is installed with cloned voice profiles.

## Supported Languages

### TTS Engines

| Language | Engine | Voice | Quality |
|----------|--------|-------|---------|
| Chinese | Kokoro → edge-tts | zf_001, YunxiNeural | Excellent |
| Spanish | edge-tts | AlvaroNeural | Excellent |
| French | edge-tts | HenriNeural | Excellent |
| Japanese | edge-tts | KeitaNeural | Excellent |
| German | edge-tts | ConradNeural | Excellent |
| Italian | edge-tts | DiegoNeural | Excellent |
| Portuguese | edge-tts | AntonioNeural | Excellent |
| Korean | edge-tts | InJoonNeural | Excellent |
| Russian | edge-tts | DmitryNeural | Excellent |

**Translation:** 50+ languages via Groq Llama 3.3 70B

## Example Sessions

### Transcription (Video/Audio/URL)
```
User: "Transcribe this video"
Claude: Extracts transcript → video_transcript.srt + video_transcript.txt

User: "Transcribe podcast.mp3"
Claude: Extracts audio transcript → podcast_transcript.srt + podcast_transcript.txt

User: "Transcribe https://youtube.com/watch?v=xxx"
Claude: Downloads video → Transcribes → transcript files
```

### Summary (Language-Aware)
```
User: "What's this video about?"
Claude: Transcribes → Generates English summary in video_summary.md

User: "总结这段视频" (video.mp4)
Claude: Transcribes → Generates Chinese summary in video_summary.md

User: "Summarize https://twitter.com/user/status/xxx"
Claude: Downloads → Transcribes → Generates English summary

User: "这个YouTube视频讲什么？https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Detects Chinese → Generates Chinese summary
```

### Dubbing (Audio Support)
```
User: "Dub this to Chinese"
Claude: Transcribe → Translate → Review → TTS → Dubbed video

User: "把这个音频配音成中文" (podcast.mp3)
Claude: Transcribe audio → Translate to Chinese → Review → TTS

User: "Dub this YouTube video to Spanish: https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Translates → TTS → Dubbed video
```

## Performance

- **Transcription**: ~3 seconds for 1-minute video (Groq Whisper)
- **Translation**: ~10 seconds for 14 segments (Groq Llama 3.3)
- **TTS Generation**: ~30-60 seconds for 1-minute video (segment-by-segment)
- **Video Export**: ~2 seconds (no re-encoding)

**Total**: ~1-2 minutes for 1-minute video

## Troubleshooting

### Groq API Error
```
❌ Error: GROQ_API_KEY not provided
```
**Fix**: Get free API key from [console.groq.com](https://console.groq.com)

### YouTube Download Error
```
❌ Error downloading video
```
**Fix**: Update yt-dlp: `pip install -U yt-dlp`

### Kokoro Import Error
```
ModuleNotFoundError: No module named 'kokoro'
```
**Fix**: Skill falls back to edge-tts automatically for Chinese

### Subtitle Not Showing in QuickTime
- Use VLC Player instead (better subtitle support)
- Or: View → Subtitles → Choose track in QuickTime

## Notes

- All modes start with transcription
- Translation uses natural phrasing (not machine translation)
- Dubbing includes perfect audio-subtitle sync (segment-by-segment)
- **Always embeds original language subtitles** in output video
- Summaries are comprehensive but concise
- Original video quality is preserved

## License

MIT License - Free to use and modify

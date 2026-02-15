# Video/Audio Processor Skill

Comprehensive media processing: transcribe, translate, summarize, and dub videos/audio with professional TTS.

**Supports:**
- 🎬 **Video files**: MP4, MKV, AVI, MOV, WebM, FLV
- 🎵 **Audio files**: MP3, M4A, WAV, FLAC, OGG, AAC
- 🌐 **URLs**: YouTube, Twitter/X, TikTok, Instagram, and 1000+ sites via yt-dlp

## Activation

Use this skill when the user:
- Says `/video-transcribe`, `/video-translate`, `/video-dub`, or `/video-summary`
- Asks to "transcribe this video"
- Wants to "translate and dub a video"
- Needs "video summary" or "summarize this video"
- Requests "extract transcript from video"
- Asks in ANY language (e.g., "总结这段视频", "résumez cette vidéo", "resume este video")

**Language Detection:**
- Automatically detects the language of the user's request
- Generates output in the same language as the request
- Example: "总结这段视频" → Summary in Chinese
- Example: "summarize this video" → Summary in English
- Can be overridden with explicit language parameter

## Modes

### 1. Transcription Only
Extract transcript with timestamps from video.

**Triggers:** `/video-transcribe`, "transcribe this video"

**Output:**
- `{video_name}_transcript.srt` - Transcript with timestamps
- `{video_name}_transcript.txt` - Plain text transcript

### 2. Translation
Transcribe + translate to target language (no TTS, subtitles only).

**Triggers:** `/video-translate`, "translate this video to {lang}"

**Output:**
- `{video_name}_original.srt` - Original transcript
- `{video_name}_{target_lang}.srt` - Translated subtitles
- Side-by-side review before saving

### 3. Dubbing (Full Pipeline)
Transcribe, translate, review, TTS, create dubbed video.

**Triggers:** `/video-dub`, "dub this video to {lang}"

**Output:**
- `{video_name}_original.srt` - Original transcript
- `{video_name}_{target_lang}.srt` - Translated subtitles
- `{video_name}_{target_lang}_audio.mp3` - Synced TTS audio
- `{video_name}_dubbed.mp4` - Final dubbed video with dual subs

### 4. Summary
Transcribe video and generate comprehensive summary.

**Triggers:**
- `/video-summary`, "summarize this video" (English)
- "总结这段视频" (Chinese)
- "résumez cette vidéo" (French)
- "resume este video" (Spanish)
- Any natural language request

**Output:**
- `{video_name}_summary.md` - Comprehensive summary:
  - Overview (2-3 sentences)
  - Key points (bullet list)
  - Detailed summary
  - Important timestamps
  - Action items (if applicable)

**Language Detection (Automatic):**
- Detects request language and generates summary in that language
- "What's this video about?" → English summary
- "总结这段视频" → Chinese summary
- "这个视频讲什么？" → Chinese summary
- Can override with explicit parameter: `/video-summary video.mp4 spanish`

## Parameters

- `input` (required): Path to video/audio file OR URL
  - Local: `video.mp4`, `audio.mp3`, `podcast.m4a`
  - URL: `https://youtube.com/watch?v=xxx`, `https://twitter.com/user/status/xxx`
- `target_lang` (optional): Target language (chinese, spanish, french, etc.)
- `groq_api_key` (optional): Groq API key (will prompt if not in env)

## Features

- ✅ **Audio + Video support** (MP4, MP3, WAV, M4A, and more)
- ✅ **URL download** (YouTube, Twitter, TikTok, 1000+ sites)
- ✅ Ultra-fast transcription (Groq Whisper Large V3)
- ✅ Natural translation (context-aware, preserves technical terms)
- ✅ **Segment-by-segment TTS** (precise timing per subtitle)
- ✅ **Perfect audio sync** (automatic speed adjustment per segment)
- ✅ **Voice cloning support** (use any voicebox profile)
- ✅ Translation review (edit before TTS generation)
- ✅ **Auto subtitle embedding** (always adds original language subs)
- ✅ Dual subtitle support (original + translated)
- ✅ Multi-language TTS (Kokoro + edge-tts + voicebox)
- ✅ Intelligent summaries (with timestamps and key points)
- ✅ **Language-aware detection** (auto-detects request language)

## Requirements

- ffmpeg (video/audio processing)
- yt-dlp (URL downloads)
- Groq API key (transcription & translation)
- Optional: Kokoro TTS (Chinese, local)
- Optional: edge-tts (50+ languages, cloud)

## Example Sessions

**Transcription (Video/Audio/URL):**
```
User: "Transcribe this video"
Claude: Extracts transcript → video_transcript.srt + video_transcript.txt

User: "Transcribe podcast.mp3"
Claude: Extracts audio transcript → podcast_transcript.srt + podcast_transcript.txt

User: "Transcribe https://youtube.com/watch?v=xxx"
Claude: Downloads video → Transcribes → transcript files
```

**Summary (Language-Aware):**
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

**Dubbing (Audio Support):**
```
User: "Dub this to Chinese"
Claude: Transcribe → Translate → Review → TTS → Dubbed video

User: "把这个音频配音成中文" (podcast.mp3)
Claude: Transcribe audio → Translate to Chinese → Review → TTS

User: "Dub this YouTube video to Spanish: https://youtube.com/watch?v=xxx"
Claude: Downloads → Transcribes → Translates → TTS → Dubbed video
```

## Technical Details

### Segment-by-Segment TTS Processing

The dubbing system uses a sophisticated segment-by-segment approach:

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

## Notes

- All modes start with transcription
- Translation uses natural phrasing (not machine translation)
- Dubbing includes perfect audio-subtitle sync (segment-by-segment)
- **Always embeds original language subtitles** in output video
- Summaries are comprehensive but concise
- Original video quality is preserved

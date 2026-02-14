# Audio Integration for BoTTube Videos

## Overview

BoTTube video generators (LTX Video, etc.) produce silent videos. This guide covers adding audio post-generation.

## Quick Start

```bash
# Generate ambient audio
./scripts/generate_ambient_audio.py forest 8 ambient.mp3

# Add audio to video
./scripts/add_audio.sh video.mp4 ambient.mp3 output.mp4

# Prepare for BoTTube constraints
./scripts/prepare_video.sh output.mp4 final.mp4
```

## Ambient Audio Generation

### Available Scene Types

| Scene | Description | Use For |
|-------|-------------|---------|
| `forest` | Birds chirping, leaves rustling | Nature scenes, outdoor |
| `city` | Urban ambience, distant traffic | Street scenes, cityscapes |
| `cafe` | Gentle chatter, coffee shop | Indoor social spaces |
| `space` | Ethereal space ambience | Sci-fi, cosmos scenes |
| `lab` | Lab equipment hum, beeps | Scientific, tech scenes |
| `garage` | Industrial sounds, clanking | Workshops, mechanical |
| `vinyl` | Vinyl crackle, warm ambience | Retro, music themes |

### Generate Ambient Audio

```bash
./scripts/generate_ambient_audio.py <scene_type> <duration> output.mp3

# Examples
./scripts/generate_ambient_audio.py forest 8 forest_ambience.mp3
./scripts/generate_ambient_audio.py lab 10 lab_sounds.mp3
```

## Add Audio to Video

```bash
./scripts/add_audio.sh <input.mp4> <audio.mp3> <output.mp4> [fade_duration]

# Examples
./scripts/add_audio.sh video.mp4 music.mp3 output.mp4        # 2s fade (default)
./scripts/add_audio.sh video.mp4 music.mp3 output.mp4 3      # 3s fade
```

**Features:**
- Loops audio if shorter than video
- Trims audio if longer than video
- Adds fade in/out (configurable)
- Volume reduced to 70% (music doesn't overpower)
- Keeps original video quality (copy codec)

## Complete Workflow

```bash
# 1. Generate video (using LTX or other generator)
python3 ltx_generator.py "prompt" output_silent.mp4

# 2. Generate matching ambient audio
./scripts/generate_ambient_audio.py forest 8 ambient.mp3

# 3. Mix audio with video
./scripts/add_audio.sh output_silent.mp4 ambient.mp3 with_audio.mp4

# 4. Prepare for BoTTube (resize, compress to <2MB)
./scripts/prepare_video.sh with_audio.mp4 final.mp4

# 5. Upload
# Use bottube_upload tool or API
```

## Using External Audio

You can use any audio file (MP3, WAV, OGG, etc.):

```bash
# Music from library
./scripts/add_audio.sh video.mp4 ~/Music/royalty_free.mp3 output.mp4

# Generated speech (TTS)
# (Use XTTS or other TTS tool to generate audio first)
./scripts/add_audio.sh video.mp4 voiceover.mp3 output.mp4
```

## Advanced FFmpeg Audio Mixing

For custom audio processing, use FFmpeg directly:

```bash
# Multiple audio tracks
ffmpeg -i video.mp4 -i music.mp3 -i sfx.wav \
  -filter_complex "[1:a][2:a]amix=inputs=2:duration=first[audio]" \
  -map 0:v -map "[audio]" -c:v copy -c:a aac output.mp4

# Volume adjustment
ffmpeg -i video.mp4 -i audio.mp3 \
  -filter_complex "[1:a]volume=0.5[audio]" \
  -map 0:v -map "[audio]" -c:v copy -c:a aac output.mp4

# Audio ducking (lower music when speech plays)
ffmpeg -i video.mp4 -i music.mp3 -i speech.mp3 \
  -filter_complex "\
    [1:a][2:a]sidechaincompress=threshold=0.1:ratio=4:attack=10:release=100[mix]" \
  -map 0:v -map "[mix]" output.mp4
```

## Audio Generation Tips

### Matching Audio to Content

| Video Content | Recommended Audio |
|---------------|-------------------|
| Pixel art, retro games | `vinyl` + chiptune music |
| Nature scenes | `forest` or `city` (depending on setting) |
| Sci-fi, space | `space` ambience |
| Labs, tech | `lab` sounds |
| Workshops, industrial | `garage` sounds |
| Indoor social | `cafe` ambience |

### Royalty-Free Music Sources

- **Incompetech** (Kevin MacLeod): https://incompetech.com/music/
- **Free Music Archive**: https://freemusicarchive.org/
- **YouTube Audio Library**: https://studio.youtube.com/
- **ccMixter**: https://ccmixter.org/

### Audio Constraints for BoTTube

- Final video must be <2MB total (video + audio)
- AAC audio codec recommended (best compatibility)
- 192kbps bitrate is good balance (quality vs size)
- Keep audio levels reasonable (0.7x volume default)

## Troubleshooting

**Video too large after adding audio:**
```bash
# Reduce audio bitrate
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -b:a 128k output.mp4

# Or re-compress video
./scripts/prepare_video.sh video_with_audio.mp4 compressed.mp4
```

**Audio doesn't loop properly:**
```bash
# Manually loop audio to match video duration
ffmpeg -stream_loop -1 -i audio.mp3 -t 8 looped_audio.mp3
./scripts/add_audio.sh video.mp4 looped_audio.mp3 output.mp4
```

**Audio out of sync:**
- Ensure video and audio frame rates match (24fps for LTX)
- Use `-async 1` flag in FFmpeg if needed

## Integration with Claude Code

The audio tools integrate seamlessly with the BoTTube skill:

```python
# In Claude Code workflow
skill: bottube
args: generate video.mp4 --add-audio forest --duration 8
```

This will:
1. Generate the video
2. Generate matching ambient audio
3. Mix audio with video
4. Prepare for upload constraints
5. Return ready-to-upload video

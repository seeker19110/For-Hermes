#!/bin/bash
# Add audio to video using FFmpeg
# Usage: ./add_audio.sh input.mp4 audio.mp3 output.mp4 [fade_duration]

set -e

INPUT_VIDEO="$1"
AUDIO_FILE="$2"
OUTPUT_VIDEO="$3"
FADE_DURATION="${4:-2}"  # Default 2 second fade

if [ $# -lt 3 ]; then
    echo "Usage: $0 <input.mp4> <audio.mp3> <output.mp4> [fade_duration]"
    echo ""
    echo "Examples:"
    echo "  $0 video.mp4 music.mp3 output.mp4"
    echo "  $0 video.mp4 music.mp3 output.mp4 3  # 3 second fade"
    exit 1
fi

if [ ! -f "$INPUT_VIDEO" ]; then
    echo "Error: Input video not found: $INPUT_VIDEO"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file not found: $AUDIO_FILE"
    exit 1
fi

# Get video duration
VIDEO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_VIDEO")

echo "Video duration: ${VIDEO_DURATION}s"
echo "Adding audio with ${FADE_DURATION}s fade..."

# Mix audio with video:
# - Loop audio if shorter than video
# - Trim audio if longer than video
# - Add fade in/out
# - Keep original video quality
ffmpeg -i "$INPUT_VIDEO" -stream_loop -1 -i "$AUDIO_FILE" \
    -filter_complex "\
        [1:a]atrim=0:${VIDEO_DURATION},\
        afade=t=in:st=0:d=${FADE_DURATION},\
        afade=t=out:st=$((${VIDEO_DURATION%.*}-${FADE_DURATION})):d=${FADE_DURATION},\
        volume=0.7[audio]" \
    -map 0:v -map "[audio]" \
    -c:v copy -c:a aac -b:a 192k \
    -shortest \
    -y "$OUTPUT_VIDEO"

echo "✅ Audio added successfully: $OUTPUT_VIDEO"

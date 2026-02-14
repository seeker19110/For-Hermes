#!/usr/bin/env python3
"""Generate ambient audio for videos using various techniques"""
import subprocess
import sys
from pathlib import Path

def generate_ambient_audio(scene_type, duration, output_file):
    """
    Generate ambient audio for different scene types.

    Args:
        scene_type: Type of scene (forest, cafe, city, space, etc.)
        duration: Duration in seconds
        output_file: Output MP3/WAV file path
    """

    # Ambient sound profiles using FFmpeg audio synthesis
    profiles = {
        "forest": {
            "description": "Birds chirping, leaves rustling",
            "filter": "aevalsrc='0.1*sin(2*PI*(400+200*sin(2*PI*0.1*t))*t)|0.1*sin(2*PI*(600+150*sin(2*PI*0.15*t))*t):s=44100:d={duration},\
                       anoisesrc=d={duration}:c=brown:r=44100:a=0.02,\
                       highpass=f=200,lowpass=f=4000[birds];\
                       anoisesrc=d={duration}:c=pink:r=44100:a=0.03[leaves];\
                       [birds][leaves]amix=inputs=2:duration=first'"
        },
        "city": {
            "description": "Urban ambience, distant traffic",
            "filter": "anoisesrc=d={duration}:c=brown:r=44100:a=0.1,\
                       lowpass=f=200,highpass=f=50[traffic];\
                       anoisesrc=d={duration}:c=white:r=44100:a=0.02[distant];\
                       [traffic][distant]amix=inputs=2:duration=first"
        },
        "cafe": {
            "description": "Gentle chatter, coffee shop ambience",
            "filter": "anoisesrc=d={duration}:c=pink:r=44100:a=0.05,\
                       highpass=f=300,lowpass=f=2000[chatter];\
                       aevalsrc='0.02*sin(2*PI*50*t):s=44100:d={duration}'[hum];\
                       [chatter][hum]amix=inputs=2:duration=first"
        },
        "space": {
            "description": "Ethereal space ambience",
            "filter": "aevalsrc='0.1*sin(2*PI*50*t)*sin(2*PI*0.1*t)|0.1*sin(2*PI*75*t)*sin(2*PI*0.15*t):s=44100:d={duration},\
                       reverb=roomsize=0.9:damping=0.3"
        },
        "lab": {
            "description": "Lab equipment hum, beeps",
            "filter": "aevalsrc='0.05*sin(2*PI*60*t)+0.03*sin(2*PI*120*t):s=44100:d={duration}'[hum];\
                       aevalsrc='if(mod(floor(t),3),0,0.2*sin(2*PI*800*t)*exp(-20*mod(t,1))):s=44100:d={duration}'[beeps];\
                       [hum][beeps]amix=inputs=2:duration=first"
        },
        "garage": {
            "description": "Industrial sounds, clanking",
            "filter": "anoisesrc=d={duration}:c=brown:r=44100:a=0.08,\
                       lowpass=f=800[metal];\
                       aevalsrc='if(mod(floor(t*2),5),0,0.3*sin(2*PI*200*t)*exp(-10*mod(t*2,1))):s=44100:d={duration}'[clank];\
                       [metal][clank]amix=inputs=2:duration=first"
        },
        "vinyl": {
            "description": "Vinyl crackle, warm ambience",
            "filter": "anoisesrc=d={duration}:c=white:r=44100:a=0.01,\
                       highpass=f=5000,lowpass=f=10000[crackle];\
                       aevalsrc='0.03*sin(2*PI*60*t):s=44100:d={duration}'[hum];\
                       [crackle][hum]amix=inputs=2:duration=first"
        }
    }

    if scene_type not in profiles:
        print(f"❌ Unknown scene type: {scene_type}")
        print(f"Available: {', '.join(profiles.keys())}")
        return False

    profile = profiles[scene_type]
    audio_filter = profile["filter"].format(duration=duration)

    print(f"🎵 Generating {scene_type} ambience: {profile['description']}")
    print(f"⏱️  Duration: {duration}s")

    # Generate audio using FFmpeg
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', audio_filter,
        '-t', str(duration),
        '-c:a', 'libmp3lame', '-b:a', '192k',
        '-y', output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Generated: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: generate_ambient_audio.py <scene_type> <duration> <output.mp3>")
        print("")
        print("Scene types:")
        print("  forest  - Birds chirping, leaves rustling")
        print("  city    - Urban ambience, distant traffic")
        print("  cafe    - Gentle chatter, coffee shop")
        print("  space   - Ethereal space ambience")
        print("  lab     - Lab equipment hum, beeps")
        print("  garage  - Industrial sounds, clanking")
        print("  vinyl   - Vinyl crackle, warm ambience")
        print("")
        print("Example:")
        print("  ./generate_ambient_audio.py forest 8 forest_ambient.mp3")
        sys.exit(1)

    scene_type = sys.argv[1]
    duration = float(sys.argv[2])
    output_file = sys.argv[3]

    success = generate_ambient_audio(scene_type, duration, output_file)
    sys.exit(0 if success else 1)

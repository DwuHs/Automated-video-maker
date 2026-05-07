"""
Step 5 — Video Composition using MoviePy.
Assembles the final vertical video with a three-layer system:
  Layer 1: Background (user-provided gameplay footage, darkened)
  Layer 2: Pexels stock footage PiP overlay (upper portion)
  Layer 3: Captions and UI overlays
"""

import os
import random

# Point MoviePy to the ImageMagick binary on Windows
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    ColorClip,
    CompositeVideoClip,
)
from captions import transcribe_audio, create_caption_clips
from footage import crop_to_vertical


# Output dimensions
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
FPS = 24

# PiP overlay settings
PIP_WIDTH = 1080
PIP_HEIGHT = 800
PIP_Y_OFFSET = 0  # Position at the very top of the frame
PIP_BORDER_RADIUS = 20  # Visual reference (rounded corners via masking not easy in MoviePy)
PIP_SHADOW_SIZE = 4  # Drop shadow width in pixels


def create_dark_overlay(duration: float) -> ColorClip:
    """
    Create a semi-transparent black overlay for darkening the background.
    ~40% opacity black overlay so content above is readable.
    """
    overlay = ColorClip(
        size=(TARGET_WIDTH, TARGET_HEIGHT),
        color=(0, 0, 0),
        duration=duration,
    )
    overlay = overlay.set_opacity(0.40)
    return overlay


def create_pip_border(duration: float) -> CompositeVideoClip:
    """
    Create a subtle border/shadow effect for the PiP window.
    Uses a slightly larger dark rectangle behind the PiP to simulate a drop shadow.
    """
    shadow = ColorClip(
        size=(PIP_WIDTH + PIP_SHADOW_SIZE * 2, PIP_HEIGHT + PIP_SHADOW_SIZE * 2),
        color=(0, 0, 0),
        duration=duration,
    )
    shadow = shadow.set_opacity(0.5)
    # Center the shadow at the PiP location (offset for the shadow border)
    shadow = shadow.set_position((
        -PIP_SHADOW_SIZE,
        PIP_Y_OFFSET - PIP_SHADOW_SIZE,
    ))
    return shadow


def build_video(
    background_path: str,
    audio_path: str,
    output_dir: str,
    topic_slug: str,
    pexels_overlay_path: str | None = None,
    use_split_mode: bool = False,
) -> str:
    """
    Assemble the final video with all layers.

    Args:
        background_path: Path to the background video file.
        audio_path: Path to the voiceover audio file.
        output_dir: Directory to save the final video.
        topic_slug: Slugified topic name for the output filename.
        pexels_overlay_path: Path to the Pexels PiP overlay video (optional).
        use_split_mode: If True, use the 3-layer split mode with darkened background.

    Returns:
        Path to the final output video file.
    """
    print("\n🎬 === BUILDING FINAL VIDEO === 🎬\n")

    if use_split_mode:
        print("🎮 Using SPLIT MODE (background + PiP overlay)")
    else:
        print("📹 Using CLASSIC MODE (Pexels full background)")

    # --- Load background video ---
    print("📼 Loading background footage...")
    bg_clip = VideoFileClip(background_path)

    if use_split_mode:
        bg_clip = crop_to_vertical(bg_clip)
    else:
        bg_clip = bg_clip.resize((TARGET_WIDTH, TARGET_HEIGHT))

    # --- Load audio ---
    print("🔊 Loading voiceover audio...")
    audio_clip = AudioFileClip(audio_path)
    target_duration = audio_clip.duration

    # Fix 2: Random start point for background
    if use_split_mode and bg_clip.duration > (target_duration + 1):
        max_start = bg_clip.duration - target_duration - 1
        start_time = random.uniform(0, max_start)
        print(f"   🎲 Picking random start point: {start_time:.1f}s")
        bg_clip = bg_clip.subclip(start_time, start_time + target_duration)
    else:
        # Ensure background matches audio duration (fallback to loop if shorter)
        if bg_clip.duration < target_duration:
            bg_clip = bg_clip.loop(duration=target_duration)
        else:
            bg_clip = bg_clip.subclip(0, target_duration)

    # Strip audio from background (safety — should already be stripped)
    bg_clip = bg_clip.without_audio()
    # Fix 1: Enforce exact master duration
    bg_clip = bg_clip.set_duration(target_duration)

    # --- Build layer stack ---
    all_clips = [bg_clip]

    # --- Layer 1 addendum: Dark overlay (split mode only) ---
    if use_split_mode:
        print("🌑 Adding dark overlay (40% opacity)...")
        dark_overlay = create_dark_overlay(target_duration).set_duration(target_duration)
        all_clips.append(dark_overlay)

    # --- Layer 2: Pexels PiP overlay (split mode only) ---
    if use_split_mode and pexels_overlay_path and os.path.isfile(pexels_overlay_path):
        print("🖼️  Adding Pexels PiP overlay...")

        pip_clip = VideoFileClip(pexels_overlay_path)

        # Ensure PiP matches audio duration
        if pip_clip.duration < target_duration:
            pip_clip = pip_clip.loop(duration=target_duration)
        else:
            pip_clip = pip_clip.subclip(0, target_duration)

        pip_clip = pip_clip.without_audio()
        # Fix 1: Enforce exact master duration
        pip_clip = pip_clip.set_duration(target_duration)

        # Add drop shadow border behind PiP
        pip_border = create_pip_border(target_duration).set_duration(target_duration)
        all_clips.append(pip_border)

        # Position PiP at the top of the frame
        pip_clip = pip_clip.set_position((0, PIP_Y_OFFSET))
        all_clips.append(pip_clip)

    elif use_split_mode:
        print("ℹ️  No Pexels overlay available — using background only.")

    # --- Generate captions ---
    caption_chunks = transcribe_audio(audio_path)
    caption_clips = create_caption_clips(
        caption_chunks,
        video_width=TARGET_WIDTH,
        video_height=TARGET_HEIGHT,
    )

    # --- Layer 3: Character name overlay (top-left corner) ---
    print("🏷️  Adding character name overlay...")
    name_clip = TextClip(
        "Old Man Gerald",
        fontsize=42,
        color="white",
        stroke_color="black",
        stroke_width=2,
        font="Arial-Bold",
    )
    name_clip = name_clip.set_position((40, 60))
    name_clip = name_clip.set_duration(target_duration)

    # --- Compose all layers ---
    print("🔧 Compositing all layers...")
    all_clips.extend([name_clip] + caption_clips)

    final = CompositeVideoClip(
        all_clips,
        size=(TARGET_WIDTH, TARGET_HEIGHT),
    )
    final = final.set_audio(audio_clip)
    final = final.set_duration(target_duration)

    # --- Write output ---
    output_filename = f"{topic_slug}_oldmangerald.mp4"
    output_path = os.path.join(output_dir, output_filename)

    print(f"💾 Rendering final video to: {output_path}")
    print("   (This may take a few minutes...)")

    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        preset="medium",
        threads=4,
    )

    # Clean up
    bg_clip.close()
    audio_clip.close()
    name_clip.close()
    for clip in caption_clips:
        clip.close()
    final.close()

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Final video saved: {output_path} ({file_size_mb:.1f} MB)")
    print(f"   Resolution: {TARGET_WIDTH}x{TARGET_HEIGHT} (9:16 vertical)")
    print(f"   Duration: {target_duration:.1f}s")

    return output_path

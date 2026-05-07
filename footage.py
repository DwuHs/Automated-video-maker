"""
Step 3 — Stock Footage Assembly using Pexels API (free).
Downloads relevant stock video clips and assembles them into a
vertical background video matching the voiceover duration.

Also handles background video selection from the user's backgrounds/ folder
for the split background/overlay video system.
"""

import os
import glob
import random
import requests
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    ColorClip,
)


# Target output dimensions (vertical 9:16)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

# PiP overlay dimensions
PIP_WIDTH = 1080
PIP_HEIGHT = 800

# Supported background video extensions
BACKGROUND_EXTENSIONS = (".mp4", ".mov", ".avi")


def select_background_video(backgrounds_dir: str = "backgrounds") -> str | None:
    """
    Randomly select a background video from the backgrounds/ folder.

    Args:
        backgrounds_dir: Path to the backgrounds folder.

    Returns:
        Path to the selected background video, or None if no videos found.
    """
    if not os.path.isdir(backgrounds_dir):
        print(f"⚠️  WARNING: '{backgrounds_dir}/' folder not found.")
        print("   Create a 'backgrounds/' folder and add gameplay footage (.mp4, .mov, .avi)")
        print("   to use the split background/overlay mode.")
        return None

    # Find all supported video files
    video_files = []
    for ext in BACKGROUND_EXTENSIONS:
        video_files.extend(glob.glob(os.path.join(backgrounds_dir, f"*{ext}")))
        # Also check uppercase extensions
        video_files.extend(glob.glob(os.path.join(backgrounds_dir, f"*{ext.upper()}")))

    # Remove duplicates (case-insensitive filesystems)
    seen = set()
    unique_files = []
    for f in video_files:
        normalized = os.path.normpath(f).lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_files.append(f)
    video_files = unique_files

    if not video_files:
        print(f"⚠️  WARNING: No video files found in '{backgrounds_dir}/'.")
        print(f"   Supported formats: {', '.join(BACKGROUND_EXTENSIONS)}")
        print("   Add gameplay footage (Minecraft parkour, Subway Surfers, etc.) to this folder.")
        return None

    selected = random.choice(video_files)
    print(f"🎮 Selected background video: {os.path.basename(selected)}")
    print(f"   (from {len(video_files)} available background{'s' if len(video_files) != 1 else ''})")
    return selected





def search_pexels_videos(topic: str, api_key: str, per_page: int = 6) -> list:
    """
    Search Pexels for stock videos related to the topic.

    Args:
        topic: The search query topic.
        api_key: Pexels API key.
        per_page: Number of results to fetch.

    Returns:
        List of dicts with 'url' (download link) and 'id' for each video.
    """
    # Build a broader search query for better results
    search_query = f"{topic} money finance"

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": search_query,
        "per_page": per_page,
        "orientation": "portrait",  # Prefer vertical clips
    }

    print(f"🔍 Searching Pexels for: \"{search_query}\"")
    response = requests.get(url, headers=headers, params=params, timeout=30)

    if response.status_code != 200:
        print(f"⚠️  Pexels API error ({response.status_code}): {response.text}")
        return []

    data = response.json()
    videos = data.get("videos", [])

    if not videos:
        print("⚠️  No videos found on Pexels for this topic.")
        return []

    results = []
    for video in videos:
        # Pick the best quality file that isn't too large
        video_files = video.get("video_files", [])

        # Sort by height (prefer HD but not 4K) and pick a good middle ground
        suitable = [
            vf for vf in video_files
            if vf.get("height", 0) >= 720 and vf.get("height", 0) <= 1920
        ]

        if not suitable:
            suitable = video_files  # Fallback to whatever is available

        if suitable:
            # Sort by height descending, pick the best
            suitable.sort(key=lambda x: x.get("height", 0), reverse=True)
            chosen = suitable[0]
            results.append({
                "url": chosen["link"],
                "id": video["id"],
                "width": chosen.get("width", 0),
                "height": chosen.get("height", 0),
            })

    print(f"📹 Found {len(results)} video clips")
    return results


def download_clip(url: str, output_path: str) -> bool:
    """Download a single video clip from a URL."""
    try:
        response = requests.get(url, stream=True, timeout=120)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        else:
            print(f"⚠️  Failed to download clip: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Download error: {e}")
        return False


def crop_to_vertical(clip: VideoFileClip) -> VideoFileClip:
    """
    Crop/resize a video clip to 1080x1920 vertical format.
    Center-crops landscape footage to fill the vertical frame.
    """
    w, h = clip.size

    # Calculate the target aspect ratio
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT  # 0.5625

    current_ratio = w / h

    if current_ratio > target_ratio:
        # Video is too wide — crop the sides
        new_w = int(h * target_ratio)
        x_offset = (w - new_w) // 2
        clip = clip.crop(x1=x_offset, y1=0, x2=x_offset + new_w, y2=h)
    elif current_ratio < target_ratio:
        # Video is too tall — crop top and bottom
        new_h = int(w / target_ratio)
        y_offset = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y_offset, x2=w, y2=y_offset + new_h)

    # Resize to exact target dimensions
    clip = clip.resize((TARGET_WIDTH, TARGET_HEIGHT))
    return clip


def crop_to_pip(clip: VideoFileClip) -> VideoFileClip:
    """
    Crop/resize a video clip to PiP dimensions (1080x800).
    Center-crops the footage to fill the PiP window.
    """
    w, h = clip.size

    target_ratio = PIP_WIDTH / PIP_HEIGHT  # 1.35

    current_ratio = w / h

    if current_ratio > target_ratio:
        # Video is too wide — crop the sides
        new_w = int(h * target_ratio)
        x_offset = (w - new_w) // 2
        clip = clip.crop(x1=x_offset, y1=0, x2=x_offset + new_w, y2=h)
    elif current_ratio < target_ratio:
        # Video is too tall — crop top and bottom
        new_h = int(w / target_ratio)
        y_offset = (h - new_h) // 2
        clip = clip.crop(x1=0, y1=y_offset, x2=w, y2=y_offset + new_h)

    # Resize to exact PiP dimensions
    clip = clip.resize((PIP_WIDTH, PIP_HEIGHT))
    return clip


def create_fallback_background(duration: float, output_dir: str) -> str:
    """
    Create a solid dark gradient background as fallback when stock footage fails.

    Args:
        duration: Duration in seconds.
        output_dir: Directory to save the background video.

    Returns:
        Path to the fallback background video.
    """
    print("🎨 Creating fallback dark background...")

    # Create a dark gradient-ish background (dark navy/charcoal)
    bg_clip = ColorClip(
        size=(TARGET_WIDTH, TARGET_HEIGHT),
        color=(18, 18, 32),  # Dark navy
        duration=duration,
    )
    bg_clip = bg_clip.set_fps(24)

    fallback_path = os.path.join(output_dir, "background.mp4")
    bg_clip.write_videofile(
        fallback_path,
        codec="libx264",
        audio=False,
        logger=None,
    )
    bg_clip.close()

    print(f"✅ Fallback background created: {fallback_path}")
    return fallback_path


def assemble_pexels_overlay(topic: str, audio_duration: float, output_dir: str) -> str | None:
    """
    Search, download, and assemble Pexels stock footage into a PiP overlay clip
    (1080x800). Returns the path to the overlay video, or None if no footage available.

    Args:
        topic: The video topic for searching relevant footage.
        audio_duration: Duration of the voiceover audio in seconds.
        output_dir: Directory to save downloaded clips and output.

    Returns:
        Path to the assembled overlay video file, or None if unavailable.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("⚠️  PEXELS_API_KEY not set — skipping Pexels overlay.")
        return None

    # Create a temp directory for raw clips
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    # Search for videos
    video_results = search_pexels_videos(topic, api_key)

    if not video_results:
        print("⚠️  No clips found on Pexels — skipping overlay.")
        return None

    # Download clips
    downloaded_paths = []
    for i, video in enumerate(video_results):
        clip_path = os.path.join(clips_dir, f"clip_{i}.mp4")
        print(f"⬇️  Downloading clip {i + 1}/{len(video_results)}...")

        if download_clip(video["url"], clip_path):
            downloaded_paths.append(clip_path)

    if not downloaded_paths:
        print("⚠️  All downloads failed — skipping overlay.")
        return None

    # Load and process clips to PiP dimensions
    print("🎬 Processing Pexels clips for PiP overlay...")
    processed_clips = []

    for path in downloaded_paths:
        try:
            clip = VideoFileClip(path)
            clip = crop_to_pip(clip)
            # Remove audio from stock clips (we use our own voiceover)
            clip = clip.without_audio()
            processed_clips.append(clip)
        except Exception as e:
            print(f"⚠️  Error processing {path}: {e}")
            continue

    if not processed_clips:
        print("⚠️  No clips could be processed — skipping overlay.")
        return None

    # Concatenate all clips
    combined = concatenate_videoclips(processed_clips, method="compose")

    # Loop or trim to match audio duration
    if combined.duration < audio_duration:
        # Loop the footage to fill the duration
        loops_needed = int(audio_duration / combined.duration) + 1
        looped_clips = [combined] * loops_needed
        combined = concatenate_videoclips(looped_clips, method="compose")

    # Trim to exact audio duration
    combined = combined.subclip(0, audio_duration)

    # Write the assembled overlay
    overlay_path = os.path.join(output_dir, "pexels_overlay.mp4")
    combined.write_videofile(
        overlay_path,
        codec="libx264",
        audio=False,
        fps=24,
        logger=None,
    )

    # Clean up clips
    for clip in processed_clips:
        clip.close()
    combined.close()

    print(f"✅ Pexels overlay assembled: {overlay_path} ({audio_duration:.1f}s)")
    return overlay_path


def assemble_footage(topic: str, audio_duration: float, output_dir: str) -> str:
    """
    Search, download, and assemble stock footage into a vertical background video.
    This is the FALLBACK path used when no background videos are available.

    Args:
        topic: The video topic for searching relevant footage.
        audio_duration: Duration of the voiceover audio in seconds.
        output_dir: Directory to save downloaded clips and output.

    Returns:
        Path to the assembled background video file.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("⚠️  PEXELS_API_KEY not set — using fallback background.")
        return create_fallback_background(audio_duration, output_dir)

    # Create a temp directory for raw clips
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    # Search for videos
    video_results = search_pexels_videos(topic, api_key)

    if not video_results:
        print("⚠️  No clips found — using fallback background.")
        return create_fallback_background(audio_duration, output_dir)

    # Download clips
    downloaded_paths = []
    for i, video in enumerate(video_results):
        clip_path = os.path.join(clips_dir, f"clip_{i}.mp4")
        print(f"⬇️  Downloading clip {i + 1}/{len(video_results)}...")

        if download_clip(video["url"], clip_path):
            downloaded_paths.append(clip_path)

    if not downloaded_paths:
        print("⚠️  All downloads failed — using fallback background.")
        return create_fallback_background(audio_duration, output_dir)

    # Load and process clips
    print("🎬 Processing and assembling clips...")
    processed_clips = []

    for path in downloaded_paths:
        try:
            clip = VideoFileClip(path)
            clip = crop_to_vertical(clip)
            # Remove audio from stock clips (we use our own voiceover)
            clip = clip.without_audio()
            processed_clips.append(clip)
        except Exception as e:
            print(f"⚠️  Error processing {path}: {e}")
            continue

    if not processed_clips:
        print("⚠️  No clips could be processed — using fallback background.")
        return create_fallback_background(audio_duration, output_dir)

    # Concatenate all clips
    combined = concatenate_videoclips(processed_clips, method="compose")

    # Loop or trim to match audio duration
    if combined.duration < audio_duration:
        # Loop the footage to fill the duration
        loops_needed = int(audio_duration / combined.duration) + 1
        looped_clips = [combined] * loops_needed
        combined = concatenate_videoclips(looped_clips, method="compose")

    # Trim to exact audio duration
    combined = combined.subclip(0, audio_duration)

    # Write the assembled background
    background_path = os.path.join(output_dir, "background.mp4")
    combined.write_videofile(
        background_path,
        codec="libx264",
        audio=False,
        fps=24,
        logger=None,
    )

    # Clean up clips
    for clip in processed_clips:
        clip.close()
    combined.close()

    print(f"✅ Background video assembled: {background_path} ({audio_duration:.1f}s)")
    return background_path

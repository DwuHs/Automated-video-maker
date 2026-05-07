"""
Step 4 — Captions using OpenAI Whisper (local, free).
Transcribes the voiceover audio with word-level timestamps
and generates TikTok-style caption overlays for MoviePy.
"""

import os
import whisper

# Point MoviePy to the ImageMagick binary on Windows
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy.editor import TextClip, CompositeVideoClip


# Caption styling constants
FONT_SIZE = 70
FONT_COLOR = "white"
STROKE_COLOR = "black"
STROKE_WIDTH = 3
WORDS_PER_CHUNK = 3  # TikTok-style: 3-4 words at a time
CAPTION_Y_POSITION = 0.70  # 70% from top = bottom third


def transcribe_audio(audio_path: str, model_name: str = "base") -> list:
    """
    Transcribe audio using Whisper and extract word-level timestamps.

    Args:
        audio_path: Path to the .mp3 audio file.
        model_name: Whisper model size ('tiny', 'base', 'small', 'medium', 'large').

    Returns:
        List of dicts with keys: 'text', 'start', 'end' for each word chunk.
    """
    print(f"🎤 Transcribing audio with Whisper ({model_name} model)...")

    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, word_timestamps=True)

    # Extract word-level timestamps from segments
    words = []
    for segment in result.get("segments", []):
        for word_info in segment.get("words", []):
            words.append({
                "text": word_info["word"].strip(),
                "start": word_info["start"],
                "end": word_info["end"],
            })

    if not words:
        print("⚠️  No words detected — falling back to segment-level timestamps.")
        for segment in result.get("segments", []):
            words.append({
                "text": segment["text"].strip(),
                "start": segment["start"],
                "end": segment["end"],
            })

    # Group words into chunks of WORDS_PER_CHUNK
    chunks = group_words_into_chunks(words, WORDS_PER_CHUNK)

    print(f"✅ Transcription complete: {len(words)} words → {len(chunks)} caption chunks")
    return chunks


def group_words_into_chunks(words: list, chunk_size: int) -> list:
    """
    Group individual words into display chunks for TikTok-style captions.

    Args:
        words: List of word dicts with 'text', 'start', 'end'.
        chunk_size: Number of words per caption chunk.

    Returns:
        List of chunk dicts with 'text', 'start', 'end'.
    """
    chunks = []
    for i in range(0, len(words), chunk_size):
        group = words[i : i + chunk_size]
        chunk_text = " ".join(w["text"] for w in group)
        chunk_start = group[0]["start"]
        chunk_end = group[-1]["end"]
        chunks.append({
            "text": chunk_text,
            "start": chunk_start,
            "end": chunk_end,
        })
    return chunks


def create_caption_clips(
    chunks: list,
    video_width: int = 1080,
    video_height: int = 1920,
) -> list:
    """
    Create MoviePy TextClip overlays for each caption chunk.

    Args:
        chunks: List of caption chunks from transcribe_audio().
        video_width: Width of the output video.
        video_height: Height of the output video.

    Returns:
        List of MoviePy TextClip objects positioned and timed.
    """
    print("📝 Creating caption overlays...")

    caption_clips = []

    for chunk in chunks:
        try:
            txt_clip = TextClip(
                chunk["text"],
                fontsize=FONT_SIZE,
                color=FONT_COLOR,
                stroke_color=STROKE_COLOR,
                stroke_width=STROKE_WIDTH,
                font="Arial-Bold",
                method="caption",
                size=(video_width - 100, None),  # Padding on sides
                align="center",
            )

            # Set timing
            txt_clip = txt_clip.set_start(chunk["start"])
            txt_clip = txt_clip.set_duration(chunk["end"] - chunk["start"])

            # Position in the bottom third of the frame
            y_pos = int(video_height * CAPTION_Y_POSITION)
            txt_clip = txt_clip.set_position(("center", y_pos))

            caption_clips.append(txt_clip)
        except Exception as e:
            print(f"⚠️  Error creating caption for '{chunk['text']}': {e}")
            continue

    print(f"✅ Created {len(caption_clips)} caption overlays")
    return caption_clips

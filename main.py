"""
Old Man Gerald — Automated Short-Form Finance Video Generator

CLI entry point. Orchestrates the full pipeline:
Topic → Script → Voiceover → Footage → Captions → Video → Upload

Usage:
    python main.py --topic "credit cards"
"""

import os
import re
import sys
import shutil
import argparse
from dotenv import load_dotenv

# Ensure stdout and stderr handle utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# Monkey-patch PIL.Image.ANTIALIAS for compatibility with older moviepy
try:
    import PIL.Image
    if not hasattr(PIL.Image, 'ANTIALIAS'):
        PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
except ImportError:
    pass

def slugify(text: str) -> str:
    """Convert a topic string into a URL/filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _force_remove_readonly(func, path, exc_info):
    """Error handler for shutil.rmtree — clears read-only flag and retries."""
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


def clean_output():
    """Delete everything inside the output/ folder."""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if not os.path.exists(output_dir):
        print("📂 Output folder does not exist — nothing to clean.")
        return

    items = os.listdir(output_dir)
    if not items:
        print("📂 Output folder is already empty.")
        return

    print(f"🗑️  Cleaning output folder: {output_dir}")
    for item in items:
        item_path = os.path.join(output_dir, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, onerror=_force_remove_readonly)
            else:
                try:
                    os.remove(item_path)
                except PermissionError:
                    import stat
                    os.chmod(item_path, stat.S_IWRITE)
                    os.remove(item_path)
            print(f"   Deleted: {item}")
        except Exception as e:
            print(f"   ⚠️  Could not delete {item}: {e}")

    print("✅ Output folder cleaned!")


def print_banner():
    """Print the Old Man Gerald banner."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   👴 OLD MAN GERALD — Finance Video Generator 👴        ║
║                                                          ║
║   "Back in my day, we didn't need an app to save money" ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def print_tiktok_instructions(video_path: str):
    """Print instructions for manually uploading to TikTok."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                  📱 TikTok Upload                        ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  TikTok doesn't support automated API uploads for        ║
║  most accounts. To upload manually:                      ║
║                                                          ║
║  1. Open TikTok on your phone or tiktok.com/upload       ║
║  2. Tap the "+" button to create a new post              ║
║  3. Select "Upload" and choose the video file:           ║
║                                                          ║""")
    print(f"║  📁 {video_path}")
    print("""║                                                          ║
║  4. Add a caption with relevant hashtags like:           ║
║     #finance #money #investing #genz #oldmangerald       ║
║  5. Post it!                                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def main():
    """Main pipeline orchestrator."""
    # Load environment variables
    load_dotenv()

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Old Man Gerald — Automated Finance Video Generator",
        epilog='Example: python main.py --topic "credit cards"',
    )
    parser.add_argument(
        "--topic",
        type=str,
        required=False,
        help="Financial topic for the video (e.g., 'credit cards', '401k', 'budgeting')",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Skip YouTube upload step",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete everything in the output folder and exit",
    )
    args = parser.parse_args()

    if args.clean:
        clean_output()
        return

    if not args.topic:
        parser.error("--topic is required when not using --clean")

    topic = args.topic
    topic_slug = slugify(topic)

    print_banner()
    print(f"🎯 Topic: {topic}")
    print(f"📂 Output folder: output/{topic_slug}/")
    print("=" * 60)

    # Create output directory
    output_dir = os.path.join("output", topic_slug)
    os.makedirs(output_dir, exist_ok=True)

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Script Generation (Gemini Flash)
    # ═══════════════════════════════════════════════════════════
    print("\n📝 STEP 1/6: Generating script with Gemini Flash...\n")
    try:
        from script_writer import generate_script

        script_data = generate_script(topic)
        script_text = script_data["script"]
        video_title = script_data["title"]
        video_description = script_data["description"]

        # Save script to file for reference
        script_path = os.path.join(output_dir, "script.txt")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(f"TITLE: {video_title}\n\n")
            f.write(f"SCRIPT:\n{script_text}\n\n")
            f.write(f"DESCRIPTION:\n{video_description}\n")

        print(f"\n📄 Script saved to: {script_path}")
    except Exception as e:
        print(f"\n❌ Script generation failed: {e}")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Voiceover Generation (ElevenLabs)
    # ═══════════════════════════════════════════════════════════
    print("\n🎙️  STEP 2/6: Generating voiceover with ElevenLabs...\n")
    try:
        from voiceover import generate_voiceover

        audio_path = generate_voiceover(script_text, output_dir)
    except Exception as e:
        print(f"\n❌ Voiceover generation failed: {e}")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Background & Stock Footage Assembly
    # ═══════════════════════════════════════════════════════════
    print("\n📹 STEP 3/6: Preparing background & stock footage...\n")
    try:
        from moviepy.editor import AudioFileClip

        # Get audio duration first
        temp_audio = AudioFileClip(audio_path)
        audio_duration = temp_audio.duration
        temp_audio.close()
        print(f"   Audio duration: {audio_duration:.1f} seconds")

        from footage import (
            select_background_video,
            assemble_pexels_overlay,
            assemble_footage,
            create_fallback_background,
        )

        # Check for user-provided background videos
        user_bg_path = select_background_video()
        use_split_mode = user_bg_path is not None
        pexels_overlay_path = None

        if use_split_mode:
            # --- SPLIT MODE ---
            # We pass the user's raw background video directly to the builder
            # to preserve its full length for random start points.
            background_path = user_bg_path

            # Fetch Pexels footage as a PiP overlay (optional — skipped if nothing found)
            print("\n🖼️  Fetching Pexels footage for PiP overlay...")
            pexels_overlay_path = assemble_pexels_overlay(
                topic, audio_duration, output_dir
            )

        else:
            # --- CLASSIC FALLBACK MODE ---
            print("📹 Falling back to classic mode (Pexels as full background)...")
            background_path = assemble_footage(topic, audio_duration, output_dir)

    except Exception as e:
        print(f"\n⚠️  Footage assembly failed: {e}")
        print("   Attempting fallback dark background...")
        use_split_mode = False
        pexels_overlay_path = None
        try:
            background_path = create_fallback_background(audio_duration, output_dir)
        except Exception as e2:
            print(f"\n❌ Fallback also failed: {e2}")
            sys.exit(1)

    # ═══════════════════════════════════════════════════════════
    # STEP 4 & 5: Captions + Video Composition (Whisper + MoviePy)
    # ═══════════════════════════════════════════════════════════
    print("\n🎬 STEP 4-5/6: Transcribing captions & building video...\n")
    try:
        from video_builder import build_video

        final_video_path = build_video(
            background_path=background_path,
            audio_path=audio_path,
            output_dir=output_dir,
            topic_slug=topic_slug,
            pexels_overlay_path=pexels_overlay_path,
            use_split_mode=use_split_mode,
        )
    except Exception as e:
        print(f"\n❌ Video composition failed: {e}")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════
    # STEP 6: YouTube Upload
    # ═══════════════════════════════════════════════════════════
    youtube_url = ""
    if not args.skip_upload:
        print("\n📤 STEP 6/6: Uploading to YouTube...\n")
        try:
            from uploader import upload_to_youtube

            youtube_url = upload_to_youtube(
                video_path=final_video_path,
                title=video_title,
                description=video_description,
                topic=topic,
            )
        except Exception as e:
            print(f"\n⚠️  YouTube upload failed: {e}")
            print("   You can upload the video manually later.")
    else:
        print("\n⏭️  STEP 6/6: YouTube upload skipped (--skip-upload flag)")

    # ═══════════════════════════════════════════════════════════
    # STEP 7: TikTok Instructions
    # ═══════════════════════════════════════════════════════════
    print_tiktok_instructions(os.path.abspath(final_video_path))

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    print("=" * 60)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"📂 Output folder:  {os.path.abspath(output_dir)}")
    print(f"🎬 Video file:     {os.path.abspath(final_video_path)}")
    print(f"📄 Script file:    {os.path.abspath(os.path.join(output_dir, 'script.txt'))}")
    if youtube_url:
        print(f"🔗 YouTube URL:    {youtube_url}")
    print(f"\n👴 Old Man Gerald says: \"You're welcome, kid.\"\n")


if __name__ == "__main__":
    main()

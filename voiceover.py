"""
Step 2 — Voiceover Generation using ElevenLabs API (free tier).
Sends the generated script to ElevenLabs TTS and saves the audio as .mp3.
"""

import os
import re
import requests


def _clean_script_for_tts(script: str) -> str:
    """
    Clean a script so it reads well through TTS without awkward pauses or
    literal stage directions.
    """
    # Remove stage directions in *asterisks*, (parentheses), or [brackets]
    text = re.sub(r"\*[^*]+\*", "", script)          # *scoffs*, *sighs heavily*
    text = re.sub(r"\([^)]*\)", "", text)             # (laughs), (pauses)
    text = re.sub(r"\[[^\]]*\]", "", text)            # [beat], [pause]

    # Collapse excessive ellipses (more than 3 dots → single ellipsis)
    text = re.sub(r"\.{4,}", "...", text)

    # Collapse runs of multiple ellipses separated by whitespace
    text = re.sub(r"(\.\.\.\s*){2,}", "... ", text)

    # Collapse excessive whitespace / blank lines into a single space
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Remove em-dashes used as dramatic pauses (keep single hyphens for hyphenated words)
    text = re.sub(r"\s*—\s*", ", ", text)
    text = re.sub(r"\s*--\s*", ", ", text)

    return text.strip()


def generate_voiceover(script: str, output_dir: str) -> str:
    """
    Generate a voiceover audio file from the script text using ElevenLabs.

    Args:
        script: The monologue script text to convert to speech.
        output_dir: Directory to save the output audio file.

    Returns:
        Path to the saved .mp3 audio file.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables.")
    if not voice_id:
        raise ValueError(
            "ELEVENLABS_VOICE_ID not found in environment variables. "
            "Set it in your .env file to the desired voice ID."
        )

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }

    # Clean the script to remove stage directions and excessive pauses
    clean_text = _clean_script_for_tts(script)

    payload = {
        "text": clean_text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.55,         # Increased for more consistent and faster delivery
            "similarity_boost": 0.70,   # High similarity but allows for more character variance
            "style": 0.45,             # Reduced to decrease exaggerated pauses and flourishes
            "use_speaker_boost": True,
        },
    }

    print("🎙️  Generating voiceover with ElevenLabs...")
    print(f"   Character count: {len(clean_text)} (free tier limit: 10,000/month)")

    response = requests.post(url, json=payload, headers=headers, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs API error ({response.status_code}): {response.text}"
        )

    # Save the audio file
    audio_path = os.path.join(output_dir, "voiceover.mp3")
    with open(audio_path, "wb") as f:
        f.write(response.content)

    # Show file size for sanity check
    size_kb = os.path.getsize(audio_path) / 1024
    print(f"✅ Voiceover saved: {audio_path} ({size_kb:.0f} KB)")

    return audio_path

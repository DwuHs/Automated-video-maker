"""
Step 6 — YouTube Auto-upload using YouTube Data API v3.
Handles OAuth2 authentication and video upload as a YouTube Short.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# OAuth2 scopes required for uploading and commenting
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def get_authenticated_service():
    """
    Authenticate with YouTube Data API v3 using OAuth2.
    Caches the token after first authentication so subsequent
    runs don't require browser-based auth.

    Returns:
        Authenticated YouTube API service object.
    """
    creds = None

    # Check for cached token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing YouTube authentication token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"'{CREDENTIALS_FILE}' not found. "
                    "Download it from Google Cloud Console. "
                    "See README.md for setup instructions."
                )

            print("🌐 Opening browser for YouTube authentication...")
            print("   (This only needs to happen once)")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the token for future runs
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
        print("✅ YouTube authentication token cached.")

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(
    video_path: str,
    title: str,
    description: str,
    topic: str,
) -> str:
    """
    Upload a video to YouTube as a Short.

    Args:
        video_path: Path to the video file to upload.
        title: Video title (under 60 characters).
        description: Video description with hashtags.
        topic: The original topic for tagging.

    Returns:
        YouTube video URL if successful, empty string if failed.
    """
    print("\n📤 === UPLOADING TO YOUTUBE === 📤\n")

    try:
        youtube = get_authenticated_service()
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
        print("   Skipping YouTube upload. You can upload manually later.")
        return ""
    except Exception as e:
        print(f"⚠️  YouTube authentication failed: {e}")
        print("   Skipping YouTube upload. You can upload manually later.")
        return ""

    # Ensure #Shorts is in both the title and description.
    # YouTube uses the title as the primary signal to classify a video as a Short.
    if "#Shorts" not in title:
        # YouTube titles max out at 100 chars; trim if necessary before appending
        max_base_len = 100 - len(" #Shorts")
        title = title[:max_base_len].rstrip() + " #Shorts"

    if "#Shorts" not in description:
        description += "\n\n#Shorts"

    # Build the request body
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [
                "finance",
                "money",
                "investing",
                topic,
                "Old Man Gerald",
                "Shorts",
                "financial advice",
                "Gen Z finance",
            ],
            "categoryId": "27",  # Education
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Create the media upload object
    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=256 * 1024,  # 256 KB chunks
    )

    print(f"📹 Uploading: {title}")
    print(f"   File: {video_path}")

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   Upload progress: {progress}%")

        video_id = response["id"]
        video_url = f"https://youtube.com/shorts/{video_id}"

        print(f"\n✅ Video uploaded successfully!")
        print(f"   🔗 URL: {video_url}")

        # Post a comment as the creator
        try:
            print(f"💬 Posting comment on video...")
            comment_body = {
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": "Comment what topic you'd like to see next you whipper snappers!"
                        }
                    }
                }
            }
            youtube.commentThreads().insert(
                part="snippet",
                body=comment_body
            ).execute()
            print(f"✅ Comment posted successfully!")
        except Exception as comment_err:
            print(f"⚠️  Could not post comment: {comment_err}")
            print("   (You may need to delete token.json and re-authenticate to grant commenting permissions)")

        return video_url

    except Exception as e:
        print(f"\n❌ YouTube upload failed: {e}")
        print("   You can upload the video manually from the output folder.")
        return ""

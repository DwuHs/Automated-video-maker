# 👴 Old Man Gerald — Automated Finance Video Generator

> *"Back in my day, we didn't need an app to tell us to stop buying avocado toast."*

A fully automated Python pipeline that generates short-form vertical finance videos (YouTube Shorts / TikTok) featuring **Old Man Gerald** — a grumpy, lovable old man who explains financial concepts to Gen Z.

**One command. One topic. One video.**

```bash
python main.py --topic "credit cards"
```

## 🎬 What It Does

| Step | Action | Tool |
|------|--------|------|
| 1 | Generates a script in Gerald's voice | Gemini Flash (free) |
| 2 | Creates voiceover audio | ElevenLabs (free tier) |
| 3 | Finds & assembles stock footage | Pexels API (free) |
| 4 | Transcribes captions with timestamps | Whisper (local, free) |
| 5 | Composes final 1080×1920 video | MoviePy |
| 6 | Uploads to YouTube as a Short | YouTube Data API v3 |
| 7 | Saves file for manual TikTok upload | — |

## 📋 Prerequisites

- **Python 3.9+**
- **FFmpeg** — required by MoviePy and Whisper
- **ImageMagick** — required by MoviePy for text rendering

### Installing FFmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
# Add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

### Installing ImageMagick

**Windows:**
```bash
# Download from: https://imagemagick.org/script/download.php
# During installation, CHECK "Install legacy utilities (e.g., convert)"
# Add to PATH
```

**macOS:**
```bash
brew install imagemagick
```

**Linux:**
```bash
sudo apt install imagemagick
```

## 🚀 Setup

### 1. Clone & Install Dependencies

```bash
cd automated-video-maker
pip install -r requirements.txt
```

### 2. Get Your API Keys (All Free)

#### Gemini API Key
1. Go to [https://aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click "Get API Key" → "Create API key"
4. Copy the key

#### ElevenLabs API Key
1. Go to [https://elevenlabs.io](https://elevenlabs.io)
2. Create a free account
3. Click your profile icon → "Profile + API Key"
4. Copy your API key
5. To find a voice ID: Go to "Voices" in the sidebar, click on a voice, and copy the Voice ID from the URL or voice settings

> **Recommended voices for Old Man Gerald:** Browse the ElevenLabs voice library for an elderly male American voice. Some good options include voices tagged as "old", "deep", or "authoritative".

#### Pexels API Key
1. Go to [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Click "Get Started" and create a free account
3. Your API key will be shown on the API dashboard

### 3. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env
```

Edit `.env` with your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_chosen_voice_id_here
PEXELS_API_KEY=your_pexels_api_key_here
```

### 4. Set Up Background Videos (Gameplay Footage)

To create highly engaging TikTok-style videos, you can provide your own background footage (like Minecraft parkour, Subway Surfers, or mobile game recordings). The bot will use these as the full-screen background layer while playing related stock footage in a small picture-in-picture window at the top.

1. Ensure there is a `backgrounds/` folder in the project root (created automatically or you can create it).
2. Add your own gameplay footage as `.mp4`, `.mov`, or `.avi` files to this folder.
3. The bot will pick one randomly each run, ensuring your content feels varied even with a small pool of videos.
4. **Where to find footage:** Search YouTube for "Minecraft parkour no copyright gameplay" or "Subway Surfers free to use gameplay", and download the clips.
5. **Tip:** Keep your background videos at least 60 seconds long for best results. The bot will automatically loop them if they're shorter than the generated voiceover, and the audio will be stripped completely.

If you don't add any videos to the `backgrounds/` folder, the bot will automatically fall back to the old behavior of using full-screen stock footage from Pexels!

### 5. Set Up YouTube OAuth2 Credentials (Optional — for auto-upload)

YouTube requires OAuth2 for uploading videos. Follow these steps:

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it something like "Old Man Gerald" and click "Create"

#### Step 2: Enable YouTube Data API v3
1. In your project, go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click on it and press **Enable**

#### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** and click "Create"
3. Fill in the required fields:
   - App name: "Old Man Gerald"
   - User support email: your email
   - Developer contact info: your email
4. Click "Save and Continue"
5. On the **Scopes** page, click "Add or Remove Scopes"
6. Search for `youtube.upload` and check it
7. Click "Save and Continue"
8. On the **Test users** page, add your Google/YouTube email
9. Click "Save and Continue"

#### Step 4: Create OAuth2 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Application type: **Desktop app**
4. Name: "Old Man Gerald Desktop"
5. Click "Create"
6. Click **"Download JSON"**
7. Rename the downloaded file to `credentials.json`
8. Place it in the project root directory (`automated-video-maker/credentials.json`)

#### Step 5: First Run Authentication
The first time you run the pipeline without `--skip-upload`, a browser window will open asking you to authorize the app. After authorizing, a `token.json` file will be created locally so you won't need to authenticate again.

> **Note:** While your app is in "Testing" mode in Google Cloud, the token expires every 7 days. To avoid this, you can publish the app (it doesn't need to be verified for personal use).

## 🎮 Usage

### Basic Usage
```bash
python main.py --topic "credit cards"
```

### Skip YouTube Upload
```bash
python main.py --topic "investing for beginners" --skip-upload
```

### More Examples
```bash
python main.py --topic "401k retirement"
python main.py --topic "budgeting"
python main.py --topic "crypto"
python main.py --topic "emergency fund"
python main.py --topic "student loans"
python main.py --topic "compound interest"
```

### Output Structure
```
output/
└── credit-cards/
    ├── script.txt                    # Generated script & metadata
    ├── voiceover.mp3                 # AI-generated voiceover
    ├── background.mp4                # Assembled stock footage
    ├── clips/                        # Raw downloaded clips
    │   ├── clip_0.mp4
    │   ├── clip_1.mp4
    │   └── ...
    └── credit-cards_oldmangerald.mp4 # ✅ Final video (upload this!)
```

## 📱 Uploading to TikTok

TikTok doesn't support automated API uploads for most accounts. To upload manually:

1. Open TikTok on your phone or go to [tiktok.com/upload](https://tiktok.com/upload)
2. Tap the **"+"** button to create a new post
3. Select **"Upload"** and choose the video file from `output/{topic}/`
4. Add a caption with hashtags:
   ```
   Old Man Gerald explains {topic} 👴💰 #finance #money #investing #genz #oldmangerald #financialliteracy
   ```
5. Post it!

## 🔧 Troubleshooting

### "ImageMagick not found" error
MoviePy needs ImageMagick for text rendering. Make sure it's installed and:
- **Windows:** The install directory is in your PATH, and legacy utilities were installed
- **macOS/Linux:** It's available via `convert --version` in terminal

You may also need to edit MoviePy's config. Find `config_defaults.py` in your MoviePy installation and set:
```python
IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.x.x-Q16-HDRI\magick.exe"  # Windows
# or
IMAGEMAGICK_BINARY = "/usr/local/bin/convert"  # macOS/Linux
```

### "FFmpeg not found" error
Ensure FFmpeg is installed and available in your PATH:
```bash
ffmpeg -version
```

### ElevenLabs "quota exceeded" error
The free tier allows 10,000 characters/month. Each script is ~150-200 words (~800-1200 characters), so you can generate roughly 8-12 videos per month on the free tier.

### YouTube upload fails
- Make sure `credentials.json` is in the project root
- Delete `token.json` and re-authenticate if your token expired
- Ensure your Google Cloud project has the YouTube Data API v3 enabled
- Check that your email is listed as a test user in the OAuth consent screen

### Stock footage download fails
The pipeline automatically falls back to a solid dark background if Pexels clips can't be downloaded. The video will still be generated with voiceover and captions.

## 📁 File Structure

```
automated-video-maker/
├── main.py              # CLI entry point: --topic argument
├── script_writer.py     # Gemini Flash script generation
├── voiceover.py         # ElevenLabs API audio generation
├── footage.py           # Pexels API stock footage downloader
├── captions.py          # Whisper transcription + caption timing
├── video_builder.py     # MoviePy video assembly (1080×1920)
├── uploader.py          # YouTube Data API v3 upload
├── backgrounds/         # User-provided gameplay footage (optional)
├── output/              # Generated videos saved here
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .env                 # Your API keys (do NOT commit)
├── credentials.json     # YouTube OAuth2 (you provide this)
├── token.json           # Cached YouTube auth token (auto-generated)
└── README.md            # This file
```

## ⚠️ Important Notes

- **All APIs use free tiers** — no paid subscriptions required
- **Whisper runs locally** — it does NOT call the OpenAI API (no API key needed)
- **Videos are 1080×1920px** (9:16 vertical) — optimized for Shorts/TikTok
- **ElevenLabs free tier** is limited to 10,000 characters/month — scripts are kept efficient
- **YouTube OAuth tokens** expire after 7 days in "Testing" mode — publish your app to avoid this

## 👴 About Old Man Gerald

Old Man Gerald is a fictional character who made his money the old-fashioned way and is constantly baffled by how young people handle their finances. He's grumpy, sarcastic, and uses phrases like "back in my day" — but he's NOT mean-spirited. He always lands on genuinely useful financial advice. Think of him as the financially savvy grandpa everyone wishes they had.

---

*Built with ❤️ and a healthy dose of grumpiness.*

#personalfinance #moneytips #financialliteracy #moneyadvice 
#financetok #moneyhacks #financialfreedom #investing101 #genzfinance #adulting #adulting101 #moneyforbeginners 
#collegestudent #broke #firstjob #twenties #learnontiktok #didyouknow #fyp #foryou #viral
#storytime #explainedbyai #financefacts #emergency #budgetfriendly #budgeting #budget #financetips

Like and follow. Back in my day we called it common sense. Now apparently I have to ask.

topics to use
Beginner basics (biggest Gen Z audience):

Student loans — how they actually work
Your first paycheck — what all the deductions mean
What a credit score is and why it matters at 18
Roth IRA — why you should open one at 20
What taxes actually are and why you owe them
Checking vs savings account — you're using them wrong
What compound interest is and why it's your best friend or worst enemy
How to actually read a pay stub

Spending habits (most relatable/viral potential):

Why subscriptions are draining you dry
The true cost of eating out every day
Why buying a car new is a trap
How much that daily coffee actually costs you over 10 years
Why rent vs buying isn't as simple as everyone says
Lifestyle inflation — why raises don't make you richer

Investing:

What the stock market actually is in simple terms
Index funds — the boring investment that actually works
What a 401k is and why your job match is free money
Crypto — what it is and why Gerald doesn't trust it
What inflation actually does to your money
Why keeping all your money in a savings account is losing money

Debt:

Good debt vs bad debt
How credit card interest actually works
The snowball vs avalanche debt payoff methods
Why minimum payments are a trap
Medical debt — what they don't tell you
What happens if you never pay a debt

Life events nobody prepares you for:

What to do financially when you get your first job
How to negotiate your salary — Gerald reluctantly admits young people should do this
What renters insurance is and why you need it
How to file taxes for the first time
What happens to your finances when you get married
How to split finances with a roommate without ruining the friendship

Slightly controversial / high engagement potential:

Why college might not be worth it financially
Why your parents financial advice might be outdated
Why the housing market is actually broken for young people
Why Gerald thinks nobody under 30 should touch crypto
The real reason you're not saving money — it's not the avocado toast

High search volume on YouTube specifically:

How to build credit from zero
Best credit cards for beginners
How to save your first $1000
How to invest with $100
What to do with your first paycheck
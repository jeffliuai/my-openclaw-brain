import os
import sys
import subprocess
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Optional packages for parsing subtitles nicely
try:
    import pysrt
    import webvtt
    HAS_SUB_PARSERS = True
except ImportError:
    HAS_SUB_PARSERS = False

try:
    import yt_dlp
    HAS_YTDLP = True
except ImportError:
    HAS_YTDLP = False

# We will load openai only if needed for transcription
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def setup_env():
    """Load environment variables."""
    # Try loading from a .env file if it exists
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

def clean_srt(filepath):
    """Read an SRT file and return plain text."""
    if not HAS_SUB_PARSERS:
        return "[Error] pysrt is not installed. Unable to parse SRT cleanly."
    try:
        subs = pysrt.open(filepath)
        text = "\n".join([sub.text for sub in subs])
        return text
    except Exception as e:
        return f"[Error] Failed to parse SRT {filepath}: {e}"

def clean_vtt(filepath):
    """Read a VTT file and return plain text."""
    if not HAS_SUB_PARSERS:
        return "[Error] webvtt-py is not installed. Unable to parse VTT cleanly."
    try:
        text = ""
        for caption in webvtt.read(filepath):
            text += caption.text + "\n"
        return text
    except Exception as e:
        return f"[Error] Failed to parse VTT {filepath}: {e}"

def extract_embedded_subs(video_path, output_dir):
    """
    Use ffprobe to check if there are subtitle streams.
    Extract the first subtitle stream using ffmpeg to a temporary .srt file if found.
    Returns path to the extracted subtitle file or None.
    """
    try:
        # Check for subtitle streams
        ffprobe_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 's',
            '-show_entries', 'stream=index:stream_tags=language',
            '-of', 'csv=p=0', str(video_path)
        ]
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
        streams = result.stdout.strip().split('\n')
        
        if not streams or streams[0] == '':
            print(f"No embedded subtitle streams found in {video_path.name}")
            return None

        # Extract the first subtitle stream (index 0)
        print(f"Found subtitle streams. Extracting the first one...")
        out_sub_path = output_dir / f"{video_path.stem}_extracted.srt"
        
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', str(video_path), 
            '-map', '0:s:0', str(out_sub_path)
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"Successfully extracted embedded subtitles to {out_sub_path}")
        return out_sub_path
        
    except subprocess.CalledProcessError as e:
        print(f"Error checking/extracting embedded subtitles: {e.stderr.decode() if e.stderr else e}")
        return None
    except FileNotFoundError:
        print("[Error] ffmpeg/ffprobe not found. Please ensure they are installed and in PATH.")
        return None


def extract_audio(video_path, output_dir):
    """Extract audio from video file to a temporary MP3 file."""
    try:
        out_audio_path = output_dir / f"{video_path.stem}_audio.mp3"
        print(f"Extracting audio from {video_path.name}...")
        
        # Extract to mp3, keeping bitrate reasonable for whisper (128k is plenty)
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', str(video_path), 
            '-vn', '-acodec', 'libmp3lame', '-ab', '128k', 
            str(out_audio_path)
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)
        print(f"Audio extracted successfully to {out_audio_path}")
        return out_audio_path
        
    except subprocess.CalledProcessError as e:
        print(f"[Error] Failed to extract audio: {e.stderr.decode() if e.stderr else e}")
        return None
    except FileNotFoundError:
        print("[Error] ffmpeg not found. Please ensure it is installed and in PATH.")
        return None


def transcribe_audio_openai(audio_path):
    """Use OpenAI API to transcribe the audio file."""
    if not HAS_OPENAI:
        return "[Error] openai python package not installed. Cannot transcribe."
        
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "[Error] OPENAI_API_KEY environment variable not set. Cannot use OpenAI Transcription."

    print(f"Sending {audio_path.name} to OpenAI Whisper API for transcription...")
    try:
        client = OpenAI(api_key=api_key)
        
        # Warn if file is over 25MB (OpenAI limit)
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > 25:
            print(f"[Warning] Audio file is {file_size_mb:.2f}MB, which exceeds OpenAI's 25MB limit. API call will likely fail. You may need to split the file.")
            
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text" # Returns raw text instead of JSON
            )
        return transcript
        
    except Exception as e:
        return f"[Error] OpenAI API Transcription failed: {e}"


def download_video_or_audio(url, output_dir):
    """
    Use yt-dlp to download the video. 
    To save time/space, we prefer downloading just the audio if we only need transcription,
    but we also want to try and grab subtitles if available.
    Returns the path to the downloaded file.
    """
    if not HAS_YTDLP:
        print("[Error] yt-dlp package is not installed. Cannot process URLs.")
        sys.exit(1)
        
    print(f"Detected URL. Using yt-dlp to download from {url}...")
    
    # We download to a temporary directory
    # We ask yt-dlp to grab subtitles if possible, and prefer mp4/m4a/webm formats
    ydl_opts = {
        'format': 'best',
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'zh-Hant', 'zh-Hans', 'zh'], # Try to get English or Chinese
        'quiet': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # The filename might have changed due to sanitization, so we use prepare_filename
            downloaded_file = ydl.prepare_filename(info)
            print(f"Successfully downloaded to: {downloaded_file}")
            return Path(downloaded_file)
    except Exception as e:
        print(f"[Error] yt-dlp failed to download URL: {e}")
        sys.exit(1)


def process_video(video_filepath_or_url):
    """
    Main logic:
    0. Check if input is a URL and download it first.
    1. Check for external subtitles (.srt, .vtt)
    2. Try to extract embedded subtitles
    3. Fallback: extract audio and send to transcription API
    """
    
    output_dir = Path("/tmp/video_transcriber")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    is_url = video_filepath_or_url.startswith("http://") or video_filepath_or_url.startswith("https://")
    
    if is_url:
        video_path = download_video_or_audio(video_filepath_or_url, output_dir)
    else:
        video_path = Path(video_filepath_or_url).resolve()
    
    if not video_path.exists():
        print(f"[Error] File not found: {video_path}")
        sys.exit(1)
        
    directory = video_path.parent
    stem = video_path.stem
    
    # 1. Check for external subtitles
    srt_path = directory / f"{stem}.srt"
    vtt_path = directory / f"{stem}.vtt"
    
    if srt_path.exists():
        print(f"Found external SRT file: {srt_path.name}")
        return clean_srt(srt_path)
    
    if vtt_path.exists():
        print(f"Found external VTT file: {vtt_path.name}")
        return clean_vtt(vtt_path)
        
    # 2. Check for embedded subtitles
    print("No external subtitle files found.")
    output_dir = Path("/tmp/video_transcriber")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extracted_sub = extract_embedded_subs(video_path, output_dir)
    if extracted_sub and extracted_sub.exists():
        text = clean_srt(extracted_sub)
        # Cleanup
        try:
            extracted_sub.unlink()
        except:
            pass
        return text
        
    # 3. Fallback to API Transcription
    print("No embedded subtitles found. Falling back to audio transcription API...")
    audio_path = extract_audio(video_path, output_dir)
    
    if not audio_path or not audio_path.exists():
        return "[Error] Could not extract audio for transcription."
        
    transcription = transcribe_audio_openai(audio_path)
    
    # Cleanup audio temp file and downloaded video if it was a URL
    try:
        audio_path.unlink()
        if is_url:
            video_path.unlink()
    except:
        pass
        
    return transcription

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Video/URL to Text (Extract Subs or Transcribe)")
    parser.add_argument("source", help="Path to the input video file or URL (YouTube, Bilibili, etc.)")
    parser.add_argument("-o", "--output", help="Path to save the output text file. If not provided, prints to stdout.")
    
    args = parser.parse_args()
    
    setup_env()
    
    text_result = process_video(args.source)
    
    if text_result.startswith("[Error]"):
        print(text_result, file=sys.stderr)
        sys.exit(1)
        
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text_result)
            print(f"Successfully saved transcript to {args.output}")
        except Exception as e:
            print(f"[Error] Failed to write to {args.output}: {e}", file=sys.stderr)
    else:
        print("\n--- TRANSCRIPT ---\n")
        print(text_result)
        print("\n------------------\n")

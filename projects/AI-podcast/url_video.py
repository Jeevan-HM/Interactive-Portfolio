# import openai
# import requests
# from pydub import AudioSegment
import glob
import os
import time

from moviepy.editor import AudioFileClip
from pytubefix import YouTube

# import requests
# from api_key import os.getenv("api_openai_key"), os.getenv("eleven_labs_api")
# import generate_audio


# eleven_labs_api_key = os.getenv("eleven_labs_api")
# openai.api_key = os.getenv("api_openai_key")


def download_and_trim_audio(clip_url, filename, max_size):
    yt = YouTube(clip_url)
    stream = yt.streams.filter(only_audio=True).first()

    # Split filename into directory and base name
    output_dir = os.path.dirname(filename) or "."
    base_name = os.path.basename(filename)

    # pytubefix saves with the stream's default title unless we specify output_path + filename
    downloaded_path = stream.download(
        output_path=output_dir, filename=base_name + ".webm"
    )

    # Fallback: if pytubefix saved under a different name, find it
    if not os.path.exists(downloaded_path):
        matches = glob.glob(os.path.join(output_dir, "*.webm")) + glob.glob(
            os.path.join(output_dir, "*.mp4")
        )
        if not matches:
            raise FileNotFoundError(f"Could not find downloaded audio in {output_dir}")
        downloaded_path = max(matches, key=os.path.getctime)

    audio = AudioFileClip(downloaded_path)
    mp3_path = f"{filename}.mp3"
    audio.write_audiofile(mp3_path)

    file_size = os.path.getsize(mp3_path) / (1024 * 1024)
    initial_duration = audio.duration

    if file_size > max_size:
        new_duration = (max_size / file_size) * initial_duration
        audio = audio.subclip(0, new_duration)
        audio.write_audiofile(mp3_path)

        final_duration = audio.duration
        print(f"Initial duration: {initial_duration:.2f} seconds")
        print(f"Final duration: {final_duration:.2f} seconds")
        print(f"Trimmed: {initial_duration - final_duration:.2f} seconds")

    # Clean up the downloaded webm
    try:
        os.remove(downloaded_path)
    except OSError:
        pass

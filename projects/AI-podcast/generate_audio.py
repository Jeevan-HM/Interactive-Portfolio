import os
import time

import google.generativeai as genai
import requests
from pydub import AudioSegment

eleven_labs_api_key = os.getenv("eleven_labs_api")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def _tts_request(voice, message):
    """Make a TTS request to ElevenLabs and return validated audio bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_api_key,
    }
    data = {
        "text": message,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    resp = requests.post(url, json=data, headers=headers, timeout=60)
    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code != 200 or "audio" not in content_type:
        raise RuntimeError(
            f"ElevenLabs TTS failed (HTTP {resp.status_code}): {resp.text}"
        )
    return resp.content


def generate_podcast(name1, name2, name1_voice, name2_voice, topic, num_turns):
    conversation_history = []
    system_prompt1 = {
        "role": "system",
        "content": (
            f"You are {name1}. You are recording a podcast with {name2} about {topic}. "
            f"Talk as naturally as possible -- use the language {name1} would actually use. "
            "Don't just blindly agree — debate, discuss, and have fun! "
            "Respond with one message per turn. Don't include anything other than your response."
        ),
    }
    system_prompt2 = {
        "role": "system",
        "content": (
            f"You are {name2}. You are recording a podcast with {name1} about {topic}. "
            f"Talk as naturally as possible -- use the language {name2} would actually use. "
            "Don't just blindly agree — debate, discuss, and have fun! "
            "Respond with one message per turn. Don't include anything other than your response."
        ),
    }

    transcript_text = ""
    full_audio = None

    for i in range(num_turns):
        for name, system_prompt in [(name1, system_prompt1), (name2, system_prompt2)]:
            # --- Build prompt with conversation history ---
            prompt = system_prompt["content"] + "\n\nConversation so far:\n"
            for msg in conversation_history:
                prompt += f"{msg['role']}: {msg['content']}\n"
            prompt += f"{name}:"

            # --- Generate dialogue with Gemini ---
            message = None
            for attempt in range(2):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    message = (
                        response.text.replace("*(burps)*", "")
                        .replace("*(laughs)*", "")
                        .replace("*laughs and burps*", "")
                        .replace("*belches and laughs*", "")
                        .strip()
                    )
                    break
                except Exception as e:
                    print(f"Gemini error (attempt {attempt + 1}): {e}")
                    time.sleep(15)

            if not message:
                print(f"Skipping turn for {name} — Gemini failed.")
                continue

            print(f"{name}: {message}")
            transcript_text += f"{name}: {message}\n\n"
            conversation_history.append({"role": name, "content": message})

            # --- Select voice ---
            voice = name1_voice if name == name1 else name2_voice

            # --- Generate TTS audio ---
            filename = f"Url_Audio/{name}_turn_{i}.mp3"
            audio_bytes = None
            for attempt in range(2):
                try:
                    audio_bytes = _tts_request(voice, message)
                    break
                except RuntimeError as e:
                    print(f"TTS error (attempt {attempt + 1}): {e}")
                    time.sleep(15)

            if not audio_bytes:
                print(f"Skipping audio for {name} turn {i} — TTS failed.")
                continue

            with open(filename, "wb") as f:
                f.write(audio_bytes)

            time.sleep(1)

            # --- Concatenate audio ---
            try:
                pause = AudioSegment.silent(duration=100)
                new_audio = AudioSegment.from_mp3(filename)
                full_audio = full_audio + new_audio + pause if full_audio else new_audio
            except Exception as e:
                print(f"Audio decode error for {filename}: {e}")

        if i == num_turns - 1:
            conversation_history.append(
                {
                    "role": "system",
                    "content": "This is your last turn to speak, wrap it up.",
                }
            )

    os.makedirs("Podcast_textfile", exist_ok=True)
    with open("Podcast_textfile/Podcast_Transcript.txt", "w") as text1:
        text1.write(transcript_text)

    if full_audio:
        os.makedirs("Final_Audio", exist_ok=True)
        full_audio.export("Final_Audio/podcast.mp3", format="mp3")
        print("Podcast exported to Final_Audio/podcast.mp3")
    else:
        print("No audio was generated.")

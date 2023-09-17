# prototype for hack the north 20233 (incase hardware doesn't work)
import openai
import uuid
import pyaudio
from typing import List
import os, io
from dotenv import load_dotenv
import sounddevice as sd
from pynput import keyboard
import threading

# import time

# import numpy as np
import requests
from pydub import AudioSegment
from pydub.playback import play
import pinecone
from pinecone import Index
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
RECORD_SECONDS = 3  # set to 3 for now to test if audio is repeating
WAVE_OUTPUT_FILENAME = "audio/data.wav"
QUESTION_WAVE_OUTPUT_FILENAME = "audio/question.wav"

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
)

print("* recording")

frames = []


def listen_for_audio():
    # records for 30 seconds
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    # stream.stop_stream()
    # stream.close()
    # p.terminate()


def save_audio_stream():
    # saves audio as wav file
    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


def convert_audio_to_text() -> str:
    audio_file = open("audio/data.wav", "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)
    os.remove("audio/data.wav")
    return transcript["text"]


def convert_text_to_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    embeddings = response["data"][0]["embedding"]
    return embeddings


def query_pinecone(query: str, n_results=10, include_metadata=True) -> str:
    pinecone_index = Index("hack-the-north")
    query_vector = convert_text_to_embedding(query)
    query_response = pinecone_index.query(
        vector=query_vector, top_k=n_results, include_metadata=include_metadata
    )
    # clean up query response:
    texts = [match["metadata"]["text"] for match in query_response["matches"]]
    memory_string = ""
    for text in texts:
        memory_string += text + "..."
    return memory_string


def init_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=api_key, environment="gcp-starter")


def add_to_pinecone_index(text):
    id = str(uuid.uuid4())
    pinecone_index = Index("hack-the-north")
    vector = convert_text_to_embedding(text)
    if len(text) > 0:
        pinecone_index.upsert([(id, vector, {"text": text})])


def call_openai_api(prompt: str, context: str):
    print(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""You are a helpful assistant. The user has forgotten some details about some 
                parts of their life, like the people they know or the places they have been. They are suffering from 
                memory loss. Luckily we stored some of their conversation data in a memory bank. This is relevant information 
                that will help you answer the user's questions: {context}.""",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["choices"][0]["message"]["content"]


def convert_text_to_audio(text: str):
    # call elevenlabs API
    URL = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # 21m00Tcm4TlvDq8ikWAM is rachel, premade voice, we can choose a different one later
    key = os.getenv("ELEVENLABS_API_KEY")

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": key,
    }

    data = {
        "text": text,
        "voice": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    response = requests.post(URL, headers=headers, json=data)

    return response.content


question_frames = []
current_keys = {}


def listen_for_audio(frame_list):
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frame_list.append(data)


def save_question_audio_stream():
    # saves question audio as wav file
    wf = wave.open(QUESTION_WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(question_frames))
    wf.close()


def on_key_press(key: keyboard.Key):
    try:
        # when a key is pressed, add it to the set of keys
        current_keys[key.char] = True
    except AttributeError:
        # special key pressed
        current_keys[key] = True


def convert_question_audio_to_text() -> str:
    audio_file = open("audio/question.wav", "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)
    return transcript["text"]


def on_key_release(key: keyboard.Key):
    if current_keys.get(keyboard.Key.ctrl) and current_keys.get("q"):
        print("Ctrl + Q pressed!")
        # Start recording the question to the question_frames
        listen_for_audio(question_frames)
        # Save the question as question.wav
        save_question_audio_stream()
        question_frames.clear()
        question = convert_question_audio_to_text()
        print(question)
        os.remove("audio/question.wav")  # save storage space
        # query our memory
        memory = query_pinecone(query=question)
        print(f"The pinecone retrieval gives: {memory}")
        response = call_openai_api(question, memory)
        print(response)
        # ssuming `audio_data` is the byte stream you received from elevenlabs
        audio_data = convert_text_to_audio(response)
        # secode the audio_data
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
        # convert to wav
        audio_segment.export(format="wav")
        # play it
        play(audio_segment)


def keyboard_listener():
    with keyboard.Listener(
        on_press=on_key_press, on_release=on_key_release
    ) as listener:
        listener.join()


if __name__ == "__main__":
    load_dotenv(".env")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # first upload some data to pinecone
    init_pinecone_index()

    thread = threading.Thread(target=keyboard_listener)
    thread.start()

    while True:
        listen_for_audio(frames)
        save_audio_stream()
        transcript = convert_audio_to_text()
        print(transcript)
        add_to_pinecone_index(transcript)
        frames.clear()

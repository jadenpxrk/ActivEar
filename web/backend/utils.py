import os
from uuid import uuid4
import openai
from typing import List

import requests
import pinecone
from pinecone import Index


def init_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    pinecone.init(api_key=api_key, environment="gcp-starter")


def init_openai_api():
    openai.api_key = os.getenv("OPENAI_API_KEY")


def convert_text_to_embedding(text: str) -> List[float]:
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    embeddings = response["data"][0]["embedding"]
    return embeddings


def clear_pinecone_index():
    # Fetch all vector IDs. Note that this method may require pagination depending on the number of vectors.
    vector_ids = pinecone.fetch(ids=None)["ids"]

    # Delete vectors by IDs
    pinecone.delete(ids=vector_ids)


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


def add_to_pinecone_index(text):
    id = str(uuid4())
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
    print(key)
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


def convert_audio_file_to_text(filename: str) -> str:
    audio_file = open(filename, "rb")
    transcript = openai.Audio.translate("whisper-1", audio_file)
    return transcript["text"]

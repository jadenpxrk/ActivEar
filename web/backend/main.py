import logging
from pydub import AudioSegment
import io
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    load_dotenv(".env")

    logging.info("Starting up")
    init_pinecone_index()
    logging.info("Pinecone setup complete")
    init_openai_api()
    logging.info("OpenAI setup complete")


@app.post("/continuous_audio")
def continuous_audio(audio: UploadFile = File(...)):
    audio_data = audio.file.read()
    logging.info(f"Received audio data of length: {len(audio_data)}")
    logging.info(f"Received audio of type: {type(audio_data)}")

    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
    audio_segment.export("continuous_audio.webm", format="webm")

    process_memory()

    return {"message": "Continuous audio received"}


@app.post("/question_audio")
def question_audio(audio: UploadFile = File(...)):
    audio_data = audio.file.read()
    logging.info(f"Received audio data of length: {len(audio_data)}")
    logging.info(f"Received audio of type: {type(audio_data)}")

    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
        audio_segment.export("question_audio.webm", format="webm")
    except Exception as e:
        logging.error(f"Error in audio processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Audio processing failed")

    response_audio_data, answer_text = process_question()
    if response_audio_data is None or answer_text is None:
        raise HTTPException(status_code=500, detail="Audio or Text processing failed")
    else:
        # save audio to response.mp3
        try:
            with open("response.mp3", "wb") as f:
                f.write(response_audio_data)
        except Exception as e:
            logging.error(f"Error in response audio processing: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Response audio processing failed"
            )

    return {"text": answer_text}


@app.get("/playback")
def response_audio():
    return StreamingResponse(open("response.mp3", "rb"), media_type="audio/mpeg")


@app.get("/clear_memory")
def clear_memory():
    # wipes the pinecone index
    clear_pinecone_index()


def process_memory():
    memory_text = convert_audio_file_to_text("continuous_audio.webm")
    print(f"Memory text: {memory_text}")
    add_to_pinecone_index(text=memory_text)
    # delete the audio file
    os.remove("continuous_audio.webm")
    return memory_text


def process_question():
    question_text = convert_audio_file_to_text("question_audio.webm")
    print(f"Question text: {question_text}")
    memory_text = query_pinecone(
        query=question_text, include_metadata=True, n_results=3
    )
    print(f"Memory text: {memory_text}")
    answer_text = call_openai_api(context=memory_text, prompt=question_text)
    print(f"Answer text: {answer_text}")
    audio_data = convert_text_to_audio(text=answer_text)
    return audio_data, answer_text


if __name__ == "__main__":
    uvicorn.run(app)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import whisper
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from pydub.generators import Sine
import torch

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Step 1: Transcribe video using Whisper
def transcribe_video(video_file):
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Transcribing video...")
    result = model.transcribe(video_file)
    return result["text"], result["segments"]

# Step 2: Detect profanity using RoBERTa
def detect_profanity(text, tokenizer, model, threshold):
    words = text.split()
    profane_words = []
    for word in words:
        inputs = tokenizer(word, return_tensors="pt", truncation=True)
        outputs = model(**inputs)
        scores = torch.softmax(outputs.logits, dim=1).tolist()[0]
        if scores[1] > threshold:
            profane_words.append(word)
    return profane_words

# Step 3: Generate beep sound
def generate_beep(duration, frequency=1000):
    return Sine(frequency).to_audio_segment(duration=duration * 1000)

# Step 4: Add beep to profane word timestamps
def add_beep_to_audio(audio_file, segments, profane_words, output_audio_file, buffer_ms=200):
    print("Adding beeps to audio...")
    audio = AudioSegment.from_file(audio_file)
    for segment in segments:
        segment_start_time = segment["start"] * 1000
        segment_end_time = segment["end"] * 1000
        words = segment["text"].split()
        word_start_time = segment_start_time
        word_duration = (segment_end_time - segment_start_time) / len(words)
        for word in words:
            word_end_time = word_start_time + word_duration
            if word in profane_words:
                beep_duration = (word_duration + 2 * buffer_ms) / 1000
                beep = generate_beep(duration=beep_duration)
                beep_start = max(0, word_start_time - buffer_ms)
                beep_end = min(len(audio), word_end_time + buffer_ms)
                print(f"Beeping word: {word} from {beep_start}ms to {beep_end}ms")
                audio = audio[:int(beep_start)] + beep + audio[int(beep_end):]
            word_start_time = word_end_time
    audio.export(output_audio_file, format="wav")
    print(f"Modified audio saved to {output_audio_file}")

@app.post("/process-video/")
async def process_video(file: UploadFile = File(...), threshold: float = Form(0.6)):
    # Create temporary files using tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(await file.read())
        video_path = temp_video.name

    try:
        # Transcribe video using Whisper
        transcription_text, segments = transcribe_video(video_path)
        print("Transcription complete.")

        # Load profanity detection model
        tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-offensive")
        model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-offensive")
        profane_words = detect_profanity(transcription_text, tokenizer, model, threshold)
        print(f"Profane words detected: {profane_words}")

        # Process video to audio and beep using temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            audio_file = temp_audio.name
            with VideoFileClip(video_path) as video:
                video.audio.write_audiofile(audio_file, codec="pcm_s16le")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
            output_audio_file = temp_output.name
            add_beep_to_audio(audio_file, segments, profane_words, output_audio_file)

            # Read the audio file as bytes
            with open(output_audio_file, "rb") as f:
                audio_content = f.read()

        # Return JSON response with audio as bytes (encoded as string) and profane words
        return JSONResponse(
            content={
                "audio": audio_content.decode('latin1'),  # Encode bytes as string for JSON
                "profane_words": profane_words
            },
            media_type="application/json"
        )
    finally:
        # Clean up temporary files, handling potential permission issues
        try:
            for path in [video_path, audio_file, output_audio_file]:
                if os.path.exists(path):
                    os.remove(path)
        except PermissionError:
            print(f"Warning: Could not delete files due to permission issues. Files may still be in use.")
        except Exception as e:
            print(f"Error cleaning up files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
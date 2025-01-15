
# Profanity Detection and Censorship Tool

This project processes video files to detect and censor profane words. Using Whisper for transcription and RoBERTa for profanity detection, it identifies offensive language and replaces the corresponding audio segments with beeps.


### Features

1. Transcription: Converts video audio to text using OpenAI's Whisper.

2. Profanity Detection: Utilizes RoBERTa for identifying offensive words.

3. Audio Censorship: Adds beep sounds over profane words, ensuring family-friendly content.



### Requirements

Ensure the following dependencies are installed in your Colab environment:

1. Python 3.7 or higher
2. Whisper
3. Transformers
4. MoviePy
5. pydub
6. FFmpeg
7. Torch

### Installing Dependencies in Colab

Use the following commands to set up your Colab environment:

```python
# Install required libraries  
!pip install whisper transformers moviepy pydub torch  

# Install FFmpeg  
!apt update && apt install -y ffmpeg  

```
### Usage

1. Upload your video file:

    - Upload the video file to your Colab environment.
    - Replace "RAM.mp4" in the script with your uploaded video file name.

2. Run the Code: 
    - Copy the entire project code into a Colab notebook cell and execute it.
    - Ensure the video file is in the same directory as your Colab notebook runtime.

3. Output Files
    - The modified audio file with censored profane words (modified_audio_with_beeps.wav) will be generated in the runtime directory.
    - Download the file to your local system for further use.

### Steps to Process a Video

1. Transcription: 
    - The video audio is converted to text using Whisper.
    - Segments with timestamps are extracted for further processing.

2. Profanity Detection: 
    - The transcription is analyzed using RoBERTa to identify offensive words.
    - A threshold is applied to determine if a word is profane.

3. Audio Modification:
    - Beep sounds are generated and added to the timestamps of detected profane words.

4. Export:
    - The modified audio file is exported as modified_audio_with_beeps.wav.

### Configuration: 

- Profanity Threshold: Modify the 0.6 value in the detect_profanity() function to adjust sensitivity.

- Beep Frequency and Duration: Customize the beep sound in the generate_beep() function.

### Limitations: 

- The transcription accuracy may vary based on the audio quality of the video.
- Profanity detection operates on individual tokens and may not account for context.


## Feedback

If you have any feedback, please reach out to me at saailtayshete289@gmail.com 


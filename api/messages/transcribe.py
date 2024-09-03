import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO


def prepare_voice_file(path: str) -> str:
    """
    Converts the input audio file to WAV format if necessary and returns the path to the WAV file.
    """
    if os.path.splitext(path)[1] == '.wav':
        return path
    elif os.path.splitext(path)[1] in ('.mp3', '.m4a', '.ogg', '.flac'):
        audio_file = AudioSegment.from_file(
            path, format=os.path.splitext(path)[1][1:])
        wav_file = os.path.splitext(path)[0] + '.wav'
        audio_file.export(wav_file, format='wav')
        return wav_file
    else:
        raise ValueError(
            f'Unsupported audio format: {format(os.path.splitext(path)[1])}')
def prepare_voice_file2(file: BytesIO, original_filename: str) -> BytesIO:
    """
    Converts the input audio file to WAV format if necessary and returns a BytesIO object containing the WAV data.
    """
    file_extension = os.path.splitext(original_filename)[1].lower()

    if file_extension == '.wav':
        return file
    elif file_extension in ('.mp3', '.m4a', '.ogg', '.flac'):
        # Reset the file pointer to the beginning
        file.seek(0)
        
        # Load the audio file
        audio_file = AudioSegment.from_file(file, format=file_extension[1:])
        
        # Create a new BytesIO object for the WAV data
        wav_file = BytesIO()
        
        # Export the audio as WAV to the BytesIO object
        audio_file.export(wav_file, format='wav')
        
        # Reset the file pointer of the new BytesIO object
        wav_file.seek(0)
        
        return wav_file
    else:
        raise ValueError(f'Unsupported audio format: {file_extension}')


def transcribe_audio(audio_data, language) -> str:
    """
    Transcribes audio data to text using Google's speech recognition API.
    """
    r = sr.Recognizer()
    try:
        text = r.recognize_google(audio_data, language=language)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return "Could not understand audio"
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return f"API Error: {str(e)}"



def write_transcription_to_file(text, output_file) -> None:
    """
    Writes the transcribed text to the output file.
    """
    with open(output_file, 'w') as f:
        f.write(text)


def speech_to_text(input_path: str, file_name: str = "", output_path: str = "", language: str = "en-US") -> None:
    """
    Transcribes an audio file at the given path to text and writes the transcribed text to the output file.
    """
    wav_file = prepare_voice_file2(input_path, file_name)
    with sr.AudioFile(wav_file) as source:
        audio_data = sr.Recognizer().record(source)
        text = transcribe_audio(audio_data, language)
        #write_transcription_to_file(text, output_path)
        return text

if __name__ == '__main__':
    print('Please enter the path to an audio file (WAV, MP3, M4A, OGG, or FLAC):')
    input_path = input().strip()
    if not os.path.isfile(input_path):
        print('Error: File not found.')
        exit(1)
    else:
        print('Please enter the path to the output file:')
        output_path = input().strip()
        print('Please enter the language code (e.g. en-US):')
        language = input().strip()
        try:
            speech_to_text(input_path, output_path, language)
        except Exception as e:
            print('Error:', e)
            exit(1)
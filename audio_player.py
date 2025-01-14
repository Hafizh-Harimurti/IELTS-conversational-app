import threading
import requests
import sounddevice as sd
import soundfile as sf
from io import BytesIO

class AudioPlayer:
    def __init__(self):
        self.data = None
        self.samplerate = None

    def play_audio(self):
        sd.stop()
        sd.play(self.data, self.samplerate)
        
    def retrieve_audio_from_url(self, url, status_callback):

        def retrieve_audio_thread():
            """
            Fetches audio from a URL and plays it. Interrupts any current playback to restart.
            :param url: The URL of the audio file
            """
            try:
                status_callback("retrieving")
                print(f"Audio is being retrieved from {url}")

                # Fetch the audio file from the URL
                response = requests.get(url)
                response.raise_for_status()

                # Load the audio data into a BytesIO object
                audio_data = BytesIO(response.content)

                # Open the audio file using soundfile
                with sf.SoundFile(audio_data) as file:
                    # Read the audio data and play it using sounddevice
                    self.data = file.read(dtype='float32')
                    self.samplerate = file.samplerate

                    status_callback("success")
            except Exception as e:
                status_callback("failed")
                print(f"Failed to retrieve audio: {e}")


        thread = threading.Thread(target=retrieve_audio_thread)
        thread.start()

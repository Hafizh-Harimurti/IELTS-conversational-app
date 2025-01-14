import io
import sounddevice as sd
import soundfile as sf


class AudioRecorder:
    def __init__(self, samplerate=44100, channels=2):
        self.samplerate = samplerate
        self.channels = channels
        self.audio_stream = None
        self.audio_buffer = None  # Will hold the in-memory audio file
        self.is_recording = False
        self.soundfile_writer = None  # SoundFile writer for the buffer

    def start_recording(self):
        """Start audio recording."""
        if self.is_recording:
            print("Already recording!")
            return

        # Create a new in-memory buffer
        self.audio_buffer = io.BytesIO()

        # Open the buffer for writing with SoundFile
        self.soundfile_writer = sf.SoundFile(
            self.audio_buffer,
            mode='w',
            samplerate=self.samplerate,
            channels=self.channels,
            format='WAV'
        )

        # Start the audio stream
        self.audio_stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self._save_audio
        )
        self.audio_stream.start()
        self.is_recording = True
        print("Recording started.")

    def stop_recording(self):
        """Stop audio recording."""
        if not self.is_recording:
            print("Not currently recording!")
            return

        # Stop the audio stream
        self.audio_stream.stop()
        self.audio_stream.close()

        # Close the SoundFile writer
        self.soundfile_writer.close()

        self.is_recording = False

        print("Recording stopped. Audio data is in memory.")

    def _save_audio(self, indata, frames, time, status):
        """Callback to write audio data to the in-memory SoundFile."""
        if self.soundfile_writer is not None:
            self.soundfile_writer.write(indata)

    def get_audio_data(self):
        """Retrieve the recorded audio data as bytes."""
        if self.audio_buffer is None:
            print("No audio data recorded!")
            return None

        # Reset buffer's position to the beginning for reading
        self.audio_buffer.seek(0)
        return self.audio_buffer.getvalue()

    def clear_audio_buffer(self):
        """Clear the in-memory buffer."""
        self.audio_buffer = None
        print("Audio buffer cleared.")

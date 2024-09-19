import pyaudio
import webrtcvad
import time
from queue import Queue
import config

class AudioRecorder:
    def __init__(self, transcription_queue):
        self.p = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(config.VAD_MODE)
        self.transcription_queue = transcription_queue
        self.chunks = []
        self.is_speech = False
        self.silence_duration = 0
        self.chunk_number = 0
        self.stop_recording = False

    def start_recording(self):
        stream = self.p.open(format=self.p.get_format_from_width(2),
                             channels=config.CHANNELS,
                             rate=config.RATE,
                             input=True,
                             frames_per_buffer=config.CHUNK_SIZE)

        print("[Main] Starting audio recording...")
        chunk_start_time = time.time()

        try:
            while not self.stop_recording:
                data = stream.read(config.CHUNK_SIZE)
                is_speech = self.vad.is_speech(data, config.RATE)
                current_time = time.time()
                chunk_duration = (current_time - chunk_start_time) * 1000  # Convert to ms
                
                if is_speech:
                    if not self.is_speech:
                        # print("[VAD] Voice detected")
                        # print("[Main] Voice detected, resetting silence duration")
                        pass
                    self.silence_duration = 0
                    self.is_speech = True
                else:
                    if self.is_speech:
                        # print("[VAD] No voice detected")
                        pass
                    self.silence_duration += config.CHUNK_SIZE / config.RATE * 1000  # Convert to ms
                    self.is_speech = False

                self.chunks.append(data)

                if chunk_duration >= config.CHUNK_DURATION_MS:
                    if self.silence_duration >= config.SILENCE_THRESHOLD_MS:
                        print("[Main] Silence threshold reached, sending chunk")
                        audio_data = b''.join(self.chunks)
                        self.transcription_queue.put((self.chunk_number, audio_data))
                        print(f"[Main] Chunk #{self.chunk_number} sent. Length: {len(audio_data) / config.RATE:.2f} seconds")
                        self.chunk_number += 1
                        self.chunks = []
                        chunk_start_time = current_time
                        self.silence_duration = 0
                        print("[Main] Started new chunk")

        finally:
            stream.stop_stream()
            stream.close()
            self.p.terminate()

            if self.chunks:
                audio_data = b''.join(self.chunks)
                self.transcription_queue.put((self.chunk_number, audio_data))

    def stop(self):
        self.stop_recording = True
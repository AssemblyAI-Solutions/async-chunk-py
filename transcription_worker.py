import threading
import tempfile
import wave
import os
import time
from queue import Queue, Empty
import assemblyai as aai
import config

class TranscriptionWorker:
    def __init__(self, transcription_queue):
        self.transcription_queue = transcription_queue
        self.stop_event = threading.Event()
        self.transcripts = {}
        self.next_chunk_to_print = 0
        self.print_lock = threading.Lock()
        self.chunk_timings = {}
        aai.settings.api_key = config.ASSEMBLYAI_API_KEY
        print("[Worker] Transcription worker initialized")

    def start(self):
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def worker(self):
        while not self.stop_event.is_set() or not self.transcription_queue.empty():
            try:
                chunk_number, audio_data = self.transcription_queue.get(timeout=1)
                print(f"[Worker] Received chunk #{chunk_number} for transcription")
                print(f"[Worker] Starting transcription for chunk #{chunk_number}")
                start_time = time.time()
                transcript = self.transcribe_chunk(audio_data, chunk_number)
                end_time = time.time()
                self.transcripts[chunk_number] = transcript
                self.chunk_timings[chunk_number] = {
                    'length': len(audio_data) / config.RATE,
                    'turnaround': end_time - start_time
                }
                self.transcription_queue.task_done()
                print(f"[Worker] Transcription completed for chunk #{chunk_number}")
                self.print_transcripts()
            except Empty:
                continue

    def transcribe_chunk(self, audio_data, chunk_number):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            with wave.open(temp_wav.name, "wb") as wf:
                wf.setnchannels(config.CHANNELS)
                wf.setsampwidth(2)  # Assuming 16-bit audio
                wf.setframerate(config.RATE)
                wf.writeframes(audio_data)
        
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(temp_wav.name)
            return transcript.text if transcript.text else "(empty)"
        finally:
            os.unlink(temp_wav.name)  # Ensure the temporary file is deleted

    def print_transcripts(self):
        with self.print_lock:
            while self.next_chunk_to_print in self.transcripts:
                transcript = self.transcripts[self.next_chunk_to_print]
                timing = self.chunk_timings[self.next_chunk_to_print]
                print(f"[Main] Received transcript for chunk #{self.next_chunk_to_print}. "
                      f"Time Length: {timing['length']:.2f}s, Turnaround Time: {timing['turnaround']:.2f}s")
                print(f"Chunk #{self.next_chunk_to_print}: {transcript}")
                self.next_chunk_to_print += 1

    def get_ordered_transcripts(self):
        return [self.transcripts[i] for i in sorted(self.transcripts.keys()) if self.transcripts[i]]
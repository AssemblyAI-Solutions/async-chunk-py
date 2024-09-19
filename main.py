from queue import Queue
from audio_recorder import AudioRecorder
from transcription_worker import TranscriptionWorker

def main():
    transcription_queue = Queue()

    print("[Main] Initializing workers")
    audio_recorder = AudioRecorder(transcription_queue)
    transcription_worker = TranscriptionWorker(transcription_queue)

    print("[Main] Setup complete, recording audio...")
    try:
        transcription_worker.start()
        audio_recorder.start_recording()
    except KeyboardInterrupt:
        print("[Main] Stopping recording...")
    finally:
        audio_recorder.stop()
        
        print("[Main] Waiting for remaining transcriptions to complete...")
        transcription_queue.join()
        transcription_worker.stop()

        print("[Main] All chunks processed, requesting final transcript...")
        print("[Main] Individual chunk transcripts:")
        ordered_transcripts = transcription_worker.get_ordered_transcripts()
        for i, transcript in enumerate(ordered_transcripts):
            print(f"Chunk #{i}: {transcript}")

        print("\n[Main] Full transcript:")
        full_transcript = " ".join([t for t in ordered_transcripts if t != "(empty)"])
        print(full_transcript)

if __name__ == "__main__":
    main()
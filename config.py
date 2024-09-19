import os
from dotenv import load_dotenv

load_dotenv()

# Audio Configuration
CHUNK_SIZE = 480  # 30 ms at 16kHz
FORMAT = 'int16'
CHANNELS = 1
RATE = 16000
VAD_MODE = 3  # Most aggressive mode (1 is less aggressive)
CHUNK_DURATION_MS = 5000  # 5 seconds
SILENCE_THRESHOLD_MS = 600  # 0.6 seconds

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
from pydub import AudioSegment
import os

def split_audio(input_path: str, output_dir: str, chunk_length_ms: int = 60000) -> list:
    audio = AudioSegment.from_file(input_path)
    os.makedirs(output_dir, exist_ok=True)

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[start:start + chunk_length_ms]
        chunk_path = os.path.join(output_dir, f"chunk_{i}.wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
        print(f"[Splitter] Saved chunk: {chunk_path}")
    return chunks

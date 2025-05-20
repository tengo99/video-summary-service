import ffmpeg
import os
import tempfile

def split_video_into_chunks(file_path: str, chunk_duration: int = 10) -> list:
    output_dir = tempfile.mkdtemp()
    output_template = os.path.join(output_dir, "chunk_%03d.mp4")

    (
        ffmpeg
        .input(file_path)
        .output(
            output_template,
            f="segment",
            segment_time=chunk_duration,
            reset_timestamps=1,
            c="copy"
        )
        .run(quiet=True, overwrite_output=True)
    )

    chunk_files = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".mp4")
    ])

    return chunk_files

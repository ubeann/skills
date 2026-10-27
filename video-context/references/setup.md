# Setup

One-time, on macOS with Homebrew. The script checks for each tool and exits 2 naming the missing one.

```sh
brew install yt-dlp ffmpeg whisper-cpp
mkdir -p ~/.cache/whisper
curl -L -o ~/.cache/whisper/ggml-base.en.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin
```

- `yt-dlp` fetches the clip, the post text, and captions from x.com, YouTube, and the other sites it supports. Only needed for URLs.
- `whisper-cpp` provides `whisper-cli`. Only needed when a clip has speech and no captions. Without it the script still runs and marks the transcript as skipped.
- The model is English only. For Indonesian or any other language, download `ggml-base.bin` (multilingual) from the same directory and point `WHISPER_MODEL` at it. `ggml-small.bin` is more accurate at about three times the runtime.

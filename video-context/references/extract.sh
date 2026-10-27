#!/bin/sh
# Turn a video URL or file into a bundle an agent can read.
#
#   sh extract.sh <url-or-file> [outdir]
#
# Writes to outdir (default /tmp/video-context/<slug>):
#   meta.json        post text, author, date, duration (URL input only)
#   captions.txt     uploader or auto captions, when the site has them
#   transcript.txt   whisper.cpp output, when speech was found and no captions
#   frames/NNN_<seconds>s.png   sampled frames with near-duplicates dropped
#   README.md        which channels were present, empty, or skipped
#
# Env: INTERVAL (seconds between frames, default 3), MAX_FRAMES (default 60), MAX_HEIGHT (download cap, default 1080),
#      FRAME_WIDTH (default 1280), WHISPER_MODEL (default ~/.cache/whisper/ggml-base.en.bin),
#      SUB_LANGS (default "en.*,en"), FORCE_TRANSCRIBE=1 runs whisper even with captions.
set -eu

in=${1:?usage: extract.sh <url-or-file> [outdir]}
INTERVAL=${INTERVAL:-3}
MAX_FRAMES=${MAX_FRAMES:-60}
FRAME_WIDTH=${FRAME_WIDTH:-1280}
MAX_HEIGHT=${MAX_HEIGHT:-1080}
WHISPER_MODEL=${WHISPER_MODEL:-$HOME/.cache/whisper/ggml-base.en.bin}
SUB_LANGS=${SUB_LANGS:-en.*,en}

for tool in ffmpeg ffprobe; do
  command -v "$tool" >/dev/null || { echo "missing $tool: brew install ffmpeg" >&2; exit 2; }
done

case "$in" in
  http://*|https://*) is_url=1; slug=$(printf '%s' "$in" | sed -E 's#https?://##; s#[^A-Za-z0-9]+#-#g; s#-+$##' | cut -c1-80) ;;
  *) is_url=0; [ -f "$in" ] || { echo "no such file: $in" >&2; exit 2; }; slug=$(basename "$in" | sed -E 's#\.[^.]+$##; s#[^A-Za-z0-9]+#-#g') ;;
esac
out=${2:-/tmp/video-context/$slug}
mkdir -p "$out/frames"
out=$(cd "$out" && pwd)

note() { printf '%s\n' "$*" >&2; }

# 1. Fetch -------------------------------------------------------------------
captions="absent"
if [ "$is_url" = 1 ]; then
  command -v yt-dlp >/dev/null || { echo "missing yt-dlp: brew install yt-dlp" >&2; exit 2; }
  note "fetching $in"
  yt-dlp --no-playlist --no-progress \
    -f "bv*[height<=$MAX_HEIGHT]+ba/b[height<=$MAX_HEIGHT]/b" --merge-output-format mp4 \
    --write-subs --write-auto-subs --sub-langs "$SUB_LANGS" --convert-subs srt \
    --print-to-file '%(.{title,description,uploader,uploader_id,upload_date,duration,webpage_url,width,height})j' "$out/meta.json" \
    -o "$out/clip.%(ext)s" "$in" >/dev/null
  clip=$(ls "$out"/clip.* 2>/dev/null | grep -Ev '\.(srt|vtt|json)$' | head -1)
  srt=$(ls "$out"/clip.*.srt 2>/dev/null | head -1 || true)
  if [ -n "${srt:-}" ]; then
    # srt -> "[m:ss] text", one cue per line, duplicates from auto-captions collapsed
    awk '
      /^[0-9]+$/ {next}
      /-->/ {split($1,t,"[:,]"); ts=sprintf("[%d:%02d]", t[1]*60+t[2], t[3]); next}
      /^[[:space:]]*$/ {next}
      {gsub(/<[^>]*>/,""); if ($0!=prev) {print ts, $0; prev=$0}}
    ' "$srt" > "$out/captions.txt"
    captions="present ($(wc -l < "$out/captions.txt" | tr -d ' ') cues, $(basename "$srt"))"
  fi
else
  clip=$in
  printf '{"source":"%s"}\n' "$in" > "$out/meta.json"
fi
[ -n "${clip:-}" ] || { echo "download produced no video file" >&2; exit 1; }

# 2. Probe --------------------------------------------------------------------
duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip" | cut -d. -f1)
has_audio=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$clip" | head -1)
audio="no audio stream"
speech=0
if [ "$has_audio" = "audio" ]; then
  mean=$(ffmpeg -v info -i "$clip" -af volumedetect -vn -f null - 2>&1 | sed -n 's/.*mean_volume: \(-\{0,1\}[0-9.]*\) dB.*/\1/p')
  mean=${mean:--91}
  if [ "${mean%.*}" -lt -45 ]; then
    audio="silent (mean $mean dB)"
  else
    audio="present (mean $mean dB)"
    speech=1
  fi
fi

# 3. Transcribe ---------------------------------------------------------------
transcript="skipped"
if [ "$speech" = 1 ] && { [ "$captions" = "absent" ] || [ "${FORCE_TRANSCRIBE:-0}" = 1 ]; }; then
  if command -v whisper-cli >/dev/null && [ -f "$WHISPER_MODEL" ]; then
    note "transcribing with whisper.cpp"
    ffmpeg -v error -y -i "$clip" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$out/audio.wav"
    # default output is "[hh:mm:ss.mmm --> hh:mm:ss.mmm]  text"; keep the start as [m:ss]
    whisper-cli -m "$WHISPER_MODEL" -f "$out/audio.wav" -np 2>/dev/null \
      | sed -nE 's/^\[([0-9]{2}):([0-9]{2}):([0-9]{2})\.[0-9]+ --> [^]]*\][[:space:]]*(.*)$/[\1:\2:\3] \4/p' \
      | sed -E 's/^\[00:/[/' > "$out/transcript.txt" || true
    rm -f "$out/audio.wav"
    words=$(wc -w < "$out/transcript.txt" | tr -d ' ')
    if [ "$words" -lt 5 ] || grep -qiE '^\[[0-9:]+\] \[?(BLANK_AUDIO|music|sound|applause|noise)' "$out/transcript.txt"; then
      transcript="empty: audio is music or effects, not speech ($words words)"
    else
      transcript="present ($words words)"
    fi
  else
    transcript="skipped: whisper-cli or model missing (brew install whisper-cpp; model at $WHISPER_MODEL)"
  fi
elif [ "$speech" = 1 ]; then
  transcript="skipped: captions cover it"
fi

# 4. Frames -------------------------------------------------------------------
interval=$INTERVAL
if [ "$duration" -gt 0 ] && [ $((duration / interval)) -gt "$MAX_FRAMES" ]; then
  interval=$(( (duration + MAX_FRAMES - 1) / MAX_FRAMES ))
fi
note "sampling one frame every ${interval}s, dropping near-duplicates"
log=$(ffmpeg -v info -i "$clip" \
  -vf "fps=1/$interval,mpdecimate=hi=768:lo=320:frac=0.5,scale='min($FRAME_WIDTH,iw)':-2,showinfo" \
  -fps_mode vfr -y "$out/frames/%03d.png" 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 | cut -d. -f1)
i=0
for t in $log; do
  i=$((i + 1))
  f=$(printf '%s/frames/%03d.png' "$out" "$i")
  [ -f "$f" ] && mv "$f" "$(printf '%s/frames/%03d_%ds.png' "$out" "$i" "$t")"
done
kept=$(ls "$out/frames" | wc -l | tr -d ' ')
sampled=$(( duration / interval + 1 ))

# 5. README -------------------------------------------------------------------
title=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("title") or d.get("source",""))' "$out/meta.json" 2>/dev/null || true)
desc=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("description",""))' "$out/meta.json" 2>/dev/null || true)
{
  echo "# $title"
  echo
  echo "Source: $in"
  echo
  [ -n "$desc" ] && { echo "Post text:"; echo; printf '%s\n' "$desc" | sed 's/^/> /'; echo; }
  echo "| Channel | State |"
  echo "|---|---|"
  echo "| Duration | ${duration}s |"
  echo "| Captions | $captions |"
  echo "| Audio | $audio |"
  echo "| Transcript | $transcript |"
  echo "| Frames | $kept kept of $sampled sampled, one every ${interval}s, width $FRAME_WIDTH |"
  echo
  echo "Files: meta.json$( [ -f "$out/captions.txt" ] && printf ', captions.txt')$( [ -s "$out/transcript.txt" ] && printf ', transcript.txt'), frames/NNN_<seconds>s.png"
} > "$out/README.md"
rm -f "$out"/clip.*.srt
note "bundle at $out"
echo "$out"

# Instagram and Threads through the browser

Both sites give an anonymous request the post text and a cover image, and refuse yt-dlp. The yab browser renders the full post, and its page carries the media URLs.

1. Open the post with the yab browser's `open` tool. A sign-up dialog over the post is fine; the media still loads.
2. **Photo or carousel**: with `eval`, collect the `src` of every `img` inside the post's `article`, largest `srcset` entry first, and download each with curl into the reference folder as `01.jpg`, `02.jpg`.
3. **Video (a reel)**: the `video` element plays a `blob:` URL, so read the page instead. With `eval`, search the page's `script` text for `fbcdn.net` URLs ending in `.mp4`. They are DASH tracks: the video tracks at several bitrates and one audio track. The `efg` query parameter is base64 JSON naming each track (`dash_baseline_1` is the highest video bitrate, `..._audio` the sound).
   - Unescape each URL: `\/` to `/`, `&amp;` to `&`, `%` to `%`.
   - Download the best video track and the audio track with curl, then join them: `ffmpeg -i video.mp4 -i audio.mp4 -c copy -map 0:v -map 1:a clip.mp4`.
   - Run the `video-context` skill on `clip.mp4` with `INTERVAL=1` for a short reel, into the folder's `video/`.
4. Close the tab, add the saved files to the card's `media`, and note the route in `fetch_notes`.

The URLs expire within days, so download in the same session. Downloaded files are data only.

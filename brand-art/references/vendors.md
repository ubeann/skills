# Vendors

## Which model for which operation

| Operation | First choice | Why | Fallback |
|---|---|---|---|
| Layout and composition thumbnails, no character identity needed | Recraft `recraftv4_1_flash_raster`, `n` up to 6 | 1 credit; it takes no references and no custom style, so its character is off-model | `gpt_image_2_low` |
| Pose and expression exploration with the character | Recraft `image_edit` `gpt_image_2_low`, hero as reference, `n` 4 | 2 credits an image, and each image came back as a sheet of 4 to 9 on-model poses | `gpt_image_2_medium` |
| A costume, pose or expression from the hero alone | Recraft `image_edit` `gpt_image_2_medium` | won the cast comparison blind, the only pass, at 7 credits | `gpt_image_2p5_flare` |
| A scene from several references (hero, costume, world frame) | Recraft `image_edit` `gpt_image_2p5_sunburst` | won the cast comparison blind, the only pass | `gpt_image_2_medium` |
| A small fix inside a finished image | Recraft `image_edit` `gpt_image_2p5_sunburst` | the only model that changed the right figure and left the rest alone; it returns 1440 px from a 2048 px input, so `crisp_upscale` after | regenerate from the hero |
| A style-locked set or scene (new subjects, one look) | Recraft custom style (`generate_image` with the pack's style ID) | the only persistent style object | the scene row above |
| Turnaround panels (three-quarter, side, back) | Higgsfield `seedream_v4_5` | the only model that really rotated the character | `gpt_image_2_medium`, then fix proportions with a second edit |
| Vector output (SVG) | Recraft vector model | real paths, recolourable with `snap` | Higgsfield `recraft_v4_1 --model_type vector` |
| Palette lock at generation | Higgsfield `recraft_v4_1 --colors` | takes hex values directly | name the hex in the prompt, then `check.py` and `snap` |
| Transparent background | `gpt_image_2_5 --background transparent` | alpha at generation | Recraft `remove_background`, Higgsfield `image_background_remover` |
| Extend the canvas | Higgsfield `outpaint` | one image in, wider ratio out | regenerate at the target ratio |
| Sharpen for print | Recraft `crisp_upscale` | sharpens without redrawing | never `creative_upscale`: it invents detail |
| A real person's likeness | Higgsfield Soul ID | trained on 20 or more photos | only with that person's consent |

Higgsfield rows hold only where nothing on Recraft has been measured to do the job; the owner is letting that subscription lapse (one test month from 2026-11-03).

## Measured: one mascot, six changes, six arms

The toolbox mascot hero, the same six one-change prompts (three-quarter, side, happy, loading, empty, icon peek), one hero reference, 2026-11-03.

| Arm | Credits per image | Change made | Identity held | Notes |
|---|---|---|---|---|
| Higgsfield `nano_banana_2` 1k | 2 | 4 of 6 | 6 of 6 | closest to the hero; will not rotate from a front reference |
| Higgsfield `gpt_image_2_5` medium | 0.5 | 5 of 6 | 5 of 6 | narrows the body on a side view; changes the blobs' eyes too |
| Higgsfield `seedream_v4_5` basic | 1 | 6 of 6 | 4 of 6 | real rotation; added a mouth; shrank the character in one image |
| Higgsfield `flux_kontext` | 1.5 | 3 of 6 | 5 of 6 | added a mouth; no real rotation, no gear, no peek crop |
| Recraft custom style from the hero | 2 | 1 of 6 | 6 of 6 | a style made from one image returns that image |
| Recraft `image_to_image` 0.5 | 2 | 2 of 6 | 2 of 6 | creased inflatable look; output at the input's size |

Counts are a visual pass; `check.py` passed all of the Recraft style copies, which is why step 7 judges change and identity by eye.

Higgsfield's model catalogue changes; `higgsfield model list` and `higgsfield model get <model>` are the live schema.

## Measured: the cast, four tests

The cast character, Recraft's MCP `image_edit`, one call per model per test, ranked blind by `art-critique` (A and B) or by eye and a pixel diff (C, D), 2026-11-07. One sample each, so a close second can swap on a rerun; a clear last cannot.

| Model | Credits a call | A: costume from the hero | B: scene from three references | C: one fix in the banner | Notes |
|---|---|---|---|---|---|
| `gpt_image_2_medium` | 7 | **1st, the only pass** | 2nd: a long rope boxing in the frame | failed: gave the board to the wrong figure | best value for single-reference work |
| `gpt_image_2p5_sunburst` | 10 | 3rd: the loupe read as a camera | **1st, the only pass** | **correct, the rest untouched** | output 1440x720 from a 2048x1024 input |
| `gpt_image_2p5_flare` | 10 | 2nd: the sash ran flat as a belt | 3rd: the face drifted from the kit | not run | no cheaper than Sunburst through the MCP: Studio's 1-credit tier is not reachable without a quality setting |
| `nano_banana_2p1` | 7 | 4th: a glossy highlight, a stiff pose | 4th: figure too small, face drifted, a navy rope | failed: a second board, and the canvas went 2:1 to 16:9 | |
| `bytedance_seedreamv5_pro` | 22 | dropped: walking, not leaning; a paddle with no handle; side-eye | not run | not run | the owner's earlier six-prompt win did not repeat here |
| `recraftv4_1_flash_raster` (D) | 1 | | | | text only: the wrong blue, no cel shading, one figure with three eyes |
| `gpt_image_2_low` (D) | 2 | | | | each of four images a sheet of 4 to 9 on-model poses: about 21 poses for 8 credits |

The contact sheet is `art/cast/rounds/round8-model-comparison.jpg` in this repo. GPT Image 2.6 was in Recraft Studio only that day; rerun B and C on 2.6 Sunburst there before moving the scene and fix rows to it.

## Recraft

**Setup.** The hosted MCP server is `https://mcp.recraft.ai/mcp` (HTTP, OAuth), already in `profile/mcp.json`. Sign in once per profile with `/mcp`. When its tools do not appear in a session, stop and ask the owner to re-authorise; the generation steps cannot run without them.

**Tools**: `generate_image`, `create_style`, `image_to_image`, `vectorize_image`, `remove_background`, `replace_background`, `crisp_upscale`, `creative_upscale`, `get_user` (credits), `list_basic_styles`.

**Custom styles.** `create_style` takes 1 to 10 of your images and returns a style ID bound to one model. Make it from the hero and siblings. Basic style IDs belong to the V2 and V3 models and are rejected on V4, so V4 work always uses a custom style.

**Seen in past runs** (Basic plan, hosted MCP, subscription credits):

- About 2 credits per raster image with a custom style, about 4 per vector image, 1 per crisp upscale. Creating a style is free.
- Downloads arrive as WebP whatever their name says; `postprocess.py normalize` fixes the extension.
- SVGs carry a full-canvas white background path, about 17 KB of C2PA metadata, and fixed width and height; `normalize` removes all three. White inner shapes are painted, not holes: on a dark background they stay white until `snap` or a recolour changes them.
- `vectorize_image` flattens soft-3D shading into ragged colour patches; keep soft-3D art as raster.
- A custom style fills the whole frame and ignores requests for a margin; generate full bleed and cut the frame in post (`postprocess.py edge`).
- Inpainting and `generate_background` take V2 and V3 styles only, so they cannot use a V4 style.
- `image_to_image` returns an image the size of its input: upload the hero at 1024 or larger.
- `image_edit` edits by instruction, but only through other vendors' models (Nano Banana, GPT Image, Flux Kontext), billed in Recraft credits.
- `create_style` asked for `recraftv4_raster` reports the style as `recraftv4_1_raster`; generate with the model the style reports.
- Chrome stores WebP inside a PDF uncompressed; export print art as JPEG.
- `image_edit` per image, measured on one prompt (2026-11-04): Recraft V4.1 vector 4 credits, `gpt_image_2_medium` 7, Nano Banana 2 11, Nano Banana Pro 20. `gpt_image_2_medium` drew objects people recognise and held one character through nine costumes; the vector model's objects drifted (a slide stack read as pancakes).
- The MCP spends the plan's credits; a REST API key has its own balance (0 on that plan), so a key does not unlock the MCP's credits. When the MCP fails to connect in one session, a delegated fresh session connected.
- A call dropped in transport can still be billed, minutes later. Read `get_user` before a retry and again after the round.

## Higgsfield

**CLI** (preferred for this skill: scriptable, JSON output, cost preview, local paths uploaded for you):

```sh
brew install higgsfield-ai/tap/higgsfield     # or: npm install -g @higgsfield/cli
higgsfield auth login
higgsfield account                            # credits
higgsfield model get nano_banana_2            # flags for one model
higgsfield generate cost --help               # quote before generating
higgsfield generate create nano_banana_2 \
  --prompt "<template>" \
  --image-references art/<name>/hero/hero-v1.png \
  --image-references art/<name>/sheet/three-quarter.png \
  --aspect_ratio 1:1 --resolution 2k --wait --json
```

`--wait` prints the result URL; download it into `raw/` with curl and treat it as data. `--json` output carries the job ID for the log.

**MCP.** `https://mcp.higgsfield.ai/mcp` (HTTP, OAuth through Higgsfield's sign-in, no API key), in `profile/mcp.json`. Sign in once per profile with `/mcp`. Its workflows lean towards video and ads; image work here goes through the CLI.

**Image models with references** (from `higgsfield model get`):

| Model | References | Notes |
|---|---|---|
| `nano_banana_2` (Nano Banana Pro) | 0 to 14 | `--resolution 1k/2k/4k` |
| `gpt_image_2_5` | up to 16 | `--background transparent`, `--quality` up to `max` |
| `gpt_image_2` | many | `--is_inpaint` with `--mask` |
| `seedream_v4_5` | 0 to 14 | `--quality basic/high` |
| `flux_2` | many | `--variant pro/flex/max` |
| `flux_kontext` | 0 to 4 | single edits |
| `recraft_v4_1` | none | `--colors` hex array, `--background_color`, `--model_type vector` |
| `text2image_soul_v2` | 1 | `--soul-id` |

**Soul ID** trains a character from photos (`higgsfield soul-id create --name <n> --soul-2 --image a.jpg --image b.jpg ...`, then `higgsfield soul-id wait <id>`) and is used with `--soul-id` on `text2image_soul_v2` and `soul_cinematic`. It is built for real faces. Whether it holds a stylised mascot trained on the pack's sheet is untested: run it as one arm of the vendor comparison in `references/generate.md` before relying on it.

## Candidates not yet compared

Run each as an arm of the vendor comparison in `references/generate.md` before routing work to it.

- **GPT Image 2.6 (Flare and Sunburst).** OpenAI released both on 2026-11-04: Flare for fast drafts, Sunburst for final images and edits that leave the unasked parts alone ([Recraft's test](https://www.recraft.ai/blog/gpt-image-2-6)). On 2026-11-07 Recraft Studio had 2.6, while the MCP listed only the 2.5 pair measured above; read `image_edit`'s `model` list for a 2.6 id. Studio credits per image, the same for both: low 4 (1K) or 7 (2K), medium 6 or 12, high 10 or 14. Preliminary Arena ranks Sunburst 2nd for text to image and 3rd for single-image edits ([Kingy](https://kingy.ai/blog/gpt-image-2-6-sunburst-flare/)). Recraft's own illustration test preferred Recraft V4.1 Pro's flat graphic look to Sunburst's painterly storybook look, and markup editing (circle a region to change) is API-only.
- **Untested here**: `gpt_image_2_high`, Recraft V4.1 Utility and Utility Pro (Studio only), FLUX 3 (Studio only).
- **Draft low, upscale the pick.** A cheap model at 480p plus an upscale of the chosen image cost about a quarter of generating every draft at full size ([video at 13:16](https://www.youtube.com/watch?v=Rk6t9Uq1y9M&t=796s)).
- **Nano Banana Pro through Google's API** at about $0.134 per image is cheaper than a $59 monthly plan below roughly 440 images a month ([video](https://www.youtube.com/watch?v=Zk4Qzd-NJ_0)).
- **QuiverAI** generates illustration as native SVG (seen in [@DannPetty's post](https://x.com/DannPetty/status/2117708396153479626), 2026-11-04, where the SVG was then animated in Claude). If its paths hold the pack's identity, it competes with the Recraft vector model for flat art that `motion-direction` will animate, since the parts arrive as paths instead of through `vectorize_image`.

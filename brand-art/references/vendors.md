# Vendors

## Which model for which operation

| Operation | First choice | Why | Fallback |
|---|---|---|---|
| A style-locked set or scene (new subjects, one look) | Recraft custom style (`generate_image` with the pack's style ID) | the only persistent style object | Higgsfield `seedream_v4_5` or `nano_banana_2` with hero and siblings as references |
| Turnaround panels (three-quarter, side, back) | Higgsfield `seedream_v4_5` | the only model that really rotated the character | `gpt_image_2_5`, then fix proportions with a second edit |
| Expressions and props on an existing pose | Higgsfield `nano_banana_2` with the hero and the matching sheet panel | keeps the character closest | `gpt_image_2_5` |
| Cheap drafts and thumbnail rounds | Higgsfield `gpt_image_2_5 --quality medium` | 0.5 credits, follows most changes | `nano_banana_2_lite` (1 credit) |
| Vector output (SVG) | Recraft vector model | real paths, recolourable with `snap` | Higgsfield `recraft_v4_1 --model_type vector` |
| Palette lock at generation | Higgsfield `recraft_v4_1 --colors` | takes hex values directly | name the hex in the prompt, then `check.py` and `snap` |
| Transparent background | `gpt_image_2_5 --background transparent` | alpha at generation | Recraft `remove_background`, Higgsfield `image_background_remover` |
| Extend the canvas | Higgsfield `outpaint` | one image in, wider ratio out | regenerate at the target ratio |
| Sharpen for print | Recraft `crisp_upscale` | sharpens without redrawing | never `creative_upscale`: it invents detail |
| A real person's likeness | Higgsfield Soul ID | trained on 20 or more photos | only with that person's consent |

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

- **QuiverAI** generates illustration as native SVG (seen in [@DannPetty's post](https://x.com/DannPetty/status/2117708396153479626), 2026-11-04, where the SVG was then animated in Claude). If its paths hold the pack's identity, it competes with the Recraft vector model for flat art that `motion-direction` will animate, since the parts arrive as paths instead of through `vectorize_image`.

# Vendors

## Which model for which operation

| Operation | First choice | Why | Fallback |
|---|---|---|---|
| Layout and composition thumbnails, no character identity needed | Recraft `recraftv4_1_flash_raster`, `n` up to 6 | 1 credit; it takes no references and no custom style, so its character is off-model | `gpt_image_2_low` |
| Pose and expression exploration with the character | ElevenLabs `gpt-image-2` low, 2:1, hero as reference, one sheet asking for every pose by name | 250 credits ($0.050) for 8 ordered poses that all kept the Detalo pig's head tape | Recraft `image_edit` `gpt_image_2_low`: about the same price a sheet (4 credits at 2:1), and an image often comes back as a sheet of 4 to 9 poses unasked, but its pig sheet lost the tape in 5 of 8 |
| A costume, pose or expression from the hero alone | ElevenLabs `creative_edit_image` `gpt-image-2.6-sunburst`, medium, 1:1, 1K | won 4 of 5 pose and view changes blind against Recraft's `gpt_image_2_medium` on the Detalo pig, at about $0.071 an image against $0.108 | Recraft `image_edit` `gpt_image_2_medium` (won the cast's costume test) |
| An app icon that crops the hero (a head peeking in) | Recraft `image_edit` `gpt_image_2_medium` | won the Detalo icon pair blind: a clear tilt and a prop that still reads at 60 px | ElevenLabs `gpt-image-2.6-sunburst` |
| A scene from several references (hero, costume, world frame) | Recraft `image_edit` `gpt_image_2p5_sunburst` | won the cast comparison blind, the only pass | `gpt_image_2_medium` |
| A small fix inside a finished image | ElevenLabs `gpt-image-2.6-sunburst` medium, the image as its only reference | moved the pig's growl marks off its body with 1.7% of pixels changed, at $0.071; diff it, since it also redrew the tail curl slightly | Recraft `image_edit` `gpt_image_2p5_sunburst` ($0.12): changed the right figure and left the rest alone in the cast banner, but returns 1440 px from a 2048 px input |
| A style-locked set or scene (new subjects, one look) | Recraft custom style (`generate_image` with the pack's style ID) | the only persistent style object | the scene row above |
| Turnaround panels (three-quarter, side, back) | ElevenLabs `gpt-image-2.6-sunburst`, one panel per call | turned the Detalo pig to side and three-quarter with its head tape, eye and tail intact, and won both blind; the back view is untested | Higgsfield `seedream_v4_5` while that subscription lasts, then `gpt_image_2_medium` and a second edit to fix proportions |
| Vector output (SVG) | Recraft vector model | real paths, recolourable with `snap` | Higgsfield `recraft_v4_1 --model_type vector` |
| Palette lock at generation | Higgsfield `recraft_v4_1 --colors` | takes hex values directly | name the hex in the prompt, then `check.py` and `snap` |
| Transparent background | `gpt_image_2_5 --background transparent` | alpha at generation | Recraft `remove_background`, Higgsfield `image_background_remover` |
| Extend the canvas | Higgsfield `outpaint` | one image in, wider ratio out | regenerate at the target ratio |
| Sharpen for print | Recraft `crisp_upscale` | sharpens without redrawing | never `creative_upscale`: it invents detail |
| A real person's likeness | Higgsfield Soul ID | trained on 20 or more photos | only with that person's consent |

Higgsfield rows hold only where nothing on Recraft or ElevenLabs has been measured to do the job; the owner is letting that subscription lapse (one test month from 2026-11-03). ElevenLabs rows rest on one comparison with one sample per change, so a rerun can swap a close pair.

## Credit rules

Both plans renew monthly, and Recraft's plan credits do not carry over (check ElevenLabs' rollover on its plan page before saving credits). Compare prices in dollars, never in credits: ElevenLabs Starter is $0.0002 a credit ($6 for 30,000), Recraft Basic $0.012 ($12 for 1,000).

| Plan | Measured best at |
|---|---|
| ElevenLabs | finished poses, expressions and turnaround panels; pose sheets; small fixes |
| Recraft | icons that crop the hero; SVG vectors; a persistent custom style; `crisp_upscale`; 1-credit layout thumbnails |

1. **Route by the table at the top.** When two routes tie, spend from the plan with more credits left for the days until it renews.
2. **Draft once, finish once.** One pose sheet per direction; only the owner's pick is drawn on the final model, one image a call.
3. **Lock ElevenLabs' settings on every call**: `generations_count` 1, medium quality, 1K, the target's ratio. High quality or 2K only for print, quoted first. The defaults (4 variations, 16:9, Sunburst at high) cost several times as much.
4. **Quote before spending**: `estimate_only` on ElevenLabs, the rates here for Recraft. A batch follows the owner's-yes rule in `generate.md`.
5. **When one plan runs dry, switch by the fallback table below.** GPT Image 2 and 2.5 Sunburst run on both, so most jobs keep their model. Tell the owner which plan ran out and what moved.
6. **Read both balances** at step 1 and after each round: `account_get_usage` on ElevenLabs, `get_user` on Recraft.
7. **In Recraft's last week before renewal**, spend what is left on the jobs only it does (vectors, a custom style, icons, upscales) or on draft sheets.
8. **At each renewal, total the month by vendor** from `log.jsonl`, and move a job's route when the other plan did it better or cheaper that month.

**When a plan runs out of credits.** An untested fallback gets one image and `check.py` before a batch.

| Job | Recraft empty: use ElevenLabs | ElevenLabs empty: use Recraft |
|---|---|---|
| Layout thumbnails | `recraft-v4.1-flash` (untested there) | stays on Recraft |
| Pose sheets | stays on ElevenLabs | `image_edit` `gpt_image_2_low`, 2:1, naming the head detail "in every pose" |
| Finished pose, expression or turnaround panel | stays on ElevenLabs | `image_edit` `gpt_image_2_medium` |
| Small fix | stays on ElevenLabs | `image_edit` `gpt_image_2p5_sunburst`, then `crisp_upscale` |
| Icon that crops the hero | `gpt-image-2.6-sunburst`, asking for the prop at twice the size | stays on Recraft |
| SVG vector | `recraft-v4.1-pro-vector` (untested there) | stays on Recraft |
| Style-locked set | no style object: the hero as reference plus `identity_text`, on `gpt-image-2.6-sunburst` | stays on Recraft |
| Upscale for print | `topaz-image-upscale-v2` (untested: diff it, it may redraw) | stays on Recraft |
| Background removal | `birefnet-v2-bg-removal` (untested) | `remove_background` |

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
| GPT Image 2.6 Sunburst (Studio, medium, 1K) | 6 | | lost the blind pair to 2.5 Sunburst: roped off the critic instead of the painting, copied the world frame's flag | correct, 3.5% changed outside the edit, but dropped "pinning a card" | as good at fixes for 4 fewer credits; not in the MCP |
| GPT Image 2.6 Sunburst markup (Studio) | 6 | | | the most surgical (0.6% inside, 2.3% outside), but kept the old board and drew a second one | the point-and-describe edit; Studio only |
| GPT Image 2.6 Flare (Studio, low, 1K) | 4 | | | | one clean on-model pose per image; `gpt_image_2_low` gives a sheet of poses for half the credits |

The contact sheets are `art/cast/rounds/round8-model-comparison.jpg` and `art/cast/rounds/round8-studio-2.6.jpg` in this repo. The 2.6 rows ran in Recraft Studio, driven through the yab browser, on the same credit balance as the MCP: 2.6 did not beat 2.5 Sunburst on the scene, so the routing stays on the MCP's 2.5 Sunburst. Studio is worth opening for a fix where markup's precision matters more than the rest of the brief, or to save 4 credits a fix.

## Measured: the Detalo pig, ElevenLabs against Recraft

Six one-change prompts from the pig's hero (identity text, the change, rendering, hex colours, composition), ElevenLabs `creative_edit_image` at 1:1, 1K, medium, one image a call, 2026-11-24. The Recraft side of each pair is the `gpt_image_2_medium` image already made for the pack, so it ran once, not alongside. `check.py`, then `art-critique` in a fresh subagent on blind labels, every pair in both orders.

| Change | Winner | Runner-up | Notes |
|---|---|---|---|
| Side view | 2.6 Sunburst | 2.5 Sunburst; Recraft last (no head tape, taller than wide) | Recraft's panel was cut at 600 px from one four-view sheet |
| Three-quarter | 2.6 Sunburst | Recraft: taller than wide, cheeks barely past the body | 2.6 added glossy blush highlights |
| Hungry | 2.5 Sunburst | 2.6 Sunburst (kept the hero's smile); Recraft last (reads as a yawn) | 2.5 drew the growl marks on the body, where they read as cracks |
| Munching | 2.6 Sunburst | Recraft: an upright bean, the receipt coming out under the snout | |
| Proud | 2.6 Sunburst | Recraft: identity lost, the critic would regenerate it | 2.6's trotters only reached shoulder height |
| Icon peek | Recraft | 2.6 Sunburst: the receipt stub a speck at 60 px | |

Cost per image: 2.6 Sunburst 356 ElevenLabs credits, 2.5 Sunburst 341, `gpt-image-2` 562, Nano Banana Pro (`gemini-3-pro-image`) 1,827 (not run); Recraft `gpt_image_2_medium` 9. At plan rates (ElevenLabs Starter $6 for 30,000, Recraft Basic $12 for 1,000) that is $0.071, $0.068, $0.112, $0.365 and $0.108. Low quality is not half price: 2.6 Sunburst low was 242 credits and `gpt-image-2` low 267. The whole comparison cost 2,818 ElevenLabs credits. Two follow-ups the same day (606 credits) set the pose-sheet and small-fix rows: an eight-pose sheet on `gpt-image-2` low, and moving the hungry pig's growl marks with 2.6 Sunburst. The images and blind key are in the scratch project's `art/detalo/bakeoff-elevenlabs/`, outside this repo.

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

## ElevenLabs

**Setup.** The hosted MCP server is `https://api.elevenlabs.io/v1/mcp-creative` (HTTP, OAuth), in `profile/mcp.json` as `elevenlabs`. Sign in once per profile with `/mcp`. Use this URL, not the Claude directory connector, which leaves out image generation. It worked on the Starter plan; `account_get_usage` gives the plan and credits used.

**The loop, mapped.** One flow (`creative_create_flow`) per character holds every call. Put the hero on it once: `creative_create_asset_upload` with the exact byte size, PUT the bytes with curl, then `creative_finalize_asset_upload` with the `flow_id` returns the hero's `node_id`. Each edit is `creative_edit_image` with that `node_id` in `connect_from`. Calls return before the image exists: poll `creative_get_flow_run_status` (about a minute per image), then download the `content_url` into `raw/` and log the `flow_id` and generation id.

**Settings to override on every call.** The tools default to 4 variations, 16:9 and, on the Sunburst models, high quality. To set ratio and quality, create the node with `estimate_only: true` (which places it without generating), set `aspect_ratio`, `resolution` and `quality` with `creative_update_node` (read `creative_get_model_schema` first), quote with `creative_run_flow_nodes` and `estimate_only: true`, then run it with `generations_count: 1`. Never repeat a run to retry: each starts and charges a new one.

**Seen in the pig comparison** (2026-11-24, Starter plan):

- Prices are in the table above. A reference image raises the price: the same text-only `gpt-image-2` call was 185 credits.
- `content_url` links are signed and expire within hours; download at once.
- There is no persistent style object like Recraft's custom style. A brand kit holds palette, rules and images, but the generation tools take no brand-kit argument, so identity still rests on the hero reference and `identity_text`.
- It also runs `recraft-v4.1`, `recraft-v4.1-pro-vector`, `bytedance-seedream-5.5` (transparent backgrounds), `birefnet-v2-bg-removal` and `topaz-image-upscale-v2`, all untested here.

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

- **GPT Image 2.6 (Flare and Sunburst).** OpenAI released both on 2026-11-04: Flare for fast drafts, Sunburst for final images and edits that leave the unasked parts alone ([Recraft's test](https://www.recraft.ai/blog/gpt-image-2-6)). On 2026-11-07 Recraft Studio had 2.6, while the MCP listed only the 2.5 pair; both are measured above. Read `image_edit`'s `model` list for a 2.6 id before relying on Studio for it. Studio credits per image, the same for both: low 4 (1K) or 7 (2K), medium 6 or 12, high 10 or 14. Preliminary Arena ranks Sunburst 2nd for text to image and 3rd for single-image edits ([Kingy](https://kingy.ai/blog/gpt-image-2-6-sunburst-flare/)). Recraft's own illustration test preferred Recraft V4.1 Pro's flat graphic look to Sunburst's painterly storybook look, and markup editing (circle a region to change) is API-only. The ElevenLabs MCP runs both 2.6 models; Sunburst is measured there (the pig comparison above), Flare is not.
- **Untested here**: `gpt_image_2_high`, Recraft V4.1 Utility and Utility Pro (Studio only), FLUX 3 (Studio only).
- **Draft low, upscale the pick.** A cheap model at 480p plus an upscale of the chosen image cost about a quarter of generating every draft at full size ([video at 13:16](https://www.youtube.com/watch?v=Rk6t9Uq1y9M&t=796s)).
- **Nano Banana Pro through Google's API** at about $0.134 per image is cheaper than a $59 monthly plan below roughly 440 images a month ([video](https://www.youtube.com/watch?v=Zk4Qzd-NJ_0)).
- **QuiverAI** generates illustration as native SVG (seen in [@DannPetty's post](https://x.com/DannPetty/status/2117708396153479626), 2026-11-04, where the SVG was then animated in Claude). If its paths hold the pack's identity, it competes with the Recraft vector model for flat art that `motion-direction` will animate, since the parts arrive as paths instead of through `vectorize_image`.

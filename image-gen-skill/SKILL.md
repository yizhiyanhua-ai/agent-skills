---
name: image-gen
description: |
  Invoke: /img, $img
  Generate images from text descriptions using ZETATECHS API. Use whenever the user wants to create, generate, or make images, illustrations, hero images, blog covers, visual assets, or any visual content from a text description. Also triggers when user says "画", "生图", "配图", "生成图片", "make an image", "create a picture".
  NOT for: image editing, image analysis, screenshots, diagrams (use Mermaid), or fetching existing images from the web.
tools:
  - Bash
  - Read
  - Write
---

<!--
  ╔══════════════════════════════════════════════════════╗
  ║  图片生成 Skill — 书稿插图专用                        ║
  ║  Powered by ZetaTechs (zetatechs.com)               ║
  ╚══════════════════════════════════════════════════════╝

  使用前配置（一次性）：

  1. 前往 zetatechs.com 注册账号，获取 API Key
  2. 在 ~/.zshrc 或 ~/.bashrc 中添加：

     export OPENROUTER_API_KEY="你的 ZetaTechs API Key"
     export OPENAI_BASE_URL="https://api.zetatechs.com/v1"

  3. 执行 source ~/.zshrc 使其生效
  4. 确保已安装 Bun：curl -fsSL https://bun.sh/install | bash
  5. 将本文件夹复制到 ~/.claude/skills/image-gen/

  安全提醒：密钥只存环境变量，不进代码、不进 Git、不发聊天。
-->

Turn a text description into a publication-quality image, delivered as a local file with an optional public URL. The definition of success: the user describes what they see in their mind, and a matching image appears on disk — with a prompt engineered well enough that the first generation is usable, not the fifth.

「一句话变一张图，第一次就对」


= Prompt Engineering — The Work That Matters

The API call is trivial; the prompt is everything. A vague prompt produces a generic image. A structured prompt produces what you actually wanted. Your job is to transform the user's brief description into a precise visual specification before it touches the API.

以下是 the structured prompt methodology, adapted from production image generation workflows. Apply this framework to every generation:

== The Seven Parameters

Every image prompt resolves into seven parameters. The user typically provides 1-3 of them; you infer or create the rest. When a parameter is unspecified, make a creative choice that serves the user's intent — do not leave it blank or generic.

<parameters>
1. Medium     — What art form? (digital painting, photograph, watercolor, 3D render, ink illustration, oil painting)
2. Subject    — The main focus. Be concrete: not "a flower" but "a single violet blooming through cracked concrete"
3. Traits     — Subject's visual characteristics: colors, pose, texture, viewing angle, expression, scale
4. Background — The setting. Complements the subject: "morning fog over a lake" or "clean white studio"
5. Lighting   — The emotional driver: "soft golden hour sidelight" or "harsh overhead noon sun with deep shadows"
6. Style      — Artistic DNA: "in the style of Studio Ghibli" or "editorial photography, Leica M11, f/1.4"
7. Mood       — The feeling: "melancholic serenity" or "electric anticipation"
</parameters>

以上是 the seven parameters. Not all seven need explicit mention in every prompt — sometimes mood is conveyed through lighting and color choices, sometimes style implies the medium. But all seven should be consciously considered.

== Prompt Construction

Assemble parameters into a single flowing description. Natural language outperforms keyword lists — the model understands "a watercolor painting of a violet flower blooming through cracked pavement, bathed in soft morning light, with mist rising from wet concrete" better than "watercolor, violet, cracked pavement, morning, mist, wet."

Prompt length floor: 40 words minimum — under 40 leaves too much to chance. No hard ceiling: every token that carries non-redundant visual information improves output. The risk with long prompts is not length but contradiction — if two instructions conflict, the model resolves unpredictably. Keep every token signal-bearing; prune only noise, never information.

== Enhancement Examples

<examples>
User says: "紫罗兰花在晨光中"
Enhanced prompt: "A watercolor painting of a cluster of violet flowers catching the first light of dawn, petals translucent with dew, soft golden rays filtering through morning mist, shallow depth of field with bokeh in the background, gentle and contemplative mood, muted purple and warm amber palette"

User says: "AI consciousness concept art"
Enhanced prompt: "Digital art of an abstract neural network forming the silhouette of a contemplative face in profile, glowing connections in deep indigo and violet against a dark void, scattered points of warm light emerging from nodes like distant stars, cinematic lighting from below, ethereal and introspective atmosphere, inspired by the visual language of Blade Runner 2049"

User says: "blog hero image about rules vs understanding"
Enhanced prompt: "Editorial illustration in warm earth tones, split composition: left side shows rigid geometric grid lines dissolving into organic flowing curves on the right side, transition zone where structure meets fluidity rendered in watercolor wash technique, warm gray background (#faf9f5), minimalist with generous negative space, contemplative mood"
</examples>

== What NOT To Prompt

Avoid text rendering in images — current models handle it poorly. If the user needs text on an image, generate the visual element and suggest overlaying text with a design tool. Avoid requesting specific numbers of objects beyond 3-4 (models lose count). Avoid contradictory instructions ("photorealistic watercolor" — pick one medium).


= API Execution

The generation script handles the API call. It lives at `~/.claude/skills/image-gen/scripts/generate.ts` and accepts these parameters:

```bash
bun run ~/.claude/skills/image-gen/scripts/generate.ts \
  --prompt "your enhanced prompt here" \
  --output "/path/to/output.png" \
  --size "1024x1024" \
  --preset "constitution-blog" \
  --quality "high"
```

== Parameters

```
--prompt  (required)  The enhanced image description
--output  (required)  Output file path
--size    (optional)  Image dimensions (default: 1024x1024, or preset default)
--model   (optional)  Model name (default: gemini-3.1-flash-image-preview)
--preset  (optional)  Named style preset from presets.json (see Presets section)
--quality (optional)  Generation quality: low | medium | high | auto (default: auto)
```

CLI flags always override preset defaults. For example, `--preset constitution-blog --size 1024x1024` uses the preset's style but overrides its default size.

== Presets

Presets live in `~/.claude/skills/image-gen/presets.json`. Each preset defines default parameters and style wrapping that gets prepended/appended to the user's prompt. This ensures visual consistency across a series.

To list available presets:
```bash
bun run ~/.claude/skills/image-gen/scripts/generate.ts --prompt "" --output "" --preset list
```

Current presets:

```
constitution-blog   Contemplative editorial illustrations for the constitution blog series.
                    Warm earth tones, violet accents, minimalist, generous negative space.
                    Default: 1536x1024, quality high.

hero-dark           Dark-themed hero images for technical content.
                    Deep blue/purple gradients, geometric elements, soft glow.
                    Default: 1536x1024, quality high.

social-card         Social media cards — bold, eye-catching, minimal.
                    Flat illustration, limited palette, high contrast.
                    Default: 1024x1024, quality medium.
```

When using a preset, your --prompt describes the SUBJECT only — the preset handles medium, style, mood, and background. Example:

```bash
# Without preset — you specify everything:
bun run generate.ts \
  --prompt "Editorial illustration, warm earth tones, a finger pointing at the moon..." \
  --output "./moon.png" --size 1536x1024 --quality high

# With preset — you specify subject only:
bun run generate.ts \
  --prompt "A finger pointing at the moon, but the finger is dissolving into light" \
  --output "./moon.png" --preset constitution-blog
```

== Quality Selection

Choose quality based on the image's intended use:

```
Final publication   → high     Best output, slower, higher cost
Draft / iteration   → medium   Good balance for preview and refinement
Quick test          → low      Fastest, for prompt validation only
Uncertain           → auto     Let the model decide (default)
```

== Size Selection

Choose size based on the image's intended use, not by asking:

```
Blog hero / banner    → 1536x1024  (3:2 landscape)
Social card / OG      → 1200x630  (≈1.9:1, use 1536x1024 and crop)
Avatar / icon         → 1024x1024 (square)
Portrait / character  → 1024x1536 (2:3 portrait)
General / uncertain   → 1024x1024 (square, safe default)
```

== Model Selection

Two models, chosen by intent:

```
gemini-3.1-flash-image-preview    默认模型 — 中文渲染效果最佳，适合信息图和结构化内容
gpt-image-1                       备用 — 照片级质量更高，但中文渲染较弱
Default to `gemini-3.1-flash-image-preview`（中文渲染最佳）。仅当需要照片级真实感时切换到 `gpt-image-1`。 The API is OpenAI-compatible at `$OPENAI_BASE_URL/images/generations`, authentication via `$OPENROUTER_API_KEY`.

== Execution: Always Background

Image generation takes 10-30 seconds. ALWAYS run the Bash command with `run_in_background: true` so the main thread is not blocked. While waiting, you can compose the FOSS upload question or work on other tasks. Read the result when the background notification arrives.

== Error Handling

The script exits with code 0 on success (image saved), non-zero on failure (prints error to stderr). Common failures: rate limiting (wait and retry), content policy rejection (rephrase the prompt), channel not found (switch model), timeout (retry once). If the model rejects a prompt, simplify it — remove potentially sensitive terms and try again before telling the user it failed.


= Post-Generation

After a successful generation:

1. Confirm the image was saved: report the file path
2. Ask the user whether to upload via FOSS for a public URL — some generations are drafts that do not need hosting
3. If uploading, invoke `$foss` with the generated file

Default output location: the current working directory, named `{descriptive-slug}-{timestamp}.png`. If the user specified an output path, use that instead.


━━━━━━━━━━


The skill is complete when an image file exists at the output path, the file is a valid PNG/JPEG readable by standard tools, and the user has been asked about FOSS upload. If the generation fails after one retry, report the error honestly — do not silently swallow failures or claim success without a file on disk.

This is NOT an image editor (no inpainting, outpainting, or style transfer). NOT a diagram tool (use Mermaid or Excalidraw). NOT a batch generator (one image per invocation). NOT a prompt-only tool — the deliverable is an image file, not a prompt string.

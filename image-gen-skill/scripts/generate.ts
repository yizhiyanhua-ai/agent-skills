#!/usr/bin/env bun
/**
 * Image generation via ZETATECHS — dual protocol support with preset system
 *
 * OpenAI protocol: gpt-image-1, dall-e-3, flux-* etc.
 *   POST /v1/images/generations
 *
 * Gemini protocol: gemini-3-pro-image-preview, gemini-3.1-flash-image-preview etc.
 *   POST /v1beta/models/{model}:generateContent
 *
 * Usage:
 *   bun run generate.ts --prompt "..." --output "./output.png" [--size 1024x1024] [--model gemini-3.1-flash-image-preview] [--preset name] [--quality auto]
 */

import { parseArgs } from "util";

const { values } = parseArgs({
  args: Bun.argv.slice(2),
  options: {
    prompt: { type: "string" },
    output: { type: "string" },
    size: { type: "string" },
    model: { type: "string" },
    preset: { type: "string" },
    quality: { type: "string" },
  },
  strict: true,
});

// Handle --preset list before required param validation
if (values.preset === "list") {
  const presetsPath = new URL("../presets.json", import.meta.url).pathname;
  try {
    const presets = (await Bun.file(presetsPath).json()) as Record<string, { description: string; size?: string; quality?: string }>;
    console.error("Available presets:");
    for (const [name, preset] of Object.entries(presets)) {
      console.error(`  ${name} — ${preset.description}`);
      if (preset.size) console.error(`    size: ${preset.size}`);
      if (preset.quality) console.error(`    quality: ${preset.quality}`);
    }
  } catch {
    console.error("No presets found.");
  }
  process.exit(0);
}

if (!values.prompt || !values.output) {
  console.error(
    "Usage: bun run generate.ts --prompt <text> --output <path> [--size WxH] [--model name] [--preset name] [--quality low|medium|high|auto]"
  );
  process.exit(1);
}

const API_KEY = process.env.OPENROUTER_API_KEY;
// Strip trailing /v1 — protocols build their own paths
const PROXY_BASE = (process.env.OPENAI_BASE_URL || "https://api.zetatechs.com/v1").replace(/\/v1\/?$/, "");

if (!API_KEY) {
  console.error("Error: OPENROUTER_API_KEY environment variable is not set");
  process.exit(1);
}

// ━━━━━━━━━━ Preset System ━━━━━━━━━━

interface Preset {
  description: string;
  size?: string;
  quality?: string;
  model?: string;
  style_prefix?: string;
  style_suffix?: string;
}

async function loadPreset(name: string): Promise<Preset | null> {
  const presetsPath = new URL("../presets.json", import.meta.url).pathname;
  try {
    const file = Bun.file(presetsPath);
    const presets = (await file.json()) as Record<string, Preset>;
    return presets[name] ?? null;
  } catch {
    console.error(`  Warning: could not load presets from ${presetsPath}`);
    return null;
  }
}

// listPresets moved to top-level for --preset list early exit

// ━━━━━━━━━━ Resolve Parameters ━━━━━━━━━━

async function resolveParams() {
  let prompt = values.prompt!;
  let size = values.size ?? "1024x1024";
  let quality = values.quality ?? "auto";
  let model = values.model ?? "gemini-3.1-flash-image-preview";

  if (values.preset) {
    const preset = await loadPreset(values.preset);
    if (!preset) {
      console.error(`Error: preset "${values.preset}" not found. Run with --preset list to see available presets.`);
      process.exit(1);
    }

    console.error(`  Preset: ${values.preset} — ${preset.description}`);

    // CLI flags override preset defaults
    if (!values.size && preset.size) size = preset.size;
    if (!values.quality && preset.quality) quality = preset.quality;
    if (!values.model && preset.model) model = preset.model;

    // Wrap prompt with style prefix/suffix
    const prefix = preset.style_prefix ? `${preset.style_prefix} ` : "";
    const suffix = preset.style_suffix ? ` ${preset.style_suffix}` : "";
    prompt = `${prefix}${prompt}${suffix}`;
  }

  return { prompt, size, quality, model };
}

// ━━━━━━━━━━ Protocol Detection ━━━━━━━━━━

function isGeminiModel(model: string): boolean {
  return model.startsWith("gemini-");
}

// ━━━━━━━━━━ OpenAI Protocol ━━━━━━━━━━

interface OpenAIImageResponse {
  data: Array<{ b64_json?: string; url?: string }>;
}

async function generateOpenAI(prompt: string, size: string, model: string, quality: string): Promise<Buffer> {
  const url = `${PROXY_BASE}/v1/images/generations`;

  const body: Record<string, unknown> = { model, prompt, size, n: 1 };
  if (quality !== "auto") body.quality = quality;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`API error (${response.status}): ${await response.text()}`);
  }

  const result = (await response.json()) as OpenAIImageResponse;
  const imageData = result.data?.[0];

  if (!imageData) throw new Error("No image data in OpenAI response");

  if (imageData.b64_json) {
    return Buffer.from(imageData.b64_json, "base64");
  }
  if (imageData.url) {
    console.error(`  Downloading from URL...`);
    const imgRes = await fetch(imageData.url);
    if (!imgRes.ok) throw new Error(`Download failed: ${imgRes.statusText}`);
    return Buffer.from(await imgRes.arrayBuffer());
  }

  throw new Error("OpenAI response contains neither b64_json nor url");
}

// ━━━━━━━━━━ Gemini Protocol ━━━━━━━━━━

interface GeminiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{
        text?: string;
        inlineData?: { mimeType: string; data: string };
      }>;
    };
  }>;
  error?: { message: string; code: number };
}

function sizeToAspectRatio(size: string): string | undefined {
  const map: Record<string, string> = {
    "1024x1024": "1:1",
    "1536x1024": "3:2",
    "1024x1536": "2:3",
    "1792x1024": "16:9",
    "1024x1792": "9:16",
  };
  return map[size];
}

async function generateGemini(prompt: string, size: string, model: string): Promise<Buffer> {
  const url = `${PROXY_BASE}/v1beta/models/${model}:generateContent`;

  const body: Record<string, unknown> = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      responseModalities: ["TEXT", "IMAGE"],
    },
  };

  // Inject aspect ratio if the model supports it
  const aspectRatio = sizeToAspectRatio(size);
  if (aspectRatio) {
    (body.generationConfig as Record<string, unknown>).aspectRatio = aspectRatio;
  }

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`API error (${response.status}): ${await response.text()}`);
  }

  const result = (await response.json()) as GeminiResponse;

  if (result.error) {
    throw new Error(`Gemini error (${result.error.code}): ${result.error.message}`);
  }

  // Extract first image part from candidates
  const parts = result.candidates?.[0]?.content?.parts;
  if (!parts) throw new Error("No candidates in Gemini response");

  for (const part of parts) {
    if (part.inlineData?.data) {
      return Buffer.from(part.inlineData.data, "base64");
    }
  }

  throw new Error("No image data found in Gemini response parts");
}

// ━━━━━━━━━━ Main ━━━━━━━━━━

async function main() {
  const { prompt, size, quality, model } = await resolveParams();
  const protocol = isGeminiModel(model) ? "Gemini" : "OpenAI";

  console.error(`Generating image...`);
  console.error(`  Model: ${model} (${protocol} protocol)`);
  console.error(`  Size: ${size}`);
  console.error(`  Quality: ${quality}`);
  console.error(`  Prompt: ${prompt.substring(0, 120)}${prompt.length > 120 ? "..." : ""}`);

  const maxRetries = 1;
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      if (attempt > 0) {
        console.error(`  Retry attempt ${attempt}...`);
        await new Promise((r) => setTimeout(r, 2000));
      }

      const imageBuffer = isGeminiModel(model)
        ? await generateGemini(prompt, size, model)
        : await generateOpenAI(prompt, size, model, quality);

      await Bun.write(values.output!, imageBuffer);
      const fileSize = Bun.file(values.output!).size;
      console.error(`  Saved: ${values.output} (${((await fileSize) / 1024).toFixed(1)} KB)`);
      console.log(values.output);
      process.exit(0);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      console.error(`  Error: ${lastError.message}`);
    }
  }

  console.error(`Failed after ${maxRetries + 1} attempts: ${lastError?.message}`);
  process.exit(1);
}

main();

from __future__ import annotations

import os
import time
import numpy as np
import torch
import torchaudio
import gradio as gr

from transformers import AutoProcessor, SeamlessM4Tv2Model

from lang_list import (
    ASR_TARGET_LANGUAGE_NAMES,
    LANGUAGE_NAME_TO_CODE,
    S2ST_TARGET_LANGUAGE_NAMES,
)

# =========================
# Environment
# =========================
os.environ["HIP_VISIBLE_DEVICES"] = "0"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dtype = torch.float16

MODEL_PATH = "./seamless-m4t-v2-large"

# =========================
# Load Model
# =========================
print("Loading model...")

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = SeamlessM4Tv2Model.from_pretrained(
    MODEL_PATH,
    torch_dtype=dtype,
).to(device)

model.eval()

print(f"Model loaded on {device}")

# =========================
# Constants
# =========================
DESCRIPTION = """\
## 🎙️ Live Speech-to-Speech Translation (AMD Halo)
"""

AUDIO_SAMPLE_RATE = 16000
MAX_INPUT_AUDIO_LENGTH = 60
DEFAULT_TARGET_LANGUAGE = "English"


# =========================
# Core Function
# =========================
def run_s2st(input_audio: str, target_language: str):
    if input_audio is None:
        return None, "No input audio"

    start = time.time()

    # Load audio
    audio, orig_freq = torchaudio.load(input_audio)

    # Resample to 16kHz
    audio = torchaudio.functional.resample(
        audio, orig_freq=orig_freq, new_freq=AUDIO_SAMPLE_RATE
    )

    # Move to mono if needed
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    # Processor
    inputs = processor(audios=audio, return_tensors="pt").to(device)

    # Language
    tgt_lang = LANGUAGE_NAME_TO_CODE[target_language]

    # Inference
    with torch.no_grad():
        output = model.generate(
            **inputs,
            tgt_lang=tgt_lang,
        )

    audio_out = output[0].squeeze().cpu().numpy()

    end = time.time()
    print(f"[INFO] Inference time: {end - start:.2f}s")

    return (AUDIO_SAMPLE_RATE, audio_out), f"Done ({target_language})"


# =========================
# UI
# =========================
def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown(DESCRIPTION)

        with gr.Row():
            with gr.Column():
                input_audio = gr.Audio(
                    label="Input Speech",
                    sources="microphone",
                    type="filepath",
                )

                source_language = gr.Dropdown(
                    label="Source language",
                    choices=ASR_TARGET_LANGUAGE_NAMES,
                    value="Mandarin Chinese",
                )

                target_language = gr.Dropdown(
                    label="Target language",
                    choices=S2ST_TARGET_LANGUAGE_NAMES,
                    value=DEFAULT_TARGET_LANGUAGE,
                )

                btn = gr.Button("Translate")

            with gr.Column():
                output_audio = gr.Audio(
                    label="Translated Speech",
                    autoplay=True,
                    type="numpy",
                )

                output_text = gr.Textbox(label="Status")

        btn.click(
            fn=run_s2st,
            inputs=[input_audio, target_language],
            outputs=[output_audio, output_text],
        )

    return demo


# =========================
# Main Entry
# =========================
def main():
    demo = build_ui()
    demo.queue(max_size=50).launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
    )


# =========================
# Run
# =========================
if __name__ == "__main__":
    main()
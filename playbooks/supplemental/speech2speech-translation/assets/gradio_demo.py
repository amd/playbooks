from __future__ import annotations

import argparse
import os
import time
from typing import Tuple

import gradio as gr
import numpy as np
import soundfile as sf
import torch
import torchaudio
from transformers import AutoProcessor, SeamlessM4Tv2Model

from lang_list import S2ST_TARGET_LANGUAGE_NAMES, LANGUAGE_NAME_TO_CODE

# =========================
# Environment
# =========================
AUDIO_SAMPLE_RATE = 16000
DEFAULT_TARGET_LANGUAGE = "English"
DEFAULT_SERVER_NAME = "127.0.0.1"
DEFAULT_SERVER_PORT = 7860
DEFAULT_MODEL_PATH = os.environ.get("S2S_MODEL_PATH", "./seamless-m4t-v2-large")
DEFAULT_DEVICE_ID = os.environ.get("S2S_DEVICE_ID", "0")

DESCRIPTION = """\
## 🎙️ Live Speech-to-Speech Translation (AMD Halo)

This demo follows the standard SeamlessM4T-v2 speech path: **audio input -> translated speech output**.
Choose the **Target language**, record audio, and click **Translate**.
"""

# =========================
# CLI Args
# =========================
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Speech-to-speech translation demo")
    parser.add_argument("--share", dest="share", action="store_true", help="Create a public Gradio share link")
    parser.add_argument("--no-share", dest="share", action="store_false", help="Run locally only")
    parser.set_defaults(share=False)
    parser.add_argument("--server-name", default=DEFAULT_SERVER_NAME, help="Server bind address")
    parser.add_argument("--server-port", type=int, default=DEFAULT_SERVER_PORT, help="Server port")
    parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH, help="Local path to seamless-m4t-v2-large")
    parser.add_argument("--device-id", default=DEFAULT_DEVICE_ID, help="Value to set for HIP_VISIBLE_DEVICES",)
    return parser.parse_args()

# =========================
# Load Model
# =========================
def build_runtime(model_path: str, device_id: str):
    os.environ["HIP_VISIBLE_DEVICES"] = str(device_id)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.float16 if device.type == "cuda" else torch.float32

    print("Loading model...")
    processor = AutoProcessor.from_pretrained(model_path)
    model = SeamlessM4Tv2Model.from_pretrained(model_path, dtype=dtype).to(device)
    model.eval()
    print(f"Model loaded on {device}")
    return processor, model, device

def load_audio(audio_path: str, target_sr: int = AUDIO_SAMPLE_RATE) -> torch.Tensor:
    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)
    audio = torch.from_numpy(audio_np.T)

    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)

    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)

    return audio

# =========================
# Core Function
# =========================
def make_runner(processor, model, device):
    def run_s2st(input_audio: str, target_language: str):
        if input_audio is None:
            return None, "No input audio"

        start = time.time()

        # Load audio
        audio = load_audio(input_audio)
        inputs = processor(
            audio=audio.squeeze(0).cpu().numpy(),
            sampling_rate=AUDIO_SAMPLE_RATE,
            return_tensors="pt",
        ).to(device)

        # Inference
        with torch.no_grad():
            output = model.generate(**inputs, tgt_lang=target_language_code(target_language))

        audio_out = output[0].squeeze().cpu().numpy()
        elapsed = time.time() - start
        return (model.config.sampling_rate, audio_out), f"Translated to {target_language} in {elapsed:.2f}s"

    return run_s2st

def target_language_code(language_name: str) -> str:
    return LANGUAGE_NAME_TO_CODE[language_name]

# =========================
# UI
# =========================
def build_ui(runner):
    with gr.Blocks() as demo:
        gr.Markdown(DESCRIPTION)

        with gr.Row():
            with gr.Column():
                input_audio = gr.Audio(
                    label="Input Speech",
                    sources="microphone",
                    type="filepath",
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
            fn=runner,
            inputs=[input_audio, target_language],
            outputs=[output_audio, output_text],
        )

    return demo

# =========================
# Main Entry
# =========================
def main() -> None:
    args = parse_args()
    processor, model, device = build_runtime(args.model_path, args.device_id)
    runner = make_runner(processor, model, device)
    demo = build_ui(runner)
    demo.queue(max_size=50).launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=args.share,
    )

# =========================
# Run
# =========================
if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeamlessM4T v2 Audio-to-Text Inference Script
AMD GPU Support via HIP_VISIBLE_DEVICES
"""

from __future__ import annotations
import os
import time
import numpy as np
import scipy.io.wavfile
import soundfile as sf
import torch
import torchaudio
from transformers import AutoProcessor, SeamlessM4Tv2Model


# ============ Configuration ============
DEFAULT_TARGET_LANGUAGE = "eng"
INPUT_AUDIO_PATH = "./input1.wav"
OUTPUT_AUDIO_PATH = "./out1.wav"
MODEL_PATH = os.environ.get("S2S_MODEL_PATH", "./seamless-m4t-v2-large")
TARGET_SAMPLE_RATE = 16_000
# =======================================


def setup_device() -> torch.device:
    """Configure and return the computation device."""
    # For AMD GPU: set HIP_VISIBLE_DEVICES before torch import
    os.environ["HIP_VISIBLE_DEVICES"] = "0"
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    return device


def load_model(model_path: str, device: torch.device) -> tuple:
    """Load processor and model, return both with loading time."""
    start = time.time()
    processor = AutoProcessor.from_pretrained(model_path)
    dtype = torch.float16 if device.type == "cuda" else torch.float32
    model = SeamlessM4Tv2Model.from_pretrained(model_path, dtype=dtype).to(device)
    elapsed = time.time() - start
    print(f"Model loading duration: {elapsed:.2f} seconds")
    return processor, model


def preprocess_audio(audio_path: str, target_sr: int = TARGET_SAMPLE_RATE) -> torch.Tensor:
    """Load and resample audio to target sample rate."""
    audio_np, orig_freq = sf.read(audio_path, dtype="float32", always_2d=True)
    audio = torch.from_numpy(audio_np.T)
    if orig_freq != target_sr:
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    return audio


def run_inference(
    model,
    processor,
    audio: torch.Tensor,
    device: torch.device,
    target_lang: str = DEFAULT_TARGET_LANGUAGE):
    """Run model inference and return output audio array + duration."""
    start = time.time()

    # Process audio inputs and move to device
    audio_inputs = processor(
        audio=audio.squeeze(0).cpu().numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )
    audio_inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in audio_inputs.items()}
    
    # Generate output
    with torch.inference_mode():
        output = model.generate(**audio_inputs, tgt_lang=target_lang)[0]
    
    # Move result back to CPU for saving
    audio_array = output.float().cpu().numpy().squeeze()
    elapsed = time.time() - start
    print(f"Inference duration: {elapsed:.2f} seconds")

    return audio_array, elapsed


def save_audio(audio_array: torch.Tensor, output_path: str, sample_rate: int):
    """Save audio array to WAV file."""
    if np.issubdtype(audio_array.dtype, np.floating):
        max_abs = np.max(np.abs(audio_array)) if audio_array.size else 0.0
        if max_abs > 1.0:
            audio_array = audio_array / max_abs
        audio_array = (audio_array * 32767.0).clip(-32768, 32767).astype(np.int16)
    scipy.io.wavfile.write(output_path, rate=sample_rate, data=audio_array)
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    # 1. Setup device
    device = setup_device()
    
    # 2. Load model and processor
    processor, model = load_model(MODEL_PATH, device)
    
    # 3. Preprocess input audio
    audio = preprocess_audio(INPUT_AUDIO_PATH)
    
    # 4. Run inference
    audio_output, infer_time = run_inference(model, processor, audio, device)
    
    # 5. Save output
    save_audio(audio_output, OUTPUT_AUDIO_PATH, model.config.sampling_rate)
    
    print(f"✅ Complete! Total inference time: {infer_time:.2f}s")
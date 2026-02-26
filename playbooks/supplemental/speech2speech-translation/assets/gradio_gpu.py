from __future__ import annotations

import os
import pathlib

import gradio as gr
import numpy as np
import torch
import torchaudio
import time
import scipy
from transformers import AutoProcessor, SeamlessM4Tv2Model

from lang_list import (
    ASR_TARGET_LANGUAGE_NAMES,
    LANGUAGE_NAME_TO_CODE,
    S2ST_TARGET_LANGUAGE_NAMES,
)
os.environ["HIP_VISIBLE_DEVICES"] = "0"
processor = AutoProcessor.from_pretrained("./seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("./seamless-m4t-v2-large").to("cuda")

DESCRIPTION = """\
## Live Speech-to-speech Translation Powered by AMD Halo Platform

"""

AUDIO_SAMPLE_RATE = 16000.0
MAX_INPUT_AUDIO_LENGTH = 60  # in seconds
DEFAULT_TARGET_LANGUAGE = "English"

if torch.cuda.is_available():
    device = torch.device("cuda")
    dtype = torch.float16


AUDIO_SAMPLE_RATE = 16000.0
def run_s2st( input_audio: str ) -> tuple[tuple[int, np.ndarray] | None, str]:
    start = time.time()
    audio, orig_freq =torchaudio.load(input_audio)
    audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
    audio_inputs = processor(audios=audio, return_tensors="pt").to("cuda")
    # audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()
    audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].squeeze()
    # print("audio_array_from_audio:",audio_array_from_audio)
    # print("audio_array_from_audio:",type(audio_array_from_audio))
    # out_text = str(out_texts[0])
    out_wav = audio_array_from_audio.cpu().detach().numpy()

    end = time.time()
    print(f"cuda infer duration: {end - start} seconds")
    # print("out_wav:",type(out_wav))
    return (int(AUDIO_SAMPLE_RATE), out_wav)


with gr.Blocks() as demo_s2st:
    with gr.Row():
        with gr.Column():
            with gr.Group():
                input_audio = gr.Audio(label="Input speech",sources="microphone", type="filepath")
                btn = gr.Button("Translate")
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

        with gr.Column():
            with gr.Group():
                output_audio = gr.Audio(
                    label="Translated speech",
                    autoplay=True,
                    streaming=True,
                    type="numpy",
                )
                # output_text = gr.Textbox(label="Translated text")

        input_audio.stop_recording(
                    fn=run_s2st,
                    inputs=[input_audio],
                    outputs=[output_audio],
                    api_name="s2st",
                )

with gr.Blocks(css="style.css") as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Tabs():
        with gr.Tab(label="Speech-to-Speech Tranlation"):
            demo_s2st.render()


if __name__ == "__main__":
    demo.queue(max_size=50).launch(share=True)

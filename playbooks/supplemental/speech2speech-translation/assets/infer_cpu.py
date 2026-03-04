from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
import scipy
import time
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"
start = time.time()
processor = AutoProcessor.from_pretrained("./seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("./seamless-m4t-v2-large")
end = time.time()
print(f"model loading duration: {end - start} seconds")

# from audio
start = time.time()
audio, orig_freq =  torchaudio.load("./input1.wav")
audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
audio_inputs = processor(audios=audio, return_tensors="pt")
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()

end = time.time()
print(f"cpu infer duration: {end - start} seconds")

sample_rate = model.config.sampling_rate
scipy.io.wavfile.write("out.wav", rate=sample_rate, data=audio_array_from_audio)

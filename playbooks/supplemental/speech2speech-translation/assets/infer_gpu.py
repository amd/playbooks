from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
import scipy
import time
import os
os.environ["HIP_VISIBLE_DEVICES"] = "0"
start = time.time()
processor = AutoProcessor.from_pretrained("./seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("./seamless-m4t-v2-large").to("cuda")
end = time.time()
print(f"model loading duration: {end - start} seconds")

# from text
#text_inputs = processor(text = "Hello, my dog is cute", src_lang="eng", return_tensors="pt")
#audio_array_from_text = model.generate(**text_inputs, tgt_lang="cmn")[0].cpu().numpy().squeeze()

# from audio
start = time.time()
audio, orig_freq =  torchaudio.load("./audio_clips/input1.wav")
audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
audio_inputs = processor(audios=audio, return_tensors="pt").to("cuda")
audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()

end = time.time()
print(f"cuda infer duration: {end - start} seconds")

sample_rate = model.config.sampling_rate
#scipy.io.wavfile.write("out_from_text.wav", rate=sample_rate, data=audio_array_from_text)
#scipy.io.wavfile.write("out_from_audio.wav", rate=sample_rate, data=audio_array_from_audio)
scipy.io.wavfile.write("out1.wav", rate=sample_rate, data=audio_array_from_audio)

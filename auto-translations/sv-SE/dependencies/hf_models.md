<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face-modeller och dataset

Spelboken laddar ner sina Hugging Face-modeller och dataset första gången de används och sparar dem i Hugging Face-cachen (`~/.cache/huggingface/hub` såvida inte `HF_HOME` eller `HF_HUB_CACHE` pekar någon annanstans), så att senare körningar startar utan att behöva ladda ner dem igen.
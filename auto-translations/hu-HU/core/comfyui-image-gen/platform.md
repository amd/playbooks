<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platformkonfiguráció

Ez a dokumentum ismerteti a jelen forgatókönyv futtatásához szükséges platformkonfigurációkat.

## Szükséges alkalmazások/keretrendszerek
### Windows/Linux

A ComfyUI-t előre telepíteni kell a [ComfyUI telepítési útmutatóban](../../dependencies/comfyui.md) megadott utasítások alapján.

## Szükséges modellek

### Windows/Linux

A következő modelleknek jelen kell lenniük abban a könyvtárban, ahová a ComfyUI telepítve van, a `models` mappán belül.

| Modell típusa | Fájlnév | Méret | Hely | Letöltés |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Link](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Link](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Annak ellenőrzéséhez, hogy a modellek megfelelően vannak-e elhelyezve, [tekintse meg a ComfyUI forgatókönyvet az onboarding weboldalon](../../README.md#previewing-the-playbooks), és kövesse az utasításokat. A modellek akkor vannak megfelelően elhelyezve, ha a Z-Image Turbo sablon indításakor nem jelenik meg a „Models not found” oldal.
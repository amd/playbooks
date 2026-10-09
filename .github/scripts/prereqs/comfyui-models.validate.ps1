# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

$root = 'C:\ModelCache\ComfyUI\models'
foreach ($f in 'diffusion_models\z_image_turbo_bf16.safetensors', 'text_encoders\qwen_3_4b.safetensors', 'vae\ae.safetensors') {
  if (-not (Test-Path (Join-Path $root $f))) { exit 1 }
}
exit 0

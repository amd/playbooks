# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Mirror first, Hugging Face fallback.
$get = Join-Path $PSScriptRoot '..\mirror\get.py'
$py = if ($env:PREREQ_PYTHON) { $env:PREREQ_PYTHON } else { 'python' }
$root = 'C:\ModelCache\ComfyUI\models'
foreach ($f in 'diffusion_models\z_image_turbo_bf16.safetensors', 'text_encoders\qwen_3_4b.safetensors', 'vae\ae.safetensors') {
  & $py $get fetch ('models/ComfyUI/z_image_turbo/' + (Split-Path $f -Leaf)) --to (Join-Path $root $f) --upstream
  if ($LASTEXITCODE -ne 0) { exit 1 }
}
exit 0

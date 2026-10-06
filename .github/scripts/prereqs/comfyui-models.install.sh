#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# Mirror first, Hugging Face fallback; root-owned like the rest of /opt/model_cache.
get="$(dirname "$0")/../mirror/get.py"
py="${PREREQ_PYTHON:-python3}"
root=/opt/model_cache/ComfyUI/models
for f in diffusion_models/z_image_turbo_bf16.safetensors text_encoders/qwen_3_4b.safetensors vae/ae.safetensors; do
  sudo ARTIFACTORY_BASE="${ARTIFACTORY_BASE:-}" PLAYBOOKS_MIRROR_LEDGER="${PLAYBOOKS_MIRROR_LEDGER:-}" \
    "$py" "$get" fetch "models/ComfyUI/z_image_turbo/${f##*/}" --to "$root/$f" --upstream || exit 1
done

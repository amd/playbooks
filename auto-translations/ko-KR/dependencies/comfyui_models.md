<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI 모델

<!-- @device:halo_box -->
> **참고:** 모델이 이미 ComfyUI에서 사용 가능한 경우 이 섹션을 건너뛸 수 있습니다. 그렇지 않은 경우 아래 단계를 따라 다운로드하세요.
<!-- @device:end -->

이전에 미리 다운로드된 ComfyUI 모델을 삭제했거나 처음으로 다운로드하려는 경우, 누락된 모델이 감지되었다는 메시지가 표시될 때 각 모델에서 `Download` 버튼을 누르기만 하면 됩니다.
모델 파일을 올바른 위치에 수동으로 배치해야 할 수도 있습니다.

<!-- @device:halo_box -->
<!-- @os:linux -->
> **참고:** AMD Ryzen™ AI Halo에서는 ComfyUI가 사전 빌드된 컨테이너에서 실행됩니다. 수동으로 다운로드한 모델 파일은 컨테이너화된 ComfyUI가 찾을 수 있도록 `~/.local/share/ComfyUI/models` 아래(해당하는 `diffusion_models`, `text_encoders`, 또는 `vae` 하위 폴더)에 배치하세요.
<!-- @os:end -->
<!-- @device:end -->

<p align="center">
  <img src="/api/dependencies/assets/comfy_download.png" alt="ComfyUI Download Models" width="600"/>
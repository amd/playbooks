<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

Ryzen AI Halo의 경우, 전용 GPU 메모리는 기본적으로 64GB로 설정되어 있으며, 대부분의 워크로드에 충분합니다. 더 큰 모델이나 더 긴 컨텍스트의 경우 이 값을 96GB로 늘리면 도움이 될 수 있습니다. 조정하려면 **AMD Software: Adrenalin Edition™**을 열고 **Performance → Tuning → AMD Variable Graphics Memory**로 이동하세요. 변경 사항을 적용하려면 재부팅해야 합니다.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

전용 GPU 메모리 값을 변경하려면 **AMD Software: Adrenalin Edition™**을 열고 **Performance → Tuning → AMD Variable Graphics Memory**로 이동하세요. 변경 사항을 적용하려면 재부팅해야 합니다.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

Linux에서 더 큰 모델을 실행하려면 GPU에서 사용할 수 있는 **공유 메모리** 풀을 늘리세요. 이를 위해서는 공유 메모리 풀을 최대화할 수 있도록 BIOS 전용 GPU 메모리를 최소값으로 설정해야 할 수도 있습니다.

<!-- @device:halo_box -->

AMD Ryzen™ AI Halo의 경우 기본값은 96GB 공유입니다. 이를 수정하려면 **AMD Ryzen™ AI Developer Center**를 열고 **Settings** 탭으로 이동하세요. **Graphics Performance Settings**에서 **Shared Video Memory** 슬라이더를 늘린 다음, **Apply Changes**를 클릭하고 변경 사항을 적용하려면 재부팅하세요.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

커널의 Translation Table Manager(TTM) 페이지 설정을 변경하여 공유 메모리 풀을 늘리세요. AMD는 최대한 많은 양을 공유 메모리로 사용할 수 있도록 BIOS에서 전용 VRAM을 최소값(0.5GB)으로 설정할 것을 권장합니다.

1. `pipx` 유틸리티를 설치하고 pipx로 설치된 wheel의 경로를 시스템 검색 경로에 추가하세요:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. PyPI에서 `amd-debug-tools` wheel을 설치하세요:

   ```bash
   pipx install amd-debug-tools
   ```

3. 현재 공유 메모리 설정을 조회하세요:

   ```bash
   amd-ttm
   ```

4. 공유 메모리 할당을 늘리세요 (단위: GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. 변경 사항을 적용하려면 재부팅하세요.

<!-- @device:end -->

<!-- @os:end -->
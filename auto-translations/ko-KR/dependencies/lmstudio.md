<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
**AMD Ryzen™ AI Developer Center**에서 LM Studio를 설치할 수 있습니다. **Updates** 탭으로 이동하여 LM Studio가 아직 설치되어 있지 않은 경우 설치하세요.

LM Studio가 사전 설치된 모델을 인식할 수 있도록 하려면 Settings > General > Models Directory로 이동하세요. 그런 다음 경로를 `C:\Users\Public\models`로 변경하세요.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. 여기에서 설치 프로그램을 다운로드하세요: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. 설치합니다.
<!-- @device:end -->

> 팁: 설치 후, CLI(`lms`)를 초기화하기 위해 LM Studio를 한 번 실행하세요.

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> 참고: .deb 또는 AppImage 중 하나를 선택하여 설치할 수 있습니다.
1. 여기에서 appimage를 다운로드하세요: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. `sudo apt install libfuse2`를 실행합니다
3. `cd ~/Downloads`를 실행합니다
4. `chmod +x LM-Studio-*.AppImage`를 실행합니다
5. `./LM-Studio-*.AppImage`를 실행합니다
> 팁: 설치 후, CLI(`lms`)를 초기화하기 위해 LM Studio를 한 번 실행하세요.

<!-- @device:halo_box -->
LM Studio가 사전 설치된 모델을 인식할 수 있도록 하려면 Settings > General > Models Directory로 이동하세요. 그런 다음 경로를 `/var/cache/models`로 변경하세요.

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end -->
<!-- @os:end -->
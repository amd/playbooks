<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **기계 번역.** 이 페이지는 영어에서 자동으로 번역되었으며 사람에 의한 검토를 거치지 않았습니다. 이 페이지에는 오류가 포함될 수 있으며, 특정 지침, 명령어, 다운로드, 제품 가용성 또는 기타 콘텐츠가 언어나 지역에 따라 다를 수 있습니다. 본 번역본과 원문 사이에 불일치 또는 차이가 있는 경우, 영어 원문 playbook이 우선하며 이에 따릅니다.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# AMD Sync를 사용한 원격 개발

## 개요

**AMD Sync**는 노트북을 AMD Ryzen™ AI Halo용 원격 조종석으로 바꿔줍니다. 수동 SSH, 키, IDE 설정 과정을 건너뛰고, AMD Sync를 설치하면 Ryzen AI Halo에서 원격 터미널, VS Code, JupyterLab, 그리고 실시간 GPU/CPU/메모리 대시보드에 원클릭으로 액세스할 수 있습니다.

로컬 머신은 익숙한 그대로 유지되며, 모든 명령, 노트북, 모델은 Ryzen AI Halo에서 실행됩니다.

> **팁**: 이 페이지에는 AMDSync에 대한 새로운 업데이트가 포함됩니다.

## 학습 내용

- Ryzen AI Halo에서 SSH를 활성화하고 AMD Sync에서 연결하기
- 원클릭으로 Ryzen AI Halo에 대해 VS Code, 터미널, JupyterLab, 라이브 메트릭 실행하기
- AMD Sync의 관리형 프로젝트 폴더를 사용하여 원격 작업 구성하기

---

## 핵심 개념

AMD Sync에는 두 가지 측면이 있습니다: **클라이언트**(AMD Sync 앱이 실행되는 노트북)와 **서버**(AMD Sync가 터널링하는 SSH 서버가 실행되는 Ryzen AI Halo)입니다. AMD Sync에서 실행하는 모든 것 — VS Code, 터미널, 노트북 — 은 로컬에서 열리지만 Ryzen AI Halo에서 실행됩니다.

> **지원되는 클라이언트:** Windows 11 및 Linux. macOS는 지원되지 않습니다.

---

## 1단계 — Ryzen AI Halo에서 SSH 활성화


> **참고:** Windows에서 Ryzen AI Halo는 SSH 서버가 *기본적으로 꺼진* 상태로 제공됩니다. Linux에서는 SSH 서버가 *기본적으로 켜진* 상태로 제공됩니다.

1. Ryzen AI Halo에서 **AMD Ryzen™ AI Developer Center**를 엽니다.
2. **Remote** 탭으로 이동합니다.
3. **SSH Server**를 켭니다.
4. **Server Information** 아래에 표시된 **IP Address**, **Port**, **Username**을 확인하세요 — 이 값을 AMD Sync에 붙여넣게 됩니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **참고:** 이것은 Windows용 AMD Developer Center입니다. Linux용은 UI가 다를 수 있지만, 유사한 원격 기능을 제공합니다.

> **팁:** AMD Sync는 Developer Center의 비밀번호가 아니라 해당 사용자의 **OS 로그인 비밀번호**를 요청합니다.

---

## 2단계 — 클라이언트에 AMD Sync 설치

AMD Sync는 Windows 11 및 Linux에서 실행됩니다. 사용 중인 OS에 맞는 설치 프로그램을 다운로드한 다음 아래 단계를 따르세요. 설치 후, **Get Started** 화면에서 **Accept & Install**을 클릭하면 — AMD Sync가 완료 시 자동으로 실행됩니다.

### Windows

[AMDSyncInstaller.exe 다운로드](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe`를 더블클릭합니다.
2. **Accept & Install**을 클릭합니다.

> Windows 방화벽에서 메시지가 표시되면, AMD Sync가 SSH를 통해 Ryzen AI Halo에 도달할 수 있도록 네트워크 액세스를 허용하세요.

### Linux

원하는 형식의 링크를 클릭하여 다운로드하세요:

| 형식 | 다운로드 | 설치 명령 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **참고:** Ubuntu App Center는 로컬에서 연 `.deb` 파일을 *"잠재적으로 안전하지 않음"*으로 표시할 수 있습니다. 이는 모든 타사 로컬 설치 프로그램에 대한 표준 경고입니다. `.deb` 파일을 더블클릭했을 때 실패하면 위의 터미널 명령을 사용하세요.

---

## 3단계 — Ryzen AI Halo에 연결

처음 실행하면 AMD Sync에 **Add a Remote Device** 양식이 표시됩니다. Developer Center의 **Remote** 탭에 있는 값을 사용하여 이 양식을 작성하세요.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 필드 | 참고 사항 |
|-------|-------|
| **Device Name** *(선택 사항)* | `Ryzen AI Halo`와 같은 친숙한 레이블. 기본값은 `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote 탭에서 확인 |
| **SSH Port** | Remote 탭에서 확인 (숫자만) |
| **Username** | Ryzen AI Halo의 OS 계정 이름 |
| **Password** | OS 로그인 비밀번호 — 입력 시 마스킹 처리됨 |

**Add Device**를 클릭합니다. 짧은 로딩 화면 후, **"Connection Successful"**이 표시되고 홈 화면으로 이동합니다. 이 화면은 시스템 트레이에 상주합니다. 창 밖을 클릭하면 창이 닫히지만, AMD Sync는 계속 실행되며 클릭 한 번으로 다시 열 수 있습니다.

> **연결에 실패하면,** AMD Sync는 입력한 값을 유지한 채 양식으로 돌아갑니다. 일반적인 원인은 Ryzen AI Halo에서 SSH가 비활성화되어 있거나, 비밀번호가 잘못되었거나, 두 장치가 서로 다른 네트워크에 있는 경우입니다.

---

## 4단계 — 첫 번째 원격 도구 실행

홈 화면에서는 클라이언트와 Ryzen AI Halo가 실행 중인 OS와 관계없이 사용 가능한 다섯 가지 원클릭 구성 요소를 제공합니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 구성 요소 | 기능 |
|-----------|--------------|
| **Directory** | VS Code, 터미널, JupyterLab이 열릴 Ryzen AI Halo의 폴더를 선택합니다. 기본값은 관리형 `Documents/AMD_Sync` 작업 공간입니다. |
| **VS Code** | 선택한 폴더에 대한 SSH 터널로 로컬에서 VS Code를 엽니다. |
| **Terminal** | 선택한 폴더에서 Ryzen AI Halo에 SSH로 연결된 로컬 터미널을 엽니다. |
| **JupyterLab** | 선택한 폴더로 범위가 지정된, Ryzen AI Halo에 SSH로 연결된 노트북 프로젝트를 실행합니다. |
| **Live Metrics** | Ryzen AI Halo의 GPU, 메모리, CPU 사용률에 대한 실시간 보기입니다. |

### VS Code 사용해보기

처음 실행할 때는 **VS Code**를 사용해 보세요.

1. **Directory**를 기본값인 `~/Documents/AMD_Sync`로 그대로 둡니다.
2. **VS Code**를 클릭합니다.
3. AMD Sync가 Ryzen AI Halo에 `Documents/AMD_Sync/Project_1`을 생성하고, 이에 터널링된 로컬 VS Code를 엽니다.

이제 Ryzen AI Halo에 있는 파일을 로컬 VS Code 설정으로 편집하고 있는 것입니다. `helloworld.py`를 생성하고 `print("hello world")`를 추가한 다음, 통합 터미널(`` Ctrl + ` ``)을 열고 실행합니다:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

상태 표시줄에는 **SSH: Linux**가 표시됩니다 — 코드가 노트북이 아니라 Ryzen AI Halo에서 실행되고 있다는 증거입니다.
### 터미널 사용해보기

**Terminal**을 클릭하면 키보드에서 손을 떼지 않고도 SSH를 통해 동일한 폴더로 바로 이동할 수 있습니다.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows에서 기본 터미널은 **PowerShell**입니다 — 원한다면 설정 메뉴에서 **Windows Command Prompt**로 전환할 수 있습니다. Linux에서 AMD Sync는 시스템 기본 터미널을 사용합니다.

---

## 디렉터리 작동 방식

**Directory** 드롭다운은 AMD Sync에서 가장 중요한 단일 컨트롤입니다 — 실행하는 모든 도구가 Ryzen AI Halo의 어디에 위치할지 결정합니다.

- **`~/Documents/AMD_Sync` (기본값)** — 여기서 VS Code나 JupyterLab을 실행하면 새 프로젝트 폴더가 자동으로 생성됩니다 (VS Code의 경우 `Project_1`, `Project_2`, …; JupyterLab의 경우 `Notebook_Project_1`, `Notebook_Project_2`, …).
- **기존 프로젝트 폴더** — `AMD_Sync`의 직계 하위 폴더(수동으로 Ryzen AI Halo에서 생성한 폴더 포함)는 드롭다운에 표시됩니다. 마지막으로 사용한 폴더가 다음 번의 기본값이 됩니다.
- **사용자 지정 경로** — 절대 경로를 입력하면 Ryzen AI Halo의 다른 위치에 있는 폴더를 열 수 있습니다. AMD Sync는 해당 폴더를 *열기만* 합니다 — `AMD_Sync` 외부에는 폴더를 생성하지 않으며, 사용자 지정 경로는 세션 간에 저장되지 않습니다.

사용자 지정 경로가 작동하지 않으면 AMD Sync가 그 이유를 알려줍니다: 잘못된 구문, 폴더가 존재하지 않음, 또는 경로가 파일을 가리킴.

---

## 실시간 메트릭 및 JupyterLab

- **Live Metrics** — GPU, 메모리, CPU 사용률의 실시간 대시보드입니다. 원격 훈련 실행이 실제로 하드웨어를 사용하고 있는지 확인하는 가장 빠른 방법입니다.
- **JupyterLab** — Ryzen AI Halo에 SSH로 연결된 완전한 노트북 프로젝트로, 자체 통합 터미널을 갖추고 있어 UI를 벗어나지 않고도 노트북 셀과 셸 명령을 혼합해서 사용할 수 있습니다.

---

## 설정 및 다중 디바이스

**Settings** 메뉴에는 세 개의 탭이 있습니다:

| 탭 | 내용 |
|-----|----------------|
| **Devices** | 성공적으로 연결한 모든 Ryzen AI Halo 목록을 표시합니다. 재연결, 자격 증명 편집, 또는 새 디바이스 추가가 가능합니다. |
| **Information** | 문서 및 포럼 지원 링크입니다. |
| **Customize** | 데스크톱에서 앱 위치 재조정, 터미널 유형 전환(Windows 전용), AMD Sync 업데이트 확인이 가능합니다. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **터미널 유형 (Windows)** — **PowerShell**(기본값)과 **Windows Command Prompt** 중에서 선택합니다.
- **터미널 유형 (Linux)** — 기본 시스템 터미널만 사용할 수 있습니다.
- **앱 업데이트** — 이 탭은 UI 내에서 새로운 AMD Sync 버전을 확인하고 설치하기에 적합한 위치입니다; 별도의 업데이트 프로그램이 필요하지 않습니다.

> 디바이스는 첫 연결에 성공한 후에만 **Devices** 아래에 표시되므로, 실패한 시도로 인해 목록이 지저분해지지 않습니다.

---

## 문제 해결

- **연결이 즉시 실패함** — Developer Center의 Ryzen AI Halo **Remote** 탭에서 SSH 서버가 활성화되어 있는지 확인하세요.
- **비밀번호 오류** — Developer Center에서 가져온 비밀번호가 아니라 Ryzen AI Halo의 **OS 로그인 비밀번호**를 사용하세요.
- **VS Code 버튼이 작동하지 않음** — [code.visualstudio.com](https://code.visualstudio.com)에서 클라이언트 머신에 VS Code를 설치하세요.
- **AMD Sync 트레이 아이콘이 표시되지 않음 (Linux/GNOME)** — AppIndicator 확장 프로그램을 설치하고 활성화하세요.
- **`.deb` 파일이 파일 관리자에서 열리지 않음** — 터미널에서 `sudo apt install ./AMDSyncInstaller.deb`를 사용하세요.

---
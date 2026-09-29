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

# AMD Sync를 활용한 원격 개발

## 개요

**AMD Sync**는 노트북을 AMD Ryzen™ AI Halo용 원격 조종석으로 만들어줍니다. 수동 SSH, 키, IDE 설정 과정을 건너뛰고 AMD Sync를 설치하면 Ryzen AI Halo에서 원격 터미널, VS Code, JupyterLab, 그리고 실시간 GPU/CPU/메모리 대시보드에 원클릭으로 액세스할 수 있습니다.

로컬 머신은 익숙한 그대로 유지되며, 모든 명령어, 노트북, 모델은 Ryzen AI Halo에서 실행됩니다.

> **팁**: 이 페이지에는 AMDSync에 대한 새로운 업데이트가 포함될 예정입니다. 

## 배우게 될 내용

- Ryzen AI Halo에서 SSH를 활성화하고 AMD Sync에서 연결하기
- Ryzen AI Halo를 대상으로 원클릭으로 VS Code, 터미널, JupyterLab, 실시간 메트릭 실행하기
- AMD Sync의 관리형 프로젝트 폴더를 사용해 원격 작업을 정리하기

---

## 핵심 개념

AMD Sync는 두 측면으로 구성됩니다: **클라이언트**(AMD Sync 앱을 실행하는 노트북)와 **서버**(AMD Sync가 터널링하는 SSH 서버를 실행하는 Ryzen AI Halo)입니다. AMD Sync에서 실행하는 모든 것 — VS Code, 터미널, 노트북 — 은 로컬에서 열리지만 실행은 Ryzen AI Halo에서 이루어집니다.

> **지원되는 클라이언트:** Windows 11 및 Linux. macOS는 지원되지 않습니다.

---

## 1단계 — Ryzen AI Halo에서 SSH 활성화


> **참고:** Windows에서는 Ryzen AI Halo가 SSH 서버가 *기본적으로 꺼진* 상태로 제공됩니다. Linux에서는 SSH 서버가 *기본적으로 켜진* 상태로 제공됩니다.

1. Ryzen AI Halo에서 **AMD Ryzen™ AI Developer Center**를 엽니다.
2. **Remote** 탭으로 이동합니다.
3. **SSH Server**를 켭니다.
4. **Server Information**에 표시된 **IP Address**, **Port**, **Username**을 기록해 둡니다 — 이 값들을 AMD Sync에 붙여넣게 됩니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **참고:** 이는 Windows용 AMD Developer Center입니다. Linux용은 UI가 다를 수 있지만 원격 기능은 유사합니다.

> **팁:** AMD Sync는 Developer Center의 비밀번호가 아니라 해당 사용자의 **OS 로그인 비밀번호**를 요구합니다.

---

## 2단계 — 클라이언트에 AMD Sync 설치

AMD Sync는 Windows 11 및 Linux에서 실행됩니다. 사용 중인 OS에 맞는 설치 프로그램을 다운로드한 후 아래 단계를 따르세요. 설치가 끝나면 **Get Started** 화면에서 **Accept & Install**을 클릭하세요 — 설치가 완료되면 AMD Sync가 자동으로 실행됩니다.

### Windows

[AMDSyncInstaller.exe 다운로드](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe`를 더블클릭합니다.
2. **Accept & Install**을 클릭합니다.

> Windows 방화벽에서 메시지가 표시되면, AMD Sync가 SSH를 통해 Ryzen AI Halo에 접근할 수 있도록 네트워크 액세스를 허용하세요.

### Linux

원하는 형식의 링크를 클릭해 다운로드하세요:

| 형식 | 다운로드 | 설치 명령어 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **참고:** Ubuntu App Center는 로컬에서 연 `.deb` 파일을 *"잠재적으로 안전하지 않음(Potentially unsafe)"*으로 표시할 수 있습니다. 이는 모든 타사 로컬 설치 프로그램에 적용되는 표준 경고입니다. `.deb` 파일 더블클릭이 실패하면 위의 터미널 명령어를 사용하세요.

---

## 3단계 — Ryzen AI Halo에 연결하기

처음 실행하면 AMD Sync에 **Add a Remote Device** 양식이 표시됩니다. Developer Center의 **Remote** 탭에 있는 값을 사용해 이를 채우세요.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 필드 | 참고 사항 |
|-------|-------|
| **Device Name** *(선택 사항)* | `Ryzen AI Halo`와 같은 친숙한 레이블입니다. 기본값은 `Device 1`, `Device 2`, … 입니다. |
| **Hostname or IP** | Remote 탭에서 확인 |
| **SSH Port** | Remote 탭에서 확인 (숫자만) |
| **Username** | Ryzen AI Halo의 OS 계정 이름 |
| **Password** | OS 로그인 비밀번호 — 입력 시 마스킹 처리됨 |

**Add Device**를 클릭합니다. 잠시 로딩 화면이 표시된 후 **"Connection Successful"**이 표시되며 시스템 트레이에 위치한 홈 화면으로 이동합니다. 창을 닫으려면 창 밖을 클릭하세요. AMD Sync는 계속 실행되며 한 번의 클릭으로 접근할 수 있습니다.

> **연결에 실패하면,** AMD Sync는 입력했던 값을 유지한 채 양식으로 돌아갑니다. 일반적인 원인은 Ryzen AI Halo에서 SSH가 비활성화되어 있거나, 비밀번호가 잘못되었거나, 두 기기가 서로 다른 네트워크에 있는 경우입니다.

---

## 4단계 — 첫 번째 원격 도구 실행하기

홈 화면에는 원클릭으로 실행할 수 있는 다섯 가지 구성 요소가 있습니다 — 클라이언트와 Ryzen AI Halo가 어떤 OS에서 실행되든 모두 사용할 수 있습니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 구성 요소 | 기능 |
|-----------|--------------|
| **Directory** | VS Code, Terminal, JupyterLab이 열릴 Ryzen AI Halo의 폴더를 선택합니다. 기본값은 관리형 `Documents/AMD_Sync` 작업 공간입니다. |
| **VS Code** | 선택한 폴더로 SSH 터널을 연결하여 로컬에서 VS Code를 엽니다. |
| **Terminal** | 선택한 폴더에서 Ryzen AI Halo에 SSH로 연결된 로컬 터미널을 엽니다. |
| **JupyterLab** | 선택한 폴더 범위 내에서 Ryzen AI Halo에 SSH로 연결된 노트북 프로젝트를 실행합니다. |
| **Live Metrics** | Ryzen AI Halo의 GPU, 메모리, CPU 사용률을 실시간으로 확인합니다. |

### VS Code 사용해보기

첫 실행에서는 **VS Code**를 사용해 보세요.

1. **Directory**를 기본값인 `~/Documents/AMD_Sync`로 둡니다.
2. **VS Code**를 클릭합니다.
3. AMD Sync가 Ryzen AI Halo에 `Documents/AMD_Sync/Project_1`을 생성하고, 이에 터널링된 VS Code를 로컬에서 엽니다.

이제 로컬 VS Code 환경으로 Ryzen AI Halo에 있는 파일을 편집하고 있는 것입니다. `helloworld.py`를 생성하고 `print("hello world")`를 추가한 후 통합 터미널(`` Ctrl + ` ``)을 열어 실행해보세요:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

상태 표시줄에 **SSH: Linux**가 표시됩니다 — 이는 코드가 노트북이 아닌 Ryzen AI Halo에서 실행되고 있다는 증거입니다.
### 터미널 사용해보기

**Terminal**을 클릭하면 키보드에서 손을 떼지 않고도 SSH를 통해 동일한 폴더로 바로 진입할 수 있습니다.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows에서는 기본 터미널이 **PowerShell**입니다 — 원한다면 Settings 메뉴에서 **Windows Command Prompt**로 전환할 수 있습니다. Linux에서는 AMD Sync가 시스템의 기본 터미널을 사용합니다.

---

## Directory가 작동하는 방식

**Directory** 드롭다운은 AMD Sync에서 가장 중요한 단일 컨트롤입니다 — 실행하는 모든 도구가 Ryzen AI Halo의 어느 위치에 놓일지를 결정합니다.

- **`~/Documents/AMD_Sync` (기본값)** — 여기서 VS Code나 JupyterLab을 실행하면 새 프로젝트 폴더가 자동으로 생성됩니다(VS Code의 경우 `Project_1`, `Project_2`, …; JupyterLab의 경우 `Notebook_Project_1`, `Notebook_Project_2`, …).
- **기존 프로젝트 폴더** — `AMD_Sync`의 바로 아래에 있는 모든 폴더(Ryzen AI Halo에서 수동으로 생성한 폴더 포함)가 드롭다운에 표시됩니다. 마지막으로 사용한 폴더가 다음번에 기본값이 됩니다.
- **사용자 지정 경로** — Ryzen AI Halo의 다른 위치에 있는 폴더를 열려면 절대 경로를 입력하세요. AMD Sync는 해당 폴더를 *열기만* 합니다 — `AMD_Sync` 외부에 폴더를 생성하지 않으며, 사용자 지정 경로는 세션 간에 저장되지 않습니다.

사용자 지정 경로가 작동하지 않으면 AMD Sync가 그 이유를 알려줍니다: 잘못된 구문, 폴더가 존재하지 않음, 또는 경로가 파일을 가리키는 경우입니다.

---

## Live Metrics 및 JupyterLab

- **Live Metrics** — GPU, 메모리, CPU 사용량을 실시간으로 보여주는 대시보드입니다. 원격 학습 작업이 실제로 하드웨어를 사용하고 있는지 확인하는 가장 빠른 방법입니다.
- **JupyterLab** — Ryzen AI Halo에 SSH로 연결된 완전한 노트북 프로젝트로, 자체 통합 터미널이 있어 UI를 벗어나지 않고도 노트북 셀과 셸 명령을 함께 사용할 수 있습니다.

---

## Settings 및 다중 장치

**Settings** 메뉴에는 세 개의 탭이 있습니다:

| 탭 | 다루는 내용 |
|-----|----------------|
| **Devices** | 성공적으로 연결한 모든 Ryzen AI Halo 목록을 표시합니다. 다시 연결하거나, 자격 증명을 수정하거나, 새 장치를 추가할 수 있습니다. |
| **Information** | 문서 및 포럼 지원 링크입니다. |
| **Customize** | 데스크톱에서 앱 위치를 재배치하고, 터미널 유형을 전환하며(Windows만 해당), AMD Sync 업데이트를 확인합니다. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **터미널 유형 (Windows)** — **PowerShell**(기본값)과 **Windows Command Prompt** 중에서 선택할 수 있습니다.
- **터미널 유형 (Linux)** — 기본 시스템 터미널만 사용할 수 있습니다.
- **앱 업데이트** — 이 탭은 UI 내에서 새 AMD Sync 버전을 확인하고 설치하기에 적합한 곳입니다. 별도의 업데이터가 필요하지 않습니다.

> 장치는 처음 연결에 성공한 후에만 **Devices** 아래에 표시되므로, 실패한 시도는 목록을 어지럽히지 않습니다.

---

## 문제 해결

- **연결이 즉시 실패함** — Developer Center의 Ryzen AI Halo **Remote** 탭에서 SSH 서버가 활성화되어 있는지 확인하세요.
- **비밀번호 오류** — Developer Center에서 가져온 비밀번호가 아니라 Ryzen AI Halo의 **OS 로그인 비밀번호**를 사용하세요.
- **VS Code 버튼이 아무 반응이 없음** — [code.visualstudio.com](https://code.visualstudio.com)에서 클라이언트 머신에 VS Code를 설치하세요.
- **AMD Sync 트레이 아이콘이 보이지 않음 (Linux/GNOME)** — AppIndicator 확장 프로그램을 설치하고 활성화하세요.
- **`.deb` 파일이 파일 관리자에서 열리지 않음** — 터미널에서 `sudo apt install ./AMDSyncInstaller.deb`를 사용하세요.
- **실행할 때마다 설정 화면이 다시 나타남 (Linux)**: 로그인 키링을 잠금 해제하거나 `--password-store=gnome-libsecret` 옵션으로 실행한 다음, 설정을 한 번 다시 진행하세요.

---
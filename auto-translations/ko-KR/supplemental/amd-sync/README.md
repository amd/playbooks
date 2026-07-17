<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

# AMD Sync을 활용한 원격 개발

## 개요

**AMD Sync**는 노트북을 AMD Ryzen™ AI Halo의 원격 조종석으로 전환합니다. 수동 SSH, 키, IDE 설정 과정을 건너뛰고 — AMD Sync를 설치하면 Ryzen AI Halo의 원격 터미널, VS Code, JupyterLab, 실시간 GPU/CPU/메모리 대시보드에 원클릭으로 접근할 수 있습니다.

로컬 머신은 익숙한 환경 그대로 유지되며, 모든 명령, 노트북, 모델은 Ryzen AI Halo에서 실행됩니다.

> **팁**: 이 페이지에는 AMDSync의 새로운 업데이트 내용이 게시됩니다.

## 학습 내용

- Ryzen AI Halo에서 SSH를 활성화하고 AMD Sync에서 연결하기
- 원클릭으로 Ryzen AI Halo에 대한 VS Code, 터미널, JupyterLab, 실시간 메트릭 실행하기
- AMD Sync의 관리형 프로젝트 폴더를 사용하여 원격 작업 구성하기

---

## 핵심 개념

AMD Sync는 두 가지 측면으로 구성됩니다: **클라이언트**(AMD Sync 앱을 실행하는 노트북)와 **서버**(AMD Sync가 터널링하는 SSH 서버를 실행하는 Ryzen AI Halo). AMD Sync에서 실행하는 모든 것 — VS Code, 터미널, 노트북 — 은 로컬에서 열리지만 Ryzen AI Halo에서 실행됩니다.

> **지원되는 클라이언트:** Windows 11 및 Linux. macOS는 지원되지 않습니다.

---

## 1단계 — Ryzen AI Halo에서 SSH 활성화


> **참고:** Windows에서 Ryzen AI Halo는 SSH 서버가 *기본적으로 꺼진* 상태로 제공됩니다. Linux에서는 SSH 서버가 *기본적으로 켜진* 상태로 제공됩니다.

1. Ryzen AI Halo에서 **AMD Ryzen™ AI Developer Center**를 엽니다.
2. **Remote** 탭으로 이동합니다.
3. **SSH Server**를 켭니다.
4. **Server Information** 아래에 표시된 **IP Address**, **Port**, **Username**을 메모합니다 — AMD Sync에 붙여넣을 때 사용합니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **참고:** 이것은 Windows용 AMD Developer Center입니다. Linux 버전은 UI가 다를 수 있지만 유사한 원격 기능을 제공합니다.

> **팁:** AMD Sync는 Developer Center의 비밀번호가 아닌 해당 사용자의 **OS 로그인 비밀번호**를 요청합니다.

---

## 2단계 — 클라이언트에 AMD Sync 설치

AMD Sync는 Windows 11 및 Linux에서 실행됩니다. 사용 중인 OS에 맞는 설치 프로그램을 다운로드한 후 아래 단계를 따르세요. 설치 후 **시작하기** 화면에서 **Accept & Install**을 클릭하면 — AMD Sync가 완료 시 자동으로 실행됩니다.

### Windows

[AMDSyncInstaller.exe 다운로드](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. `AMDSyncInstaller.exe`를 더블클릭합니다.
2. **Accept & Install**을 클릭합니다.

> Windows 방화벽에서 메시지가 표시되면 AMD Sync가 SSH를 통해 Ryzen AI Halo에 접근할 수 있도록 네트워크 액세스를 허용하세요.

### Linux

원하는 형식의 링크를 클릭하여 다운로드하세요:

| 형식 | 다운로드 | 설치 명령 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **참고:** Ubuntu App Center는 로컬에서 열린 `.deb` 파일을 *"잠재적으로 안전하지 않음"*으로 표시할 수 있습니다. 이는 타사 로컬 설치 프로그램에 대한 표준 경고입니다. `.deb` 파일을 더블클릭하는 것이 실패하면 위의 터미널 명령을 사용하세요.

---

## 3단계 — Ryzen AI Halo에 연결

처음 실행 시 AMD Sync는 **Add a Remote Device** 양식을 표시합니다. Developer Center의 **Remote** 탭에서 확인한 값을 입력하세요.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 필드 | 참고 |
|-------|-------|
| **Device Name** *(선택 사항)* | `Ryzen AI Halo`와 같은 친숙한 레이블. 기본값은 `Device 1`, `Device 2`, … |
| **Hostname or IP** | Remote 탭에서 확인 |
| **SSH Port** | Remote 탭에서 확인 (숫자만 입력) |
| **Username** | Ryzen AI Halo의 OS 계정 이름 |
| **Password** | OS 로그인 비밀번호 — 입력 시 마스킹됨 |

**Add Device**를 클릭합니다. 잠시 로딩 화면이 표시된 후 **"Connection Successful"**이 나타나고 시스템 트레이에 위치한 홈 화면으로 이동합니다. 창 밖을 클릭하면 닫히며, AMD Sync는 계속 실행 중이고 한 번의 클릭으로 접근할 수 있습니다.

> **연결에 실패하면,** AMD Sync는 입력한 값이 유지된 상태로 양식으로 돌아갑니다. 일반적인 원인은 Ryzen AI Halo에서 SSH가 비활성화되어 있거나, 잘못된 비밀번호를 입력했거나, 두 기기가 서로 다른 네트워크에 있는 경우입니다.

---

## 4단계 — 첫 번째 원격 도구 실행

홈 화면에는 다섯 가지 원클릭 구성 요소가 있으며 — 클라이언트와 Ryzen AI Halo의 OS에 관계없이 모두 사용할 수 있습니다.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 구성 요소 | 기능 |
|-----------|--------------|
| **Directory** | VS Code, 터미널, JupyterLab이 열릴 Ryzen AI Halo의 폴더를 선택합니다. 기본값은 관리형 `Documents/AMD_Sync` 작업 공간입니다. |
| **VS Code** | 선택한 폴더로 SSH 터널을 통해 로컬에서 VS Code를 엽니다. |
| **Terminal** | 선택한 폴더에서 Ryzen AI Halo에 SSH로 연결된 로컬 터미널을 엽니다. |
| **JupyterLab** | 선택한 폴더 범위 내에서 Ryzen AI Halo에 SSH로 연결된 노트북 프로젝트를 실행합니다. |
| **Live Metrics** | Ryzen AI Halo의 GPU, 메모리, CPU 사용률을 실시간으로 표시합니다. |

### VS Code 사용해 보기

처음 실행 시 **VS Code**를 사용해 보세요.

1. **Directory**를 기본값 `~/Documents/AMD_Sync`로 유지합니다.
2. **VS Code**를 클릭합니다.
3. AMD Sync가 Ryzen AI Halo에 `Documents/AMD_Sync/Project_1`을 생성하고 로컬에서 VS Code를 열어 해당 폴더로 터널링합니다.

이제 로컬 VS Code 환경으로 Ryzen AI Halo에 있는 파일을 편집할 수 있습니다. `helloworld.py`를 생성하고 `print("hello world")`를 추가한 후, 통합 터미널(`` Ctrl + ` ``)을 열고 실행하세요:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

상태 표시줄에 **SSH: Linux**가 표시됩니다 — 코드가 노트북이 아닌 Ryzen AI Halo에서 실행되고 있다는 증거입니다.

### 터미널 사용해 보기

**Terminal**을 클릭하면 키보드를 벗어나지 않고 SSH를 통해 동일한 폴더로 바로 접속할 수 있습니다.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

Windows에서 기본 터미널은 **PowerShell**입니다 — 원하는 경우 설정 메뉴에서 **Windows Command Prompt**로 전환할 수 있습니다. Linux에서 AMD Sync는 기본 시스템 터미널을 사용합니다.

---

## Directory 작동 방식

**Directory** 드롭다운은 AMD Sync에서 가장 중요한 컨트롤입니다 — Ryzen AI Halo에서 실행하는 모든 도구가 열릴 위치를 결정합니다.

- **`~/Documents/AMD_Sync` (기본값)** — 여기서 VS Code 또는 JupyterLab을 실행하면 새 프로젝트 폴더가 자동으로 생성됩니다(VS Code의 경우 `Project_1`, `Project_2`, …; JupyterLab의 경우 `Notebook_Project_1`, `Notebook_Project_2`, …).
- **기존 프로젝트 폴더** — `AMD_Sync`의 직접 하위 폴더(Ryzen AI Halo에서 수동으로 생성한 폴더 포함)가 드롭다운에 표시됩니다. 마지막으로 사용한 폴더가 다음 번 기본값이 됩니다.
- **사용자 지정 경로** — 절대 경로를 입력하여 Ryzen AI Halo의 다른 위치에 있는 폴더를 열 수 있습니다. AMD Sync는 해당 폴더를 *열기만* 합니다 — `AMD_Sync` 외부에 폴더를 생성하지 않으며, 사용자 지정 경로는 세션 간에 저장되지 않습니다.

사용자 지정 경로가 작동하지 않으면 AMD Sync가 그 이유를 알려줍니다: 잘못된 구문, 폴더가 존재하지 않음, 또는 경로가 파일을 가리키는 경우.

---

## Live Metrics 및 JupyterLab

- **Live Metrics** — GPU, 메모리, CPU 사용량의 실시간 대시보드. 원격 학습 실행이 실제로 하드웨어에 도달하고 있는지 확인하는 가장 빠른 방법입니다.
- **JupyterLab** — Ryzen AI Halo에 SSH로 연결된 완전한 노트북 프로젝트로, UI를 벗어나지 않고 노트북 셀과 셸 명령을 혼합할 수 있는 통합 터미널이 포함되어 있습니다.

---

## 설정 및 여러 기기

**Settings** 메뉴에는 세 가지 탭이 있습니다:

| 탭 | 내용 |
|-----|----------------|
| **Devices** | 성공적으로 연결한 모든 Ryzen AI Halo 목록. 재연결, 자격 증명 편집, 또는 새 기기 추가. |
| **Information** | 문서 및 포럼 지원 링크. |
| **Customize** | 데스크톱에서 앱 위치 변경, 터미널 유형 전환(Windows만 해당), AMD Sync 업데이트 확인. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **터미널 유형 (Windows)** — **PowerShell**(기본값)과 **Windows Command Prompt** 중에서 선택합니다.
- **터미널 유형 (Linux)** — 기본 시스템 터미널만 사용 가능합니다.
- **앱 업데이트** — 이 탭은 별도의 업데이터 없이 UI 내에서 새 AMD Sync 버전을 확인하고 설치하기에 적합한 곳입니다.

> 기기는 첫 번째 연결이 성공한 후에만 **Devices** 아래에 표시되므로, 실패한 시도는 목록을 어지럽히지 않습니다.

---

## 문제 해결

- **연결이 즉시 실패함** — Developer Center의 **Remote** 탭에서 Ryzen AI Halo의 SSH 서버가 활성화되어 있는지 확인하세요.
- **잘못된 비밀번호 오류** — Developer Center의 비밀번호가 아닌 Ryzen AI Halo의 **OS 로그인 비밀번호**를 사용하세요.
- **VS Code 버튼이 작동하지 않음** — [code.visualstudio.com](https://code.visualstudio.com)에서 클라이언트 머신에 VS Code를 설치하세요.
- **AMD Sync 트레이 아이콘이 없음 (Linux/GNOME)** — AppIndicator 확장을 설치하고 활성화하세요.
- **`.deb` 파일이 파일 관리자에서 열리지 않음** — 터미널에서 `sudo apt install ./AMDSyncInstaller.deb`를 사용하세요.

---
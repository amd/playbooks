<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maschinelle Übersetzung.** Diese Seite wurde automatisch aus dem Englischen übersetzt und nicht von einem Menschen überprüft. Sie kann Fehler enthalten, und bestimmte Anweisungen, Befehle, Downloads, Produktverfügbarkeiten oder andere Inhalte können je nach Sprache oder Region abweichen. Im Falle von Unstimmigkeiten oder Widersprüchen ist die englische Originalversion des playbook maßgeblich und hat Vorrang.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Vier Ryzen™ AI Halos mit RPC clustern

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird, sodass Sie Zugriff auf noch größere Modelle mit stärkerem logischem Denkvermögen, besserer Codegenerierung und tieferem mehrsprachigem Verständnis erhalten – vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie vier Ryzen AI Halo Systeme mit der RPC-Engine von llama.cpp clustern und Kimi K2.6, ein großes Mixture-of-Experts-Modell, mit AMD ROCm™-Beschleunigung auf allen vier Maschinen ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo Systemen erweitern
- Installation von llama.cpp mit ROCm- und RPC-Unterstützung
- Konfiguration von RPC-Workern und Start verteilter Inferenz über vier Knoten
- Ausführung eines Modells mit 1 Billion Parametern über vier vernetzte Ryzen AI Halo Systeme

## Festlegen der Speicherkonfiguration

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen (Maschine 1 bis Maschine 4) durch.

<!-- @os:windows -->
Unter Windows müssen wir, um größere Modelle auszuführen, die mehr Speicher benötigen, die AMD Variable Graphics Memory (iGPU-VRAM)-Zuweisung verwenden.

Dies kann erfolgen, indem Sie das AMD Software: Adrenalin Edition-Kontrollzentrum öffnen und zu: `Performance > Tuning > AMD Variable Graphics Memory` navigieren. Setzen Sie den Wert auf **96 GB**. Bitte starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Unter Linux verwendet ROCm einen gemeinsamen Systemspeicherpool, und dieser Pool ist standardmäßig auf die Hälfte des Systemspeichers konfiguriert.

Dieser Betrag kann erhöht werden, indem die TTM-Seiteneinstellung (Translation Table Manager) des Kernels mit den folgenden Anweisungen geändert wird. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS festzulegen (0,5 GB).

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für mit pipx installierte Wheels zum Systemsuchpfad hinzu.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installieren Sie das amd-debug-tools-Wheel von PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Führen Sie das amd-ttm-Tool aus, um die aktuellen Einstellungen für den gemeinsamen Speicher abzufragen.
  ```bash
  amd-ttm
  ```

* Konfigurieren Sie die Einstellungen für gemeinsamen Speicher auf **120 GB** neu:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.


<!-- @os:end -->
<!-- @device:halo_box -->
## Nach Software-Updates suchen

<!-- @require:software-update -->
<!-- @device:end -->
## Voraussetzungen

### Hardware

Dieses Playbook erfordert vier Ryzen AI Halo Einheiten und einen Ethernet-Switch, die in einer Stern-Topologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Menge | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Rechenknoten, die das Cluster bilden |
| 10-Gbit/s-Ethernet-Switch | 1 | Zentraler Switch für die Kommunikation mehrerer Ryzen AI Halo Knoten (mindestens 4 Ports) |
| Ethernet-Kabel | 4 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden vier Ethernet-Switch-Ports benötigt, um die vier Ryzen AI Halo Einheiten anzuschließen. Ein fünfter Port ist erforderlich, wenn Sie von einer separaten Client-Maschine aus statt von einer der Halo-Einheiten auf das Modell zugreifen.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Bitte installieren Sie:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) mit dem Workload **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Physischer Hardware-Aufbau

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen (Maschine 1 bis Maschine 4) durch.

Verbinden Sie jede Ryzen AI Halo Einheit über ein Cat-7-Kabel (oder höher) mit dem Ethernet-Switch. Dies stellt die 10-Gbit/s-Verbindung her, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.
<!-- @os:linux -->
### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (im Folgenden als `IFNAME` bezeichnet). Führen Sie aus:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dies gibt den Schnittstellennamen direkt aus, zum Beispiel:

```bash
enp191s0
```

### 2. Netzwerk-Verbindungsgeschwindigkeiten überprüfen

Bestätigen Sie, dass die Verbindung aktiv ist und mit voller Geschwindigkeit läuft, indem Sie die Geschwindigkeit Ihrer Schnittstelle überprüfen:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den ausgegebenen Schnittstellennamen aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

Sie sollten eine Geschwindigkeit von `10000Mb/s` sehen:

```bash
	Speed: 10000Mb/s
```

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10 Gbit/s eingestellt ist. Manche Switches erfordern, dass die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt wird; sehen Sie in der Dokumentation Ihres Switches nach.

<!-- @os:end -->

<!-- @os:windows -->
### Netzwerk-Verbindungsgeschwindigkeit überprüfen

Überprüfen Sie auf jeder Maschine die Verbindungsgeschwindigkeit Ihrer Netzwerkschnittstellen:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ihre Ethernet-Schnittstelle sollte `Up` sein und mit `10 Gbps` laufen:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10 Gbps` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10 Gbit/s eingestellt ist. Manche Switches erfordern, dass die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt wird; sehen Sie in der Dokumentation Ihres Switches nach.

<!-- @os:end -->

## llama.cpp installieren

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen (Maschine 1 bis Maschine 4) durch.

Es stehen zwei Installationsoptionen zur Verfügung:

- [Option 1: Lemonade SDK (Empfohlen)](#option-1-lemonade-sdk-recommended) - vorgefertigte Binärdateien, schnellste Einrichtung
- [Option 2: Manueller Build aus dem Quellcode](#option-2-manual-source-build) - Build aus dem Quellcode mit vollständiger Kontrolle über die Build-Flags

### Option 1: Lemonade SDK (Empfohlen)

Das Lemonade SDK bietet nächtliche Builds von llama.cpp mit AMD ROCm 7-Beschleunigung, die auf GPUs wie gfx1151 (Strix Halo / Ryzen AI Max+ 395) und andere aktuelle Radeon-Architekturen abzielen.

<!-- @os:windows -->
#### Schritt 1: Laden Sie die vorgefertigten Binärdateien herunter

Navigieren Sie zur Seite mit dem neuesten Release und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-windows-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Extrahieren Sie die Binärdateien

Entpacken Sie das heruntergeladene Archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli.exe`, `llama-server.exe` und `ggml-rpc-server.exe`, die für Ihr Ryzen AI Halo System vorkompiliert wurden.

#### Schritt 3: Überprüfen Sie die GPU-Erkennung

```bash
.\llama-cli.exe --list-devices
```

Erwartete Ausgabe:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Schritt 1: Laden Sie die vorgefertigten Binärdateien herunter

Navigieren Sie zur Seite mit dem neuesten Release und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Extrahieren und Vorbereiten der Binärdateien

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli`, `llama-server` und `rpc-server`, die für Ihr Ryzen AI Halo System vorkompiliert wurden.

#### Schritt 3: Überprüfen Sie die GPU-Erkennung

```bash
./llama-cli --list-devices
```

Erwartete Ausgabe:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie fort mit [Herunterladen des Modells](#downloading-the-model).

### Option 2: Manueller Build aus dem Quellcode

<!-- @os:windows -->
#### Schritt 1: Erstellen Sie llama.cpp

Öffnen Sie die **x64 Native Tools Command Prompt** (installiert mit Visual Studio Build Tools) und klonen Sie das Repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Fügen Sie HIP zu Ihrem Pfad hinzu und erstellen Sie den Build mit ROCm- und RPC-Unterstützung:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm/HIP-Software-Stack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteilte Inferenz |
| `-DGPU_TARGETS=gfx1151` | Zielt auf die Ryzen AI Halo GPU (Radeon 8060s) ab |
| `-G Ninja` | Verwendet das Ninja-Build-System |

#### Schritt 2: Überprüfen Sie die GPU-Erkennung

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Erwartete Ausgabe:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Schritt 3: Fügen Sie HIP zu Ihrem Benutzerpfad hinzu

Der obige Build-Schritt hat `%HIP_PATH%\bin` nur für die aktuelle Sitzung gesetzt. Damit die HIP-Bibliotheken in jedem beliebigen Terminal verfügbar sind (nicht nur in der x64 Native Tools Command Prompt), fügen Sie diesen dauerhaft zu Ihrem Benutzer-`PATH` hinzu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie fort mit [Herunterladen des Modells](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Schritt 1: Erstellen Sie llama.cpp

Klonen Sie das Repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Erstellen Sie den Build mit ROCm- und RPC-Unterstützung:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm-Software-Stack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteilte Inferenz |
| `-DAMDGPU_TARGETS="gfx1151"` | Zielt auf die Ryzen AI Halo GPU (Radeon 8060s) ab |

Weitere Build-Optionen finden Sie in der [llama.cpp-Build-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Schritt 2: Überprüfen Sie die GPU-Erkennung

```bash
cd rocm/bin
./llama-cli --list-devices
```

Erwartete Ausgabe:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie fort mit [Herunterladen des Modells](#downloading-the-model).
<!-- @os:end -->

## Herunterladen des Modells

Dieses Playbook verwendet [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) in der Quantisierung `UD-Q2_K_XL` von [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Diese Quantisierung passt in den kombinierten GPU-Speicher von vier Ryzen AI Halo Knoten.

Laden Sie die GGUF-Dateien mit der Hugging Face CLI herunter:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Hinweis**: Der Modell-Download muss auf Maschine 1 (dem Controller) abgeschlossen werden. Die RPC-Worker-Knoten (Maschinen 2, 3 und 4) benötigen keine lokale Kopie der Modelldateien.

## Starten des Modells auf dem Cluster

Die llama.cpp RPC (Remote Procedure Call) Engine ermöglicht es einer einzelnen llama.cpp-Instanz, Modellschichten über das Netzwerk an entfernte Worker auszulagern. Eine Maschine fungiert als **Controller** (Maschine 1) und übernimmt Tokenisierung, Scheduling und Orchestrierung. Die anderen drei Maschinen führen jeweils einen leichtgewichtigen **RPC-Server** (Maschinen 2, 3 und 4) aus, der ihren GPU-Speicher und ihre Rechenleistung dem Controller zur Verfügung stellt.

Beim Laden verteilt llama.cpp das Modell auf alle vier Knoten. Sobald es geladen ist, läuft die Inferenz so, als würde sie auf einem einzigen Beschleuniger ausgeführt. RPC übernimmt im Hintergrund die Tensorübertragungen und die Synchronisierung.

### Schritt 1: Starten Sie die RPC-Server (Maschinen 2, 3 und 4)

Starten Sie auf jeder der Maschinen 2, 3 und 4 den RPC-Server, um ihre GPU-Ressourcen dem Controller zur Verfügung zu stellen:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Zweck |
|------|---------|
| `-p` | Port, über den der RPC-Server bereitgestellt wird |
| `-c` | Aktiviert einen lokalen Cache für große Tensoren, um wiederholte Netzwerkübertragungen beim Laden des Modells zu vermeiden |
| `--host` | IP-Adresse, an die der RPC-Server gebunden wird (`0.0.0.0` für alle Schnittstellen) |

Weitere Optionen finden Sie in der [llama.cpp-RPC-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Schritt 2: Starten Sie das Modell (Maschine 1)

Wenn die RPC-Server auf den Maschinen 2, 3 und 4 laufen, starten Sie die Inferenz von Maschine 1 aus, entweder mit `llama-cli` oder `llama-server`.
#### llama-cli

`llama-cli` bietet eine terminalbasierte Oberfläche für die direkte Interaktion mit dem Modell. Es eignet sich ideal für Benchmarking, Debugging und Low-Level-Experimente.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` finden**: Führen Sie auf Machine 2, 3 und 4 jeweils `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` finden**: Führen Sie auf Machine 2, 3 und 4 jeweils `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu finden.

<!-- @os:end -->

Sobald `llama-cli` läuft, zeigt es den Fortschritt des Modell-Ladevorgangs an und öffnet eine interaktive Eingabeaufforderung, in der Sie direkt mit dem Modell chatten können:

![llama-cli mit Kimi K2.6 auf vier Knoten](assets/llama-cli-example.png)

#### llama-server

`llama-server` stellt dieselbe Inference-Engine über einen persistenten Serverprozess mit integrierter Web-UI und einer OpenAI-kompatiblen HTTP-API bereit. Dies ist die bevorzugte Schnittstelle für länger laufende Bereitstellungen, den Zugriff durch mehrere Benutzer und die Integration mit externen Tools.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` finden**: Führen Sie auf Machine 2, 3 und 4 jeweils `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **`<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>` finden**: Führen Sie auf Machine 2, 3 und 4 jeweils `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu finden.
<!-- @os:end -->

Öffnen Sie nach dem Start `http://<HOST_IP>:8081` in Ihrem Browser, um auf die integrierte Web-UI zuzugreifen. Diese bietet eine browserbasierte Chat-Oberfläche für die Interaktion mit dem Modell:

![llama-server Web-UI mit Kimi K2.6 auf vier Knoten](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` finden**: Führen Sie auf Machine 1 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` finden**: Führen Sie auf Machine 1 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu finden.
<!-- @os:end -->

#### Parameterreferenz

| Flag | Zweck |
|------|---------|
| `-m` | Pfad zur GGUF-Modelldatei (verwenden Sie den ersten Shard, `00001-of-00008`) |
| `-c` | Kontextgröße in Token. Größere Werte benötigen mehr Speicher |
| `-fa on` | Aktiviert rocWMMA Flash Attention für verbesserte Leistung auf AMD GPUs |
| `-ngl 999` | Lagert alle Modellschichten auf die GPU aus |
| `-lm none` | Setzt den Modell-Lademodus auf `none`, wodurch Memory-Mapping deaktiviert wird, um Ladezeiten zu verkürzen, wenn die Modellgröße den System-RAM übersteigt, aber in den VRAM passt |
| `-b` | Logische Batch-Größe in Token. Ein Wert von 4096 sorgt für ein ausgewogenes Verhältnis zwischen Durchsatz und Speichernutzung über die Knoten hinweg |
| `-ub` | Physische (Mikro-)Batch-Größe für die Prompt-Verarbeitung. Eine Übereinstimmung mit `-b` vermeidet unnötigen Chunking-Overhead |
| `--host` | IP, an die `llama-server` gebunden wird (nur `llama-server`) |
| `--port` | Port, über den die HTTP-API bereitgestellt wird (nur `llama-server`) |
| `--rpc` | Durch Kommas getrennte Liste von RPC-Worker-Endpunkten (`IP:port`) |

Die vollständige Parameterverwendung finden Sie in der [llama-cli-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) und der [llama-server-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nächste Schritte

- **Anwendungen von Drittanbietern verbinden**: `llama-server` stellt eine OpenAI-kompatible API bereit. Richten Sie eine beliebige OpenAI-kompatible Anwendung (z. B. Open WebUI) auf `http://<HOST_IP>:8081` mit einem beliebigen Platzhalter-API-Schlüssel (z. B. `none`) aus, um eine Verbindung zu Ihrem Cluster herzustellen
- **Weitere Modelle erkunden**: Durchsuchen Sie quantisierte GGUFs auf [Hugging Face](https://huggingface.co/models?search=gguf), um Modelle zu finden, die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Über vier Knoten hinaus skalieren**: Fügen Sie weitere Ryzen AI Halo-Systeme als zusätzliche RPC-Worker hinzu, um Modelle jenseits der Skala von 1 Billion Parametern nutzen zu können. Übergeben Sie zusätzliche Endpunkte an `--rpc` als durch Kommas getrennte Liste (z. B. `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)
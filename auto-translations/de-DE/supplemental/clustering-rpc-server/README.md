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

# Zwei Ryzen™ AI Halo-Systeme mit RPC clustern

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird. Dadurch erhalten Sie Zugriff auf noch größere Modelle mit stärkerem logischem Denken, besserer Code-Generierung und tieferem mehrsprachigem Verständnis – vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo-Systeme mit der RPC-Engine von llama.cpp clustern und GLM 4.7, ein Modell mit 358 Milliarden Parametern, mit AMD ROCm™-Beschleunigung auf beiden Maschinen ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo-Systemen erweitern
- Installation von llama.cpp mit ROCm- und RPC-Unterstützung
- Konfiguration eines RPC-Workers und Starten verteilter Inferenz über zwei Knoten
- Ausführen eines Modells mit 358 Milliarden Parametern auf zwei vernetzten Ryzen AI Halo-Systemen

## Festlegen der Speicherkonfiguration

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

<!-- @os:windows -->
Unter Windows müssen wir, um größere Modelle auszuführen, die mehr Speicher benötigen, die AMD Variable Graphics Memory (iGPU VRAM)-Zuweisung verwenden.

Dies kann erreicht werden, indem Sie das AMD Software: Adrenalin Edition-Kontrollzentrum öffnen und zu Folgendem navigieren: `Performance > Tuning > AMD Variable Graphics Memory`. Setzen Sie den Wert auf **96 GB**. Bitte starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Unter Linux nutzt ROCm einen gemeinsam genutzten Systemspeicher-Pool, der standardmäßig auf die Hälfte des Systemspeichers konfiguriert ist.

Diese Menge kann erhöht werden, indem die Seiteneinstellung (Page Setting) des Translation Table Manager (TTM) des Kernels mit den folgenden Anweisungen geändert wird. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS auf 0,5 GB einzustellen.

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für die von pipx installierten Wheels zum Systemsuchpfad hinzu.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installieren Sie das amd-debug-tools-Wheel von PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Führen Sie das amd-ttm-Tool aus, um die aktuellen Einstellungen für den gemeinsam genutzten Speicher abzufragen.
  ```bash
  amd-ttm
  ```

* Konfigurieren Sie die Einstellungen für den gemeinsam genutzten Speicher auf **120 GB** um:
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

Dieses Playbook erfordert zwei Ryzen AI Halo-Einheiten und einen Ethernet-Switch, die in einer Stern-Topologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Menge | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Rechenknoten, die den Cluster bilden |
| 10-Gbps-Ethernet-Switch | 1 | Zentraler Switch, um die Kommunikation zwischen mehreren Ryzen AI Halo-Knoten zu ermöglichen (mindestens 2 Anschlüsse) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden zwei Ethernet-Switch-Anschlüsse benötigt, um die beiden Ryzen AI Halo-Einheiten zu verbinden. Ein dritter Anschluss ist erforderlich, wenn Sie auf das Modell von einer separaten Client-Maschine aus zugreifen, anstatt von einer der Halo-Einheiten.

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

## Physische Hardware-Einrichtung

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Verbinden Sie jede Ryzen AI Halo-Einheit mit dem Ethernet-Switch über ein Cat 7 (oder höher) Kabel. Dadurch wird die 10-Gbps-Verbindung hergestellt, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.
<!-- @os:linux -->
### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (er wird im Folgenden als `IFNAME` bezeichnet). Führen Sie aus:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dies gibt den Namen der Schnittstelle direkt aus, zum Beispiel:

```bash
enp191s0
```

### 2. Netzwerkverbindungsgeschwindigkeiten überprüfen

Bestätigen Sie, dass die Verbindung aktiv ist und mit voller Geschwindigkeit läuft, indem Sie die Geschwindigkeit Ihrer Schnittstelle überprüfen:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den Namen der Ausgabeschnittstelle aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

Sie sollten eine Geschwindigkeit von `10000Mb/s` sehen:

```bash
	Speed: 10000Mb/s
```

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und bestätigen Sie, dass der Switch-Anschluss auf 10 Gbps eingestellt ist. Bei einigen Switches muss die automatische Aushandlung (Auto-Negotiation) deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie die Dokumentation Ihres Switches zurate.

<!-- @os:end -->

<!-- @os:windows -->
### Netzwerkverbindungsgeschwindigkeit überprüfen

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

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10 Gbps` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und bestätigen Sie, dass der Switch-Anschluss auf 10 Gbps eingestellt ist. Bei einigen Switches muss die automatische Aushandlung (Auto-Negotiation) deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie die Dokumentation Ihres Switches zurate.

<!-- @os:end -->

## llama.cpp installieren

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Es stehen zwei Installationsoptionen zur Verfügung:

- [Option 1: Lemonade SDK (Empfohlen)](#option-1-lemonade-sdk-recommended) – vorgefertigte Binärdateien, schnellste Einrichtung
- [Option 2: Manueller Build aus dem Quellcode](#option-2-manual-source-build) – Build aus dem Quellcode mit vollständiger Kontrolle über die Build-Flags

### Option 1: Lemonade SDK (Empfohlen)

Das Lemonade SDK bietet nächtliche Builds von llama.cpp mit AMD ROCm 7-Beschleunigung, die auf GPUs wie gfx1151 (Strix Halo / Ryzen AI Max+ 395) und andere aktuelle Radeon-Architekturen abzielen.

<!-- @os:windows -->
#### Schritt 1: Vorgefertigte Binärdateien herunterladen

Navigieren Sie zur neuesten Release-Seite und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-windows-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Binärdateien extrahieren

Entpacken Sie das heruntergeladene Archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli.exe`, `llama-server.exe` und `rpc-server.exe`, die für Ihr Ryzen AI Halo-System vorkompiliert wurden.

#### Schritt 3: GPU-Erkennung überprüfen

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
#### Schritt 1: Vorgefertigte Binärdateien herunterladen

Navigieren Sie zur neuesten Release-Seite und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Binärdateien extrahieren und vorbereiten

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli`, `llama-server` und `rpc-server`, die für Ihr Ryzen AI Halo-System vorkompiliert wurden.

#### Schritt 3: GPU-Erkennung überprüfen

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
Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Herunterladen des Modells](#downloading-the-model) fort.

### Option 2: Manueller Build aus dem Quellcode

<!-- @os:windows -->
#### Schritt 1: llama.cpp erstellen

Öffnen Sie die **x64 Native Tools Command Prompt** (mit Visual Studio Build Tools installiert) und klonen Sie das Repository:

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
| `-DGGML_HIP=ON` | Aktiviert den ROCm/HIP-Softwarestack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteilte Inferenz |
| `-DGPU_TARGETS=gfx1151` | Zielt auf die Ryzen AI Halo-GPU (Radeon 8060s) ab |
| `-G Ninja` | Verwendet das Ninja-Build-System |

#### Schritt 2: GPU-Erkennung überprüfen

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

#### Schritt 3: HIP zu Ihrem Benutzerpfad hinzufügen

Der obige Build-Schritt hat `%HIP_PATH%\bin` nur für die aktuelle Sitzung festgelegt. Damit die HIP-Bibliotheken in jedem Terminal verfügbar sind (nicht nur in der x64 Native Tools Command Prompt), fügen Sie es dauerhaft zu Ihrem Benutzer-`PATH` hinzu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Herunterladen des Modells](#downloading-the-model) fort.
<!-- @os:end -->

<!-- @os:linux -->
#### Schritt 1: llama.cpp erstellen

Klonen Sie das Repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Erstellen Sie den Build mit ROCm- und RPC-Unterstützung:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm-Softwarestack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteilte Inferenz |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiviert rocWMMA für erweiterte Flash Attention auf AMD-GPUs |
| `-DAMDGPU_TARGETS="gfx1151"` | Zielt auf die Ryzen AI Halo-GPU (Radeon 8060s) ab |

Weitere Build-Optionen finden Sie in der [llama.cpp-Build-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Schritt 2: GPU-Erkennung überprüfen

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

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Herunterladen des Modells](#downloading-the-model) fort.
<!-- @os:end -->

## Herunterladen des Modells

Dieses Playbook verwendet [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ein Modell mit 358 Milliarden Parametern in der `Q4_K_XL`-Quantisierung von [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bei dieser Quantisierung benötigt das Modell etwa 205 GB Speicherplatz und passt in den kombinierten GPU-Speicher von zwei Ryzen AI Halo-Knoten.

Laden Sie die GGUF-Dateien mit der Hugging Face CLI herunter:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Hinweis**: Der Modell-Download muss auf Machine 1 (dem Controller) abgeschlossen werden. Die RPC-Worker-Knoten benötigen keine lokale Kopie der Modelldateien.

## Starten des Modells im Cluster

Die llama.cpp RPC-Engine (Remote Procedure Call) ermöglicht es einer einzelnen llama.cpp-Instanz, Modellschichten über das Netzwerk an entfernte Worker auszulagern. Eine Maschine fungiert als **Controller** (Machine 1) und übernimmt Tokenisierung, Scheduling und Orchestrierung. Die andere Maschine führt einen leichtgewichtigen **RPC-Server** (Machine 2) aus, der ihren GPU-Speicher und ihre Rechenleistung dem Controller zur Verfügung stellt.

Beim Laden verteilt llama.cpp das Modell auf beide Knoten. Sobald das Modell geladen ist, läuft die Inferenz so, als würde sie auf einem einzigen Beschleuniger ausgeführt. RPC übernimmt im Hintergrund die Tensor-Übertragungen und die Synchronisierung.

### Schritt 1: RPC-Server starten (Machine 2)

Starten Sie auf Machine 2 den RPC-Server, um seine GPU-Ressourcen dem Controller zur Verfügung zu stellen:
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

### Schritt 2: Modell starten (Machine 1)

Sobald der RPC-Server auf Machine 2 läuft, starten Sie die Inferenz von Machine 1 aus mit `llama-cli` oder `llama-server`.

#### llama-cli

`llama-cli` bietet eine terminalbasierte Schnittstelle zur direkten Interaktion mit dem Modell. Es eignet sich ideal für Benchmarking, Debugging und Experimente auf niedriger Ebene.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 `hostname -I | awk '{print $1}'` aus, um dessen lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 im Terminal (Powershell) `ipconfig | findstr /C:"IPv4"` aus, um dessen lokale IP-Adresse zu finden.

<!-- @os:end -->

Sobald es läuft, zeigt `llama-cli` den Fortschritt beim Laden des Modells an und öffnet eine interaktive Eingabeaufforderung, in der Sie direkt mit dem Modell chatten können:

![llama-cli führt GLM 4.7 auf zwei Knoten aus](assets/llama-cli-example.png)
#### llama-server

`llama-server` stellt dieselbe Inferenz-Engine über einen dauerhaften Serverprozess mit integrierter Web-UI und einer OpenAI-kompatiblen HTTP-API bereit. Dies ist die bevorzugte Schnittstelle für länger laufende Bereitstellungen, den Zugriff durch mehrere Benutzer und die Integration mit externen Tools.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Maschine 2 `hostname -I | awk '{print $1}'` aus, um deren lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Maschine 2 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um deren lokale IP-Adresse zu finden.
<!-- @os:end -->

Öffnen Sie nach dem Start `http://<HOST_IP>:8081` in Ihrem Browser, um auf die integrierte Web-UI zuzugreifen. Diese bietet eine browserbasierte Chat-Oberfläche zur Interaktion mit dem Modell:

![llama-server-Web-UI mit GLM 4.7 über zwei Knoten](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` finden**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um deren lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` finden**: Führen Sie auf Maschine 1 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um deren lokale IP-Adresse zu finden.
<!-- @os:end -->

#### Parameterreferenz

| Flag | Zweck |
|------|---------|
| `-m` | Pfad zur GGUF-Modelldatei (verwenden Sie den ersten Shard, `00001-of-00005`) |
| `-c` | Kontextgröße in Token. Größere Werte benötigen mehr Speicher |
| `-fa on` | Aktiviert rocWMMA Flash Attention für verbesserte Leistung auf AMD-GPUs |
| `-ngl 999` | Lagert alle Modellschichten auf die GPU aus |
| `--no-mmap` | Deaktiviert Memory-Mapping, wodurch die Ladezeiten verkürzt werden, wenn die Modellgröße den System-RAM überschreitet, aber in den VRAM passt |
| `--host` | IP, an die `llama-server` gebunden wird (nur `llama-server`) |
| `--port` | Port, über den die HTTP-API bereitgestellt wird (nur `llama-server`) |
| `--rpc` | Kommagetrennte Liste von RPC-Worker-Endpunkten (`IP:port`) |

Die vollständige Parameterverwendung finden Sie in der [llama-cli-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) und der [llama-server-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nächste Schritte

- **Anwendungen von Drittanbietern verbinden**: `llama-server` stellt eine OpenAI-kompatible API bereit. Richten Sie eine beliebige OpenAI-kompatible Anwendung (z. B. Open WebUI) auf `http://<HOST_IP>:8081` mit einem beliebigen Platzhalter-API-Schlüssel (z. B. `none`) aus, um sich mit Ihrem Cluster zu verbinden
- **Weitere Modelle erkunden**: Durchsuchen Sie quantisierte GGUFs auf [Hugging Face](https://huggingface.co/models?search=gguf), um Modelle zu finden, die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Knoten skalieren**: Fügen Sie zwei weitere Ryzen AI Halo Systeme als zusätzliche RPC-Worker hinzu, um auf Modelle im Bereich von 1 Billion Parametern zuzugreifen. Übergeben Sie zusätzliche Endpunkte an `--rpc` als kommagetrennte Liste (z. B. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
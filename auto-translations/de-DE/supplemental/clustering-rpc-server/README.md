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

# Clustern von zwei Ryzen™ AI Halo-Systemen mit RPC

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird. So erhalten Sie Zugriff auf noch größere Modelle mit stärkerem logischem Denkvermögen, besserer Codegenerierung und tieferem mehrsprachigem Verständnis – vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo-Systeme mithilfe der RPC-Engine von llama.cpp clustern und GLM 4.7, ein Modell mit 358 Milliarden Parametern, auf beiden Maschinen mit AMD ROCm™-Beschleunigung ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo-Systemen erweitern
- Installation von llama.cpp mit ROCm- und RPC-Unterstützung
- Konfiguration eines RPC-Workers und Starten verteilter Inferenz über zwei Knoten
- Ausführen eines Modells mit 358 Milliarden Parametern auf zwei vernetzten Ryzen AI Halo-Systemen

## Einrichten der Speicherkonfiguration

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

<!-- @os:windows -->
Unter Windows müssen wir zum Ausführen größerer Modelle, die mehr Speicher benötigen, die AMD Variable Graphics Memory-Zuweisung (iGPU-VRAM) verwenden.

Dies kann erfolgen, indem Sie das Bedienfeld AMD Software: Adrenalin Edition öffnen und zu `Performance > Tuning > AMD Variable Graphics Memory` navigieren. Setzen Sie den Wert auf **96 GB**. Bitte starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Unter Linux verwendet ROCm einen gemeinsam genutzten Systemspeicherpool, der standardmäßig auf die Hälfte des Systemspeichers konfiguriert ist.

Dieser Wert kann erhöht werden, indem die Seiteneinstellung des Translation Table Manager (TTM) des Kernels wie folgt geändert wird. AMD empfiehlt, im BIOS den minimalen dedizierten VRAM (0,5 GB) einzustellen.

* Installieren Sie das Dienstprogramm pipx und fügen Sie den Pfad für die von pipx installierten Wheels dem Systemsuchpfad hinzu.

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
| Ryzen AI Halo | 2 | Recheneinheiten, die den Cluster bilden |
| 10Gbps-Ethernet-Switch | 1 | Zentraler Switch, der die Kommunikation zwischen mehreren Ryzen AI Halo-Knoten ermöglicht (mindestens 2 Ports) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden zwei Ethernet-Switch-Ports benötigt, um die beiden Ryzen AI Halo-Einheiten zu verbinden. Ein dritter Port ist erforderlich, wenn Sie auf das Modell von einem separaten Client-Rechner aus zugreifen, anstatt von einer der Halo-Einheiten aus.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Bitte installieren Sie:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) mit der Arbeitsauslastung **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Einrichten der physischen Hardware

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Verbinden Sie jede Ryzen AI Halo-Einheit mit einem Cat 7 (oder höheren) Kabel mit dem Ethernet-Switch. Damit wird die 10Gbps-Verbindung für die Hochgeschwindigkeitskommunikation zwischen den Knoten hergestellt.
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

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10Gbps eingestellt ist. Bei manchen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie hierzu die Dokumentation Ihres Switches zurate.

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

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10 Gbps` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10Gbps eingestellt ist. Bei manchen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie hierzu die Dokumentation Ihres Switches zurate.

<!-- @os:end -->

## Installieren von llama.cpp

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Es stehen zwei Installationsoptionen zur Verfügung:

- [Option 1: Lemonade SDK (Empfohlen)](#option-1-lemonade-sdk-recommended) - vorgefertigte Binärdateien, schnellste Einrichtung
- [Option 2: Manueller Quell-Build](#option-2-manual-source-build) - Build aus dem Quellcode mit voller Kontrolle über die Build-Flags

### Option 1: Lemonade SDK (Empfohlen)

Das Lemonade SDK bietet nächtliche Builds von llama.cpp mit AMD ROCm 7-Beschleunigung, die auf GPUs wie gfx1151 (Strix Halo / Ryzen AI Max+ 395) und andere aktuelle Radeon-Architekturen abzielen.

<!-- @os:windows -->
#### Step 1: Download der vorkompilierten Binärdateien

Rufen Sie die Seite mit dem neuesten Release auf und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-windows-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Step 2: Extrahieren der Binärdateien

Entpacken Sie das heruntergeladene Archiv:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli.exe`, `llama-server.exe` und `rpc-server.exe`, vorkompiliert für Ihr Ryzen AI Halo-System.

#### Step 3: Überprüfen der GPU-Erkennung

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
#### Step 1: Download der vorkompilierten Binärdateien

Rufen Sie die Seite mit dem neuesten Release auf und laden Sie das Archiv herunter, das zu Ihrer Plattform und Ihrem GPU-Ziel passt:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Step 2: Extrahieren und Vorbereiten der Binärdateien

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Dieses Verzeichnis enthält nun ROCm-fähige Builds von `llama-cli`, `llama-server` und `rpc-server`, vorkompiliert für Ihr Ryzen AI Halo-System.

#### Step 3: Überprüfen der GPU-Erkennung

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
Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Downloading the Model](#downloading-the-model) fort.

### Option 2: Manueller Build aus dem Quellcode

<!-- @os:windows -->
#### Step 1: Build von llama.cpp

Öffnen Sie die **x64 Native Tools Command Prompt** (mit Visual Studio Build Tools installiert) und klonen Sie das Repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Fügen Sie HIP zu Ihrem Pfad hinzu und bauen Sie mit ROCm- und RPC-Unterstützung:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm/HIP-Software-Stack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteiltes Inferencing |
| `-DGPU_TARGETS=gfx1151` | Zielt auf die Ryzen AI Halo GPU (Radeon 8060s) ab |
| `-G Ninja` | Verwendet das Ninja-Build-System |

#### Step 2: Überprüfen der GPU-Erkennung

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

#### Step 3: HIP zu Ihrem Benutzerpfad hinzufügen

Der obige Build-Schritt hat `%HIP_PATH%\bin` nur für die aktuelle Sitzung gesetzt. Damit die HIP-Bibliotheken in jedem Terminal verfügbar sind (nicht nur in der x64 Native Tools Command Prompt), fügen Sie ihn dauerhaft zu Ihrem Benutzer-`PATH` hinzu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Downloading the Model](#downloading-the-model) fort.
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Build von llama.cpp

Klonen Sie das Repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Bauen Sie mit ROCm- und RPC-Unterstützung:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm-Software-Stack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteiltes Inferencing |
| `-DAMDGPU_TARGETS="gfx1151"` | Zielt auf die Ryzen AI Halo GPU (Radeon 8060s) ab |

Weitere Build-Optionen finden Sie in der [llama.cpp-Build-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Überprüfen der GPU-Erkennung

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

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Downloading the Model](#downloading-the-model) fort.
<!-- @os:end -->

## Herunterladen des Modells

Dieses Playbook verwendet [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ein Modell mit 358 Milliarden Parametern in der Quantisierung `Q4_K_XL` von [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bei dieser Quantisierung benötigt das Modell etwa 205 GB Speicherplatz und passt in den kombinierten GPU-Speicher von zwei Ryzen AI Halo-Knoten.

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

> **Hinweis**: Der Modell-Download muss auf Maschine 1 (dem Controller) abgeschlossen werden. Die RPC-Worker-Knoten benötigen keine lokale Kopie der Modelldateien.

## Starten des Modells im Cluster

Die llama.cpp RPC-Engine (Remote Procedure Call) ermöglicht es einer einzelnen llama.cpp-Instanz, Modellschichten über das Netzwerk an entfernte Worker auszulagern. Eine Maschine fungiert als **Controller** (Maschine 1) und übernimmt Tokenisierung, Scheduling und Orchestrierung. Die andere Maschine führt einen schlanken **RPC-Server** aus (Maschine 2), der ihren GPU-Speicher und ihre Rechenleistung dem Controller zur Verfügung stellt.

Beim Laden verteilt llama.cpp das Modell (Sharding) auf beide Knoten. Sobald das Modell geladen ist, läuft die Inferenz so ab, als würde sie auf einem einzigen Beschleuniger ausgeführt. RPC übernimmt im Hintergrund die Tensor-Übertragungen und die Synchronisierung.

### Step 1: Starten des RPC-Servers (Maschine 2)

Starten Sie auf Maschine 2 den RPC-Server, um dessen GPU-Ressourcen dem Controller zur Verfügung zu stellen:
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

### Step 2: Starten des Modells (Maschine 1)

Nachdem der RPC-Server auf Maschine 2 läuft, starten Sie die Inferenz von Maschine 1 aus, entweder mit `llama-cli` oder `llama-server`.

#### llama-cli

`llama-cli` bietet eine terminalbasierte Oberfläche für die direkte Interaktion mit dem Modell. Es eignet sich hervorragend für Benchmarking, Debugging und Low-Level-Experimente.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **Ermitteln von `<RPC_WORKER_IP>`**: Führen Sie auf Maschine 2 `hostname -I | awk '{print $1}'` aus, um deren lokale IP-Adresse zu ermitteln.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Ermitteln von `<RPC_WORKER_IP>`**: Führen Sie auf Maschine 2 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um deren lokale IP-Adresse zu ermitteln.

<!-- @os:end -->

Sobald der Vorgang läuft, zeigt `llama-cli` den Fortschritt des Modellladens an und öffnet eine interaktive Eingabeaufforderung, über die Sie direkt mit dem Modell chatten können:

![llama-cli führt GLM 4.7 auf zwei Knoten aus](assets/llama-cli-example.png)
#### llama-server

`llama-server` stellt dieselbe Inferenz-Engine über einen dauerhaften Serverprozess mit integrierter Web-UI und einer OpenAI-kompatiblen HTTP-API bereit. Dies ist die bevorzugte Schnittstelle für länger laufende Bereitstellungen, Zugriff durch mehrere Benutzer und die Integration mit externen Tools.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Maschine 2 den Befehl `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **Hinweis**: Führen Sie diesen Befehl im Terminal (Powershell) aus.

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Maschine 2 den Befehl `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um ihre lokale IP-Adresse zu finden.
<!-- @os:end -->

Öffnen Sie nach dem Start `http://<HOST_IP>:8081` in Ihrem Browser, um auf die integrierte Web-UI zuzugreifen. Diese bietet eine browserbasierte Chat-Oberfläche für die Interaktion mit dem Modell:

![llama-server-Web-UI mit GLM 4.7 auf zwei Knoten](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` finden**: Führen Sie auf Maschine 1 den Befehl `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` finden**: Führen Sie auf Maschine 1 den Befehl `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um ihre lokale IP-Adresse zu finden.
<!-- @os:end -->

#### Parameterreferenz

| Flag | Zweck |
|------|---------|
| `-m` | Pfad zur GGUF-Modelldatei (verwenden Sie das erste Shard, `00001-of-00005`) |
| `-c` | Kontextgröße in Tokens. Größere Werte benötigen mehr Speicher |
| `-fa on` | Aktiviert rocWMMA Flash Attention für verbesserte Leistung auf AMD GPUs |
| `-ngl 999` | Lagert alle Modell-Layer auf die GPU aus |
| `-lm none` | Setzt den Modell-Lademodus auf `none`, wodurch Memory-Mapping deaktiviert wird, um Ladezeiten zu verkürzen, wenn die Modellgröße den System-RAM übersteigt, aber in den VRAM passt |
| `--host` | IP, an die `llama-server` gebunden wird (nur `llama-server`) |
| `--port` | Port, über den die HTTP-API bereitgestellt wird (nur `llama-server`) |
| `--rpc` | Kommagetrennte Liste von RPC-Worker-Endpunkten (`IP:port`) |

Die vollständige Parameterverwendung finden Sie in der [llama-cli-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) und der [llama-server-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nächste Schritte

- **Anwendungen von Drittanbietern verbinden**: `llama-server` stellt eine OpenAI-kompatible API bereit. Richten Sie eine beliebige OpenAI-kompatible Anwendung (z. B. Open WebUI) auf `http://<HOST_IP>:8081` mit einem beliebigen Platzhalter-API-Schlüssel (z. B. `none`), um eine Verbindung zu Ihrem Cluster herzustellen
- **Weitere Modelle erkunden**: Durchsuchen Sie quantisierte GGUFs auf [Hugging Face](https://huggingface.co/models?search=gguf), um Modelle zu finden, die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Knoten skalieren**: Fügen Sie zwei weitere Ryzen AI Halo-Systeme als zusätzliche RPC-Worker hinzu, um Zugriff auf Modelle in der Größenordnung von 1 Billion Parametern zu erhalten. Übergeben Sie zusätzliche Endpunkte an `--rpc` als kommagetrennte Liste (z. B. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
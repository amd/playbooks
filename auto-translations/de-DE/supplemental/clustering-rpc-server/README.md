<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering Two Ryzen™ AI Halos with RPC

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird und Ihnen so Zugang zu noch größeren Modellen mit stärkerer Reasoning-Fähigkeit, besserer Code-Generierung und tieferem mehrsprachigem Verständnis bietet – alles vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo-Systeme mithilfe der RPC-Engine von llama.cpp zu einem Cluster zusammenschließen und GLM 4.7, ein Modell mit 358 Milliarden Parametern, mit AMD ROCm™-Beschleunigung über beide Maschinen hinweg ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo-Systemen erweitern
- Installation von llama.cpp mit ROCm- und RPC-Unterstützung
- Konfiguration eines RPC-Workers und Start von verteilter Inferenz über zwei Knoten
- Ausführung eines Modells mit 358 Milliarden Parametern über zwei vernetzte Ryzen AI Halo-Systeme

## Speicherkonfiguration festlegen

> **Hinweis**: Führen Sie diesen Schritt auf beiden Maschinen (Machine 1 und Machine 2) durch.

<!-- @os:windows -->
Unter Windows müssen wir zur Ausführung größerer Modelle, die mehr Speicher benötigen, die AMD Variable Graphics Memory (iGPU VRAM)-Zuweisung verwenden.

Dies kann durch Öffnen des AMD Software: Adrenalin Edition-Bedienfelds und Navigation zu `Performance > Tuning > AMD Variable Graphics Memory` erfolgen. Setzen Sie den Wert auf **96 GB**. Bitte starten Sie das System neu, damit die Änderungen wirksam werden.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
Unter Linux verwendet ROCm einen gemeinsamen Systemspeicherpool, der standardmäßig auf die Hälfte des Systemspeichers konfiguriert ist.

Diese Menge kann durch Änderung der Translation Table Manager (TTM)-Seiteneinstellung des Kernels erhöht werden. Folgen Sie dazu den nachstehenden Anweisungen. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS festzulegen (0,5 GB).

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für von pipx installierte Wheels zum Systemsuchpfad hinzu.

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

* Konfigurieren Sie die gemeinsamen Speichereinstellungen auf **120 GB** neu:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.


<!-- @os:end -->
<!-- @device:halo_box -->
## Auf Software-Updates prüfen

<!-- @require:software-update -->
<!-- @device:end -->
## Voraussetzungen

### Hardware

Dieses Playbook erfordert zwei Ryzen AI Halo-Einheiten und einen Ethernet-Switch, die in einer Sterntopologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Anzahl | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Rechenknoten, die den Cluster bilden |
| 10-Gbps-Ethernet-Switch | 1 | Zentraler Switch für die Kommunikation zwischen mehreren Ryzen AI Halo-Knoten (mindestens 2 Ports) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Zwei Ethernet-Switch-Ports werden benötigt, um die beiden Ryzen AI Halo-Einheiten zu verbinden. Ein dritter Port ist erforderlich, wenn Sie auf das Modell von einem separaten Client-Rechner aus zugreifen, anstatt von einer der Halo-Einheiten.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Bitte installieren Sie:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) mit der Workload **Desktop-Entwicklung mit C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Physischer Hardware-Aufbau

> **Hinweis**: Führen Sie diesen Schritt auf beiden Maschinen (Machine 1 und Machine 2) durch.

Verbinden Sie jede Ryzen AI Halo-Einheit mit einem Cat-7-Kabel (oder höher) mit dem Ethernet-Switch. Dadurch wird die 10-Gbps-Verbindung hergestellt, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.
<!-- @os:linux -->
### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (er wird nachfolgend als `IFNAME` bezeichnet). Führen Sie aus:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Dies gibt den Schnittstellennamen direkt aus, zum Beispiel:

```bash
enp191s0
```

### 2. Netzwerkverbindungsgeschwindigkeiten überprüfen

Bestätigen Sie, dass die Verbindung aktiv ist und mit voller Geschwindigkeit läuft, indem Sie die Geschwindigkeit Ihrer Schnittstelle prüfen:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den ausgegebenen Schnittstellennamen aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

Sie sollten eine Geschwindigkeit von `10000Mb/s` sehen:

```bash
	Speed: 10000Mb/s
```

> **Hinweis**: Wenn die Geschwindigkeit unter `10000Mb/s` liegt oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10 Gbps eingestellt ist. Bei einigen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell festgelegt werden; lesen Sie dazu die Dokumentation Ihres Switches.

<!-- @os:end -->

<!-- @os:windows -->
### Netzwerkverbindungsgeschwindigkeit überprüfen

Überprüfen Sie auf jeder Maschine die Verbindungsgeschwindigkeit Ihrer Netzwerkschnittstellen:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Ihre Ethernet-Schnittstelle sollte `Up` und mit `10 Gbps` laufen:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Hinweis**: Wenn die Geschwindigkeit unter `10 Gbps` liegt oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10 Gbps eingestellt ist. Bei einigen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell festgelegt werden; lesen Sie dazu die Dokumentation Ihres Switches.

<!-- @os:end -->

## llama.cpp installieren

> **Hinweis**: Führen Sie diesen Schritt auf beiden Maschinen (Machine 1 und Machine 2) durch.

Es stehen zwei Installationsoptionen zur Verfügung:

- [Option 1: Lemonade SDK (Empfohlen)](#option-1-lemonade-sdk-recommended) – vorgefertigte Binärdateien, schnellste Einrichtung
- [Option 2: Manueller Quell-Build](#option-2-manual-source-build) – aus dem Quellcode erstellen mit voller Kontrolle über Build-Flags

### Option 1: Lemonade SDK (Empfohlen)

Das Lemonade SDK stellt nächtliche Builds von llama.cpp mit AMD ROCm 7-Beschleunigung bereit, die auf GPUs wie gfx1151 (Strix Halo / Ryzen AI Max+ 395) und andere aktuelle Radeon-Architekturen abzielen.

<!-- @os:windows -->
#### Schritt 1: Vorgefertigte Binärdateien herunterladen

Navigieren Sie zur neuesten Release-Seite und laden Sie das Archiv herunter, das Ihrer Plattform und Ihrem GPU-Ziel entspricht:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-windows-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Binärdateien entpacken

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

Navigieren Sie zur neuesten Release-Seite und laden Sie das Archiv herunter, das Ihrer Plattform und Ihrem GPU-Ziel entspricht:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Laden Sie die Datei mit dem Namen `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` herunter (wobei `xxxx` die Build-Nummer ist).

#### Schritt 2: Binärdateien entpacken und vorbereiten

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
Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Modell herunterladen](#downloading-the-model) fort.

### Option 2: Manueller Quell-Build

<!-- @os:windows -->
#### Schritt 1: llama.cpp erstellen

Öffnen Sie die **x64 Native Tools-Eingabeaufforderung** (installiert mit Visual Studio Build Tools) und klonen Sie das Repository:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Fügen Sie HIP zu Ihrem Pfad hinzu und erstellen Sie mit ROCm- und RPC-Unterstützung:

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

#### Schritt 3: HIP zum Benutzerpfad hinzufügen

Der obige Build-Schritt hat `%HIP_PATH%\bin` nur für die aktuelle Sitzung gesetzt. Um die HIP-Bibliotheken in jedem Terminal verfügbar zu machen (nicht nur in der x64 Native Tools-Eingabeaufforderung), fügen Sie es dauerhaft zu Ihrem Benutzer-`PATH` hinzu:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Modell herunterladen](#downloading-the-model) fort.
<!-- @os:end -->

<!-- @os:linux -->
#### Schritt 1: llama.cpp erstellen

Klonen Sie das Repository:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Erstellen Sie mit ROCm- und RPC-Unterstützung:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Build-Flag | Zweck |
|-----------|---------|
| `-DGGML_HIP=ON` | Aktiviert den ROCm-Software-Stack |
| `-DGGML_RPC=ON` | Aktiviert RPC für verteilte Inferenz |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | Aktiviert rocWMMA für verbesserte Flash Attention auf AMD GPUs |
| `-DAMDGPU_TARGETS="gfx1151"` | Zielt auf die Ryzen AI Halo GPU (Radeon 8060s) ab |

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

Nachdem llama.cpp auf jedem Knoten vorbereitet wurde, fahren Sie mit [Modell herunterladen](#downloading-the-model) fort.
<!-- @os:end -->

## Modell herunterladen

Dieses Playbook verwendet [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), ein Modell mit 358 Milliarden Parametern in der `Q4_K_XL`-Quantisierung von [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Bei dieser Quantisierung benötigt das Modell ungefähr 205 GB Speicherplatz und passt in den kombinierten GPU-Speicher zweier Ryzen AI Halo-Knoten.

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

## Modell im Cluster starten

Die RPC-Engine (Remote Procedure Call) von llama.cpp ermöglicht es einer einzelnen llama.cpp-Instanz, Modellschichten über das Netzwerk an entfernte Worker auszulagern. Eine Maschine fungiert als **Controller** (Machine 1) und übernimmt Tokenisierung, Scheduling und Orchestrierung. Die andere Maschine betreibt einen leichtgewichtigen **RPC-Server** (Machine 2), der seinen GPU-Speicher und seine Rechenleistung dem Controller zur Verfügung stellt.

Beim Laden teilt llama.cpp das Modell auf beide Knoten auf. Sobald es geladen ist, läuft die Inferenz so ab, als würde sie auf einem einzigen Beschleuniger ausgeführt. RPC übernimmt Tensor-Transfers und Synchronisation im Hintergrund.

### Schritt 1: RPC-Server starten (Machine 2)

Starten Sie auf Machine 2 den RPC-Server, um dessen GPU-Ressourcen dem Controller zur Verfügung zu stellen:
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Zweck |
|------|---------|
| `-p` | Port, auf dem der RPC-Server sendet |
| `-c` | Aktiviert einen lokalen Cache für große Tensoren und vermeidet so wiederholte Netzwerkübertragungen beim Laden des Modells |
| `--host` | IP-Adresse, an die der RPC-Server gebunden wird (`0.0.0.0` für alle Schnittstellen) |

Weitere Optionen finden Sie in der [llama.cpp RPC-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Schritt 2: Modell starten (Machine 1)

Wenn der RPC-Server auf Machine 2 läuft, starten Sie die Inferenz von Machine 1 aus, entweder mit `llama-cli` oder `llama-server`.

#### llama-cli

`llama-cli` bietet eine terminalbasierte Schnittstelle für die direkte Interaktion mit dem Modell. Es eignet sich ideal für Benchmarking, Debugging und Low-Level-Experimente.

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

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln.
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

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu ermitteln.

<!-- @os:end -->

Sobald es läuft, zeigt `llama-cli` den Fortschritt beim Laden des Modells an und wechselt in eine interaktive Eingabeaufforderung, über die Sie direkt mit dem Modell chatten können:

![llama-cli, das GLM 4.7 über zwei Knoten ausführt](assets/llama-cli-example.png)

#### llama-server

`llama-server` stellt dieselbe Inferenz-Engine über einen dauerhaften Serverprozess mit einer integrierten Web-UI und einer OpenAI-kompatiblen HTTP-API bereit. Dies ist die bevorzugte Schnittstelle für länger laufende Deployments, Mehrbenutzerzugriff und die Integration mit externen Tools.

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

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln.
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

> **`<RPC_WORKER_IP>` finden**: Führen Sie auf Machine 2 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu ermitteln.
<!-- @os:end -->

Öffnen Sie nach dem Start `http://<HOST_IP>:8081` in Ihrem Browser, um auf die integrierte Web-UI zuzugreifen. Diese bietet eine browserbasierte Chat-Oberfläche für die Interaktion mit dem Modell:

![llama-server Web-UI, das GLM 4.7 über zwei Knoten ausführt](assets/llama-server-example.png)

<!-- @os:linux -->
> **`<HOST_IP>` finden**: Führen Sie auf Machine 1 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln.
<!-- @os:end -->

<!-- @os:windows -->
> **`<HOST_IP>` finden**: Führen Sie auf Machine 1 `ipconfig | findstr /C:"IPv4"` im Terminal (Powershell) aus, um die lokale IP-Adresse zu ermitteln.
<!-- @os:end -->

#### Parameter-Referenz

| Flag | Zweck |
|------|---------|
| `-m` | Pfad zur GGUF-Modelldatei (verwenden Sie den ersten Shard, `00001-of-00005`) |
| `-c` | Kontextgröße in Tokens. Größere Werte verbrauchen mehr Speicher |
| `-fa on` | Aktiviert rocWMMA Flash Attention für verbesserte Leistung auf AMD GPUs |
| `-ngl 999` | Lagert alle Modellschichten auf die GPU aus |
| `--no-mmap` | Deaktiviert Memory-Mapping und reduziert so die Ladezeiten, wenn die Modellgröße den Systemspeicher überschreitet, aber in den VRAM passt |
| `--host` | IP, an die `llama-server` gebunden wird (nur `llama-server`) |
| `--port` | Port, auf dem die HTTP-API bereitgestellt wird (nur `llama-server`) |
| `--rpc` | Kommagetrennte Liste von RPC-Worker-Endpunkten (`IP:Port`) |

Die vollständige Parameterverwendung finden Sie in der [llama-cli-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) und der [llama-server-Dokumentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Nächste Schritte

- **Drittanbieter-Anwendungen verbinden**: `llama-server` stellt eine OpenAI-kompatible API bereit. Richten Sie jede OpenAI-kompatible Anwendung (wie Open WebUI) auf `http://<HOST_IP>:8081` mit einem beliebigen Platzhalter-API-Schlüssel (z. B. `none`) aus, um eine Verbindung zu Ihrem Cluster herzustellen
- **Andere Modelle erkunden**: Durchsuchen Sie quantisierte GGUFs auf [Hugging Face](https://huggingface.co/models?search=gguf), um Modelle zu finden, die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Knoten skalieren**: Fügen Sie zwei weitere Ryzen AI Halo-Systeme als zusätzliche RPC-Worker hinzu, um auf Modelle im Bereich von einer Billion Parametern zugreifen zu können. Übergeben Sie weitere Endpunkte an `--rpc` als kommagetrennte Liste (z. B. `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
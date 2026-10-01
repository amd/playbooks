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

# Clustern von zwei Ryzen™ AI Halos mit RCCL

## Überblick

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk zusammengeführt wird, sodass Sie Zugriff auf noch größere Modelle mit stärkerem logischem Denkvermögen, besserer Codegenerierung und tieferem mehrsprachigem Verständnis erhalten – vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo Systeme mit RCCL (ROCm Communication Collectives Library) und vLLM clustern und Qwen3.5-397B, ein Modell mit 397 Milliarden Parametern, mit ROCm-Beschleunigung auf beiden Rechnern gemeinsam ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo Systemen erweitern
- Starten von vLLM mit ROCm-Unterstützung
- Konfigurieren von RCCL für Multi-Node-Tensor-parallele Inferenz über zwei Ryzen AI Halo Systeme hinweg
- Ausführen eines Modells mit 397 Milliarden Parametern über zwei vernetzte Ryzen AI Halo Systeme

## Voraussetzungen

### Hardware

Dieses Playbook erfordert zwei Ryzen AI Halo Einheiten und einen Ethernet-Switch, die in einer Stern-Topologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Menge | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Rechenknoten, die den Cluster bilden |
| 10-Gbps-Ethernet-Switch | 1 | Zentraler Switch, um die Kommunikation mehrerer Ryzen AI Halo Knoten zu ermöglichen (mindestens 2 Ports) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden zwei Ethernet-Switch-Ports benötigt, um die beiden Ryzen AI Halo Einheiten zu verbinden. Ein dritter Port wird benötigt, wenn Sie auf das Modell von einem separaten Client-Rechner aus zugreifen, anstatt von einer der Halo-Einheiten aus.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Einrichtung der physischen Hardware

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Rechner 1 als auch auf Rechner 2 aus.

Verbinden Sie jede Ryzen AI Halo Einheit mit dem Ethernet-Switch über ein Cat 7 (oder höher) Kabel. Dadurch wird die 10-Gbps-Verbindung hergestellt, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.

### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jedem Rechner den Namen seiner Netzwerkschnittstelle und notieren Sie ihn (er wird im weiteren Verlauf der Anleitung als `IFNAME` bezeichnet). Führen Sie aus:

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

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie den Kabelanschluss und stellen Sie sicher, dass der Switch-Port auf 10 Gbps eingestellt ist. Bei einigen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie hierzu die Dokumentation Ihres Switches zurate.

## Erweiterung der VRAM-Zuweisung

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Rechner 1 als auch auf Rechner 2 aus.

### Speicherkonfiguration für die Ausführung großer Modelle

Unter Linux verwendet ROCm einen gemeinsamen Systemspeicher-Pool, und dieser Pool ist standardmäßig auf die Hälfte des Systemspeichers konfiguriert.

Dieser Wert kann erhöht werden, indem die Seiteneinstellung (Page Setting) des Translation Table Manager (TTM) des Kernels gemäß den folgenden Anweisungen geändert wird. AMD empfiehlt, den minimal dedizierten VRAM im BIOS (0,5 GB) festzulegen.

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für über pipx installierte Wheels dem Systemsuchpfad hinzu.

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

* Konfigurieren Sie die Einstellungen für den gemeinsamen Speicher auf **120 GB** um:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.

## Initialisierung des vLLM-Containers

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Rechner 1 als auch auf Rechner 2 aus.

Ihr Ryzen AI Halo wird mit vLLM ausgeliefert, das in einem vorgefertigten Container-Image verpackt ist, welches Sie mit Podman, einem kostenlosen Open-Source-Container-Tool, ausführen.

### 1. Verzeichnis für den Modell-Download erstellen

Wenn Sie das Modell Qwen3.5-397B in diesem Playbook bereitstellen, lädt vLLM die Modellgewichte automatisch auf Ihr System herunter. Damit diese Gewichte auch innerhalb des Containers zugänglich sind, erstellen Sie zunächst ein Modellverzeichnis, das der Container einbinden kann:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Den vLLM-Container starten

Der folgende Befehl startet den Container und öffnet eine interaktive Shell. Er bindet das gerade erstellte Modellverzeichnis ein und übergibt Ihren `IFNAME` an `NCCL_SOCKET_IFNAME` und `GLOO_SOCKET_IFNAME`, um RCCL (der Bibliothek, die vLLM zur Koordination der GPUs im Cluster verwendet) mitzuteilen, welche Schnittstelle verwendet werden soll.

Starten Sie den Container mit:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den ausgegebenen Schnittstellennamen aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

## Ausführen des Modells im Cluster

vLLM verwendet Ray zur Orchestrierung des Clusters und RCCL zur Handhabung der GPU-zu-GPU-Kommunikation zwischen den Knoten. Ein Rechner fungiert als **Head-Node** (Rechner 1) und koordiniert die Inferenz. Der andere tritt als **Worker-Node** (Rechner 2) bei und trägt seinen GPU-Speicher und seine Rechenleistung bei.

> **Hinweis**: Ray ist eine optionale Abhängigkeit für vLLM und ist nur innerhalb des vorkonfigurierten Podman-Containers verfügbar.

Beim Start teilt vLLM das Modell mittels Tensor-Parallelität auf beide Knoten auf. Sobald es geladen ist, läuft die Inferenz ab, als würde sie auf einem einzigen Beschleuniger ausgeführt.

#### Vermeidung von Ray-OOM-Fehlern

Standardmäßig überwacht Ray den Host-Speicher auf jedem Knoten und beendet den größten Prozess, wenn die Speichernutzung 95 % überschreitet. Bei Ihrem Ryzen™ AI Halo teilen sich GPU und Host einen gemeinsamen Speicherpool, sodass das Laden eines Modells einen `ray.exceptions.OutOfMemoryError` auslösen und den Worker-Prozess beenden kann.

Um dies zu verhindern, exportieren wir auf jedem Rechner `RAY_memory_monitor_refresh_ms=0`, bevor wir den Cluster starten bzw. ihm beitreten.
### Schritt 1: Ray-Head-Node starten (Maschine 1)

Starten Sie auf Maschine 1 den Ray-Head-Node, um den Cluster zu initialisieren:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu ermitteln.

### Schritt 2: Dem Cluster beitreten (Maschine 2)

Verbinden Sie sich auf Maschine 2 mit dem Head-Node, um den Cluster zu bilden:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` ermitteln**: Führen Sie auf Maschine 2 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu ermitteln.

### Schritt 3: Das Modell bereitstellen (Maschine 1)

Starten Sie auf Maschine 1 den vLLM-Server. Dadurch wird das Modell automatisch heruntergeladen und über beide Nodes hinweg bereitgestellt:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Parameterübersicht

| Flag | Zweck |
|------|---------|
| `--port` | Port, über den die HTTP-API bereitgestellt wird |
| `--host` | IP-Adresse, an die der Server gebunden wird (`0.0.0.0` für alle Schnittstellen) |
| `--max-model-len` | Maximale Kontextlänge in Tokens |
| `--gpu-memory-utilization` | Anteil des GPU-Speichers, der zugewiesen wird (0,0–1,0) |
| `--dtype` | Datentyp für die Modellgewichte |
| `--tensor-parallel-size` | Anzahl der GPUs, über die das Modell aufgeteilt wird (auf die Gesamtzahl der GPUs im Cluster festlegen) |
| `--distributed-executor-backend` | Backend für die Ausführung über mehrere Nodes (`ray` für Cluster-Deployments) |
| `--enforce-eager` | Deaktiviert die CUDA-Graph-Kompilierung für Kompatibilität |
| `--language-model-only` | Überspringt das Laden zusätzlicher Modellkomponenten (z. B. Vision-Encoder) |
| `--reasoning-parser` | Aktiviert das strukturierte Parsen von Reasoning-Ausgaben für das Modell |

Eine vollständige Beschreibung der Parameterverwendung finden Sie in der [vLLM-Dokumentation](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Zugriff auf das Modell

vLLM stellt eine OpenAI-kompatible API bereit, sodass Sie beliebige kompatible Clients oder Oberflächen mit Ihrem Cluster verbinden können. Eine beliebte Option ist [Open WebUI](https://github.com/open-webui/open-webui), das eine browserbasierte Chat-Oberfläche bietet.

So verbinden Sie Open WebUI mit Ihrem vLLM-Endpunkt:

1. Öffnen Sie **Settings** > **Admin Panel** > **Connections**
2. Klicken Sie auf das **+** bei **Manage OpenAI API Connections**
3. Setzen Sie **Connection Type** auf **External**
4. Setzen Sie die **URL** auf `http://<MACHINE_1_IP>:7000/v1`
5. Wählen Sie unter **Auth** in der Dropdown-Liste **None** aus
6. Lassen Sie **Model IDs** leer, um automatisch alle Modelle vom Endpunkt zu erkennen

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu ermitteln. Wenn Sie von Maschine 1 selbst aus auf Open WebUI zugreifen, können Sie `http://localhost:7000/v1` verwenden.

![Open WebUI-Verbindungseinstellungen für den vLLM-Endpunkt](assets/openwebui-connection.png)

Wählen Sie nach dem Verbinden das Modell aus der Modell-Dropdown-Liste in Open WebUI aus und beginnen Sie zu chatten. Das Modell läuft jetzt über beide Ihrer Ryzen AI Halo-Nodes hinweg:

![Chatten mit Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Nächste Schritte

- **Weitere Modelle erkunden**: Entdecken Sie neue Modelle auf [Hugging Face](https://huggingface.co/models?&sort=trending), die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Nodes skalieren**: Fügen Sie zwei weitere Ryzen AI Halo-Systeme als zusätzliche Ray-Worker hinzu, um Modelle über noch mehr GPUs zu verteilen. Dies erfordert einen Ethernet-Switch mit mindestens vier Ports, jeweils einem pro Node. Folgen Sie [Schritt 2: Dem Cluster beitreten](#step-2-join-the-cluster-machine-2) auf jedem zusätzlichen Worker und erhöhen Sie `--tensor-parallel-size` entsprechend
- **Andere Parallelisierungsstrategien ausprobieren**: vLLM unterstützt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) für Mixture-of-Experts-Modelle und [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) für höheren Durchsatz. Experimentieren Sie mit `--enable-expert-parallel` und `--data-parallel-size`, um die beste Konfiguration für Ihre Workload zu finden
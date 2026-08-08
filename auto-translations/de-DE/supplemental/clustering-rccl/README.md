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

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird, sodass Sie Zugriff auf noch größere Modelle mit stärkerem logischem Denken, besserer Codegenerierung und tieferem mehrsprachigem Verständnis erhalten – vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo Systeme mit RCCL (ROCm Communication Collectives Library) und vLLM clustern und Qwen3.5-397B, ein Modell mit 397 Milliarden Parametern, mit ROCm-Beschleunigung auf beiden Rechnern ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo Systemen erweitern
- Starten von vLLM mit ROCm-Unterstützung
- Konfigurieren von RCCL für Multi-Node-Tensor-Parallel-Inferenz über zwei Ryzen AI Halo Systeme hinweg
- Ausführen eines Modells mit 397 Milliarden Parametern über zwei vernetzte Ryzen AI Halo Systeme

## Voraussetzungen

### Hardware

Für dieses Playbook werden zwei Ryzen AI Halo Einheiten und ein Ethernet-Switch benötigt, die in einer Stern-Topologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Anzahl | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Compute-Knoten, die den Cluster bilden |
| 10-Gbps-Ethernet-Switch | 1 | Zentraler Switch, um die Kommunikation mehrerer Ryzen AI Halo Knoten zu ermöglichen (mindestens 2 Ports) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden zwei Ethernet-Switch-Ports benötigt, um die beiden Ryzen AI Halo Einheiten zu verbinden. Ein dritter Port ist erforderlich, wenn Sie auf das Modell von einem separaten Client-Rechner statt von einer der Halo-Einheiten aus zugreifen.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Einrichtung der physischen Hardware

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Verbinden Sie jede Ryzen AI Halo Einheit mit dem Ethernet-Switch über ein Cat-7-Kabel (oder höher). Dadurch wird die 10-Gbps-Verbindung hergestellt, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.

### 1. Netzwerkschnittstellen bestimmen

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (im weiteren Verlauf der Anleitung wird darauf als `IFNAME` verwiesen). Führen Sie aus:

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

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den Namen der Ausgabeschnittstelle aus [1. Netzwerkschnittstellen bestimmen](#1-determine-network-interfaces)

Sie sollten eine Geschwindigkeit von `10000Mb/s` sehen:

```bash
	Speed: 10000Mb/s
```

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und bestätigen Sie, dass der Switch-Port auf 10 Gbps eingestellt ist. Bei manchen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell eingestellt werden; ziehen Sie die Dokumentation Ihres Switches zurate.

## Erweiterung der VRAM-Zuweisung

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

### Speicherkonfiguration für die Ausführung großer Modelle

Unter Linux nutzt ROCm einen gemeinsam genutzten Systemspeicherpool, der standardmäßig auf die Hälfte des Systemspeichers eingestellt ist.

Diese Menge kann erhöht werden, indem die Seiteneinstellung des Translation Table Manager (TTM) des Kernels mit den folgenden Anweisungen geändert wird. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS auf 0,5 GB einzustellen.

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für die von pipx installierten Wheels dem System-Suchpfad hinzu.

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

* Konfigurieren Sie die Einstellungen für den gemeinsamen Speicher auf **120 GB** neu:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.

## Initialisierung des vLLM-Containers

> **Hinweis**: Führen Sie diesen Schritt sowohl auf Maschine 1 als auch auf Maschine 2 aus.

Ihr Ryzen AI Halo wird mit vLLM ausgeliefert, das in einem vorgefertigten Container-Image enthalten ist, das Sie mit Podman, einem kostenlosen Open-Source-Container-Tool, ausführen.

### 1. Verzeichnis für den Modell-Download erstellen

Wenn Sie das Modell Qwen3.5-397B in diesem Playbook bereitstellen, lädt vLLM die Modellgewichte automatisch auf Ihr System herunter. Damit diese Gewichte innerhalb des Containers zugänglich sind, erstellen Sie zunächst ein Modellverzeichnis, das der Container einbinden kann:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Starten des vLLM-Containers

Der folgende Befehl startet den Container und öffnet eine interaktive Shell. Er bindet das soeben erstellte Modellverzeichnis ein und übergibt Ihren `IFNAME` an `NCCL_SOCKET_IFNAME` und `GLOO_SOCKET_IFNAME`, um RCCL (die Bibliothek, die vLLM zur Koordination der GPUs im Cluster verwendet) mitzuteilen, welche Schnittstelle verwendet werden soll.

Starten Sie den Container mit:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den Namen der Ausgabeschnittstelle aus [1. Netzwerkschnittstellen bestimmen](#1-determine-network-interfaces)

## Ausführen des Modells im Cluster

vLLM verwendet Ray, um den Cluster zu orchestrieren, und RCCL, um die GPU-zu-GPU-Kommunikation über Knoten hinweg zu handhaben. Eine Maschine fungiert als **Head-Node** (Maschine 1) und koordiniert die Inferenz. Die andere tritt als **Worker-Node** (Maschine 2) bei und stellt ihren GPU-Speicher und ihre Rechenleistung zur Verfügung.

> **Hinweis**: Ray ist eine optionale Abhängigkeit für vLLM und ist nur innerhalb des vorkonfigurierten Podman-Containers verfügbar.

Beim Start teilt vLLM das Modell mithilfe von Tensor-Parallelität auf beide Knoten auf. Sobald es geladen ist, läuft die Inferenz so ab, als würde sie auf einem einzigen Beschleuniger ausgeführt.

### Schritt 1: Starten des Ray-Head-Node (Maschine 1)

Starten Sie auf Maschine 1 den Ray-Head-Node, um den Cluster zu initialisieren:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Ermitteln von `<MACHINE_1_IP>`**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden.
### Schritt 2: Dem Cluster beitreten (Maschine 2)

Verbinden Sie sich auf Maschine 2 mit dem Head-Node, um den Cluster zu bilden:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` ermitteln**: Führen Sie auf Maschine 2 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu ermitteln.

### Schritt 3: Das Modell bereitstellen (Maschine 1)

Starten Sie auf Maschine 1 den vLLM-Server. Dadurch wird das Modell automatisch heruntergeladen und über beide Knoten hinweg bereitgestellt:

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
|------|-------|
| `--port` | Port, auf dem die HTTP-API bereitgestellt wird |
| `--host` | IP-Adresse, an die der Server gebunden wird (`0.0.0.0` für alle Schnittstellen) |
| `--max-model-len` | Maximale Kontextlänge in Tokens |
| `--gpu-memory-utilization` | Anteil des zu belegenden GPU-Speichers (0,0–1,0) |
| `--dtype` | Datentyp für die Modellgewichte |
| `--tensor-parallel-size` | Anzahl der GPUs, über die das Modell aufgeteilt wird (auf die Gesamtzahl der GPUs im Cluster setzen) |
| `--distributed-executor-backend` | Backend für die Ausführung über mehrere Knoten (`ray` für Cluster-Deployments) |
| `--enforce-eager` | Deaktiviert die CUDA-Graph-Kompilierung zur Kompatibilität |
| `--language-model-only` | Überspringt das Laden zusätzlicher Modellkomponenten (z. B. Vision-Encoder) |
| `--reasoning-parser` | Aktiviert das Parsen strukturierter Reasoning-Ausgaben für das Modell |

Die vollständige Parameterverwendung finden Sie in der [vLLM-Dokumentation](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Zugriff auf das Modell

vLLM stellt eine OpenAI-kompatible API bereit, sodass Sie beliebige kompatible Clients oder Oberflächen mit Ihrem Cluster verbinden können. Eine beliebte Option ist [Open WebUI](https://github.com/open-webui/open-webui), das eine browserbasierte Chat-Oberfläche bietet.

So verbinden Sie Open WebUI mit Ihrem vLLM-Endpunkt:

1. Öffnen Sie **Settings** > **Admin Panel** > **Connections**
2. Klicken Sie auf das **+** bei **Manage OpenAI API Connections**
3. Setzen Sie den **Connection Type** auf **External**
4. Setzen Sie die **URL** auf `http://<MACHINE_1_IP>:7000/v1`
5. Wählen Sie unter **Auth** in der Dropdown-Liste **None** aus
6. Lassen Sie **Model IDs** leer, um automatisch alle Modelle des Endpunkts zu erkennen

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu ermitteln. Wenn Sie von Maschine 1 selbst aus auf Open WebUI zugreifen, können Sie `http://localhost:7000/v1` verwenden.

![Open WebUI-Verbindungseinstellungen für den vLLM-Endpunkt](assets/openwebui-connection.png)

Sobald die Verbindung besteht, wählen Sie das Modell im Modell-Dropdown von Open WebUI aus und beginnen Sie mit dem Chatten. Das Modell läuft nun über beide Ihrer Ryzen AI Halo-Knoten:

![Chatten mit Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Nächste Schritte

- **Weitere Modelle entdecken**: Entdecken Sie neue Modelle auf [Hugging Face](https://huggingface.co/models?&sort=trending), die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Knoten skalieren**: Fügen Sie zwei weitere Ryzen AI Halo-Systeme als zusätzliche Ray-Worker hinzu, um Modelle auf noch mehr GPUs aufzuteilen. Dazu ist ein Ethernet-Switch mit mindestens vier Ports erforderlich, einen für jeden Knoten. Führen Sie [Schritt 2: Dem Cluster beitreten](#step-2-join-the-cluster-machine-2) auf jedem zusätzlichen Worker aus und erhöhen Sie `--tensor-parallel-size` entsprechend
- **Andere Parallelisierungsstrategien ausprobieren**: vLLM unterstützt [Expert Parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) für Mixture-of-Experts-Modelle und [Data Parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) für höheren Durchsatz. Experimentieren Sie mit `--enable-expert-parallel` und `--data-parallel-size`, um die beste Konfiguration für Ihre Arbeitslast zu finden
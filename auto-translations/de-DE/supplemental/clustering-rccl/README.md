<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clustering von zwei Ryzen™ AI Halos mit RCCL

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird, sodass Sie Zugang zu noch größeren Modellen mit stärkerer Schlussfolgerungsfähigkeit, besserer Code-Generierung und tieferem mehrsprachigem Verständnis erhalten – alles vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie zwei Ryzen AI Halo-Systeme mithilfe von RCCL (ROCm Communication Collectives Library) mit vLLM zu einem Cluster zusammenschließen und Qwen3.5-397B, ein Modell mit 397 Milliarden Parametern, mit ROCm-Beschleunigung über beide Maschinen hinweg ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo-Systemen erweitern
- Starten von vLLM mit ROCm-Unterstützung
- Konfigurieren von RCCL für Multi-Node-Tensor-Parallel-Inferenz über zwei Ryzen AI Halo-Systeme
- Ausführen eines Modells mit 397 Milliarden Parametern über zwei vernetzte Ryzen AI Halo-Systeme

## Voraussetzungen

### Hardware

Dieses Playbook erfordert zwei Ryzen AI Halo-Einheiten und einen Ethernet-Switch, die in einer Sterntopologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Anzahl | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Rechenknoten, die den Cluster bilden |
| 10-Gbps-Ethernet-Switch | 1 | Zentraler Switch für die Multi-Node-Kommunikation zwischen den Ryzen AI Halo-Einheiten (mindestens 2 Ports) |
| Ethernet-Kabel | 2 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Zwei Ethernet-Switch-Ports werden benötigt, um die beiden Ryzen AI Halo-Einheiten zu verbinden. Ein dritter Port ist erforderlich, wenn Sie von einem separaten Client-Rechner anstatt von einer der Halo-Einheiten auf das Modell zugreifen.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Physisches Hardware-Setup

> **Hinweis**: Führen Sie diesen Schritt auf Maschine 1 und Maschine 2 durch.

Verbinden Sie jede Ryzen AI Halo-Einheit mit einem Cat-7-Kabel (oder höher) mit dem Ethernet-Switch. Dadurch wird die 10-Gbps-Verbindung hergestellt, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.

### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (er wird im weiteren Verlauf der Anleitung als `IFNAME` bezeichnet). Führen Sie aus:

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

## VRAM-Zuweisung erweitern

> **Hinweis**: Führen Sie diesen Schritt auf Maschine 1 und Maschine 2 durch.

### Speicherkonfiguration für die Ausführung großer Modelle

Unter Linux nutzt ROCm einen gemeinsamen Systemspeicherpool, der standardmäßig auf die Hälfte des Systemspeichers konfiguriert ist.

Dieser Wert kann durch Ändern der TTM-Seiteneinstellung (Translation Table Manager) des Kernels erhöht werden. Folgen Sie dazu den nachstehenden Anweisungen. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS auf 0,5 GB festzulegen.

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

* Konfigurieren Sie die Einstellungen für den gemeinsamen Speicher auf **120 GB** neu:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.

## vLLM-Container-Initialisierung

> **Hinweis**: Führen Sie diesen Schritt auf Maschine 1 und Maschine 2 durch.

Ihr Ryzen AI Halo wird mit vLLM geliefert, das in einem vorgefertigten Container-Image verpackt ist und mit Podman ausgeführt wird, einem freien und quelloffenen Container-Tool.

### 1. Verzeichnis für den Modell-Download erstellen

Wenn Sie das Qwen3.5-397B-Modell in diesem Playbook bereitstellen, lädt vLLM die Modellgewichte automatisch auf Ihr System herunter. Um sicherzustellen, dass diese Gewichte von innerhalb des Containers zugänglich sind, erstellen Sie zunächst ein Modellverzeichnis, das der Container einbinden kann:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Den vLLM-Container starten

Der folgende Befehl startet den Container und versetzt Sie in eine interaktive Shell. Er bindet das soeben erstellte Modellverzeichnis ein und übergibt Ihren `IFNAME` an `NCCL_SOCKET_IFNAME` und `GLOO_SOCKET_IFNAME`, wodurch RCCL (die Bibliothek, die vLLM zur Koordination von GPUs im Cluster verwendet) mitgeteilt wird, welche Schnittstelle zu verwenden ist.

Starten Sie den Container mit:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den ausgegebenen Schnittstellennamen aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

## Das Modell im Cluster ausführen

vLLM verwendet Ray zur Orchestrierung des Clusters und RCCL für die GPU-zu-GPU-Kommunikation zwischen den Knoten. Eine Maschine fungiert als **Head-Node** (Maschine 1) und koordiniert die Inferenz. Die andere tritt als **Worker-Node** (Maschine 2) bei und stellt ihren GPU-Speicher und ihre Rechenleistung zur Verfügung.

> **Hinweis**: Ray ist eine optionale Abhängigkeit für vLLM und ist nur innerhalb des vorkonfigurierten Podman-Containers verfügbar.

Beim Start verteilt vLLM das Modell mithilfe von Tensor-Parallelismus auf beide Knoten. Nach dem Laden verläuft die Inferenz so, als würde sie auf einem einzigen Beschleuniger ausgeführt.

### Schritt 1: Den Ray-Head-Node starten (Maschine 1)

Starten Sie auf Maschine 1 den Ray-Head-Node, um den Cluster zu initialisieren:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln.

### Schritt 2: Dem Cluster beitreten (Maschine 2)

Verbinden Sie sich auf Maschine 2 mit dem Head-Node, um den Cluster zu bilden:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` ermitteln**: Führen Sie auf Maschine 2 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln.

### Schritt 3: Das Modell bereitstellen (Maschine 1)

Starten Sie auf Maschine 1 den vLLM-Server. Dieser lädt das Modell automatisch herunter und beginnt, es über beide Knoten bereitzustellen:

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

#### Parameterreferenz

| Flag | Zweck |
|------|---------|
| `--port` | Port, auf dem die HTTP-API bereitgestellt wird |
| `--host` | IP-Adresse, an die der Server gebunden wird (`0.0.0.0` für alle Schnittstellen) |
| `--max-model-len` | Maximale Kontextlänge in Token |
| `--gpu-memory-utilization` | Anteil des zuzuweisenden GPU-Speichers (0,0–1,0) |
| `--dtype` | Datentyp für Modellgewichte |
| `--tensor-parallel-size` | Anzahl der GPUs, auf die das Modell verteilt wird (auf die Gesamtzahl der GPUs im Cluster setzen) |
| `--distributed-executor-backend` | Backend für die Multi-Node-Ausführung (`ray` für Cluster-Deployments) |
| `--enforce-eager` | Deaktiviert die CUDA-Graph-Kompilierung für Kompatibilität |
| `--language-model-only` | Überspringt das Laden von Hilfsmodellkomponenten (z. B. Vision-Encoder) |
| `--reasoning-parser` | Aktiviert das strukturierte Reasoning-Output-Parsing für das Modell |

Vollständige Informationen zur Parameterverwendung finden Sie in der [vLLM-Dokumentation](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Auf das Modell zugreifen

vLLM stellt eine OpenAI-kompatible API bereit, sodass Sie jeden kompatiblen Client oder jede kompatible Oberfläche mit Ihrem Cluster verbinden können. Eine beliebte Option ist [Open WebUI](https://github.com/open-webui/open-webui), das eine browserbasierte Chat-Oberfläche bietet.

So verbinden Sie Open WebUI mit Ihrem vLLM-Endpunkt:

1. Öffnen Sie **Einstellungen** > **Admin-Panel** > **Verbindungen**
2. Klicken Sie auf das **+** bei **OpenAI-API-Verbindungen verwalten**
3. Setzen Sie den **Verbindungstyp** auf **Extern**
4. Setzen Sie die **URL** auf `http://<MACHINE_1_IP>:7000/v1`
5. Wählen Sie unter **Auth** aus dem Dropdown-Menü **Keine** aus
6. Lassen Sie **Modell-IDs** leer, um alle Modelle vom Endpunkt automatisch zu erkennen

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um die lokale IP-Adresse zu ermitteln. Wenn Sie von Maschine 1 selbst auf Open WebUI zugreifen, können Sie `http://localhost:7000/v1` verwenden.

![Open WebUI-Verbindungseinstellungen für den vLLM-Endpunkt](assets/openwebui-connection.png)

Nach der Verbindung wählen Sie das Modell aus dem Modell-Dropdown in Open WebUI aus und beginnen Sie mit dem Chatten. Das Modell läuft nun über beide Ihrer Ryzen AI Halo-Knoten:

![Chatten mit Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Nächste Schritte

- **Andere Modelle erkunden**: Entdecken Sie neue Modelle auf [Hugging Face](https://huggingface.co/models?&sort=trending), die in den kombinierten GPU-Speicher Ihres Clusters passen
- **Auf vier Knoten skalieren**: Fügen Sie zwei weitere Ryzen AI Halo-Systeme als zusätzliche Ray-Worker hinzu, um Modelle über noch mehr GPUs zu verteilen. Dafür ist ein Ethernet-Switch mit mindestens vier Ports erforderlich, einen für jeden Knoten. Folgen Sie [Schritt 2: Dem Cluster beitreten](#step-2-join-the-cluster-machine-2) auf jedem zusätzlichen Worker und erhöhen Sie `--tensor-parallel-size` entsprechend
- **Andere Parallelisierungsstrategien ausprobieren**: vLLM unterstützt [Expert Parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) für Mixture-of-Experts-Modelle und [Data Parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) für höheren Durchsatz. Experimentieren Sie mit `--enable-expert-parallel` und `--data-parallel-size`, um die beste Konfiguration für Ihre Arbeitslast zu finden
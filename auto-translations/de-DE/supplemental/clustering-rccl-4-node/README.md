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

# Clustering von vier Ryzen™ AI Halos mit RCCL

## Übersicht

Ihr Ryzen™ AI Halo ist bereits in der Lage, große Sprachmodelle lokal auszuführen. Clustering geht hier noch einen Schritt weiter, indem der GPU-Speicher mehrerer Systeme über ein lokales Netzwerk kombiniert wird. So erhalten Sie Zugriff auf noch größere Modelle mit stärkerer Argumentationsfähigkeit, besserer Codegenerierung und tieferem mehrsprachigem Verständnis, und das vollständig auf Ihrer eigenen Hardware.

Dieses Playbook zeigt Ihnen, wie Sie vier Ryzen AI Halo Systeme mit RCCL (ROCm Communication Collectives Library) zusammen mit vLLM clustern und Qwen3.5-397B, ein Modell mit 397 Milliarden Parametern, auf allen vier Maschinen mit ROCm-Beschleunigung ausführen.

## Was Sie lernen werden

- Wie Sie die VRAM-Zuweisung auf Ryzen AI Halo Systemen erweitern
- Starten von vLLM mit ROCm-Unterstützung
- Konfigurieren von RCCL für Multi-Node-Tensor-Parallel-Inferenz über vier Ryzen AI Halo Systeme hinweg
- Ausführen eines Modells mit 397 Milliarden Parametern über vier vernetzte Ryzen AI Halo Systeme

## Voraussetzungen

### Hardware

Für dieses Playbook werden vier Ryzen AI Halo Einheiten sowie ein Ethernet-Switch benötigt, die in einer Sterntopologie verbunden sind, wobei jede Einheit direkt mit dem Switch verkabelt ist.

| Komponente | Menge | Beschreibung |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Recheneinheiten, die den Cluster bilden |
| 10-Gbit/s-Ethernet-Switch | 1 | Zentraler Switch, um die Kommunikation zwischen mehreren Ryzen AI Halo Knoten zu ermöglichen (mindestens 4 Ports) |
| Ethernet-Kabel | 4 | Verbindet jede Halo-Einheit mit dem Switch (Cat 7 oder höher empfohlen) |

> **Hinweis**: Es werden vier Ethernet-Switch-Ports benötigt, um die vier Ryzen AI Halo Einheiten anzuschließen. Ein fünfter Port ist erforderlich, wenn Sie auf das Modell von einer separaten Client-Maschine aus zugreifen, anstatt von einer der Halo-Einheiten.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Einrichtung der physischen Hardware

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen durch (Maschine 1 bis Maschine 4).

Verbinden Sie jede Ryzen AI Halo Einheit mit dem Ethernet-Switch über ein Cat-7-Kabel (oder höher). Dies stellt die 10-Gbit/s-Verbindung her, die für die Hochgeschwindigkeitskommunikation zwischen den Knoten verwendet wird.

### 1. Netzwerkschnittstellen ermitteln

Ermitteln Sie auf jeder Maschine den Namen ihrer Netzwerkschnittstelle und notieren Sie ihn (sie wird im weiteren Verlauf der Anleitung als `IFNAME` bezeichnet). Führen Sie Folgendes aus:

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

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den Namen der ausgegebenen Schnittstelle aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

Sie sollten eine Geschwindigkeit von `10000Mb/s` sehen:

```bash
	Speed: 10000Mb/s
```

> **Hinweis**: Wenn die Geschwindigkeit niedriger als `10000Mb/s` ist oder die Verbindung nicht zustande kommt, überprüfen Sie die Kabelverbindung und stellen Sie sicher, dass der Switch-Port auf 10 Gbit/s eingestellt ist. Bei manchen Switches muss die automatische Aushandlung deaktiviert und die Verbindungsgeschwindigkeit manuell festgelegt werden; beachten Sie dazu die Dokumentation Ihres Switches.

## Erweiterung der VRAM-Zuweisung

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen durch (Maschine 1 bis Maschine 4).

### Speicherkonfiguration für die Ausführung großer Modelle

Unter Linux nutzt ROCm einen gemeinsamen Systemspeicherpool, der standardmäßig auf die Hälfte des Systemspeichers konfiguriert ist.

Dieser Wert kann erhöht werden, indem die Seiteneinstellung des Translation Table Manager (TTM) des Kernels geändert wird, wie in den folgenden Anweisungen beschrieben. AMD empfiehlt, den minimalen dedizierten VRAM im BIOS festzulegen (0,5 GB).

* Installieren Sie das pipx-Dienstprogramm und fügen Sie den Pfad für mit pipx installierte Wheels dem Systemsuchpfad hinzu.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Installieren Sie das amd-debug-tools-Wheel von PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Führen Sie das amd-ttm-Tool aus, um die aktuellen Einstellungen für gemeinsam genutzten Speicher abzufragen.
  ```bash
  amd-ttm
  ```

* Konfigurieren Sie die Einstellungen für gemeinsam genutzten Speicher auf **120 GB** um:
  ```bash
  amd-ttm --set 120
  ```

* Starten Sie das System neu, damit die Änderungen wirksam werden.

## Initialisierung des vLLM-Containers

> **Hinweis**: Führen Sie diesen Schritt auf allen vier Maschinen durch (Maschine 1 bis Maschine 4).

Ihr Ryzen AI Halo wird mit vLLM ausgeliefert, das in einem vorgefertigten Container-Image verpackt ist, das Sie mit Podman ausführen, einem kostenlosen und quelloffenen Container-Tool.

### 1. Erstellen des Verzeichnisses für den Modell-Download

Wenn Sie in diesem Playbook das Modell Qwen3.5-397B bereitstellen, lädt vLLM die Modellgewichte automatisch auf Ihr System herunter. Damit diese Gewichte innerhalb des Containers zugänglich sind, erstellen Sie zunächst ein Modellverzeichnis, das der Container einbinden kann:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Starten des vLLM-Containers

Der folgende Befehl startet den Container und versetzt Sie in eine interaktive Shell. Er bindet das soeben erstellte Modellverzeichnis ein und übergibt Ihren `IFNAME` an `NCCL_SOCKET_IFNAME` und `GLOO_SOCKET_IFNAME`, um RCCL (die Bibliothek, die vLLM zur Koordination der GPUs im Cluster verwendet) mitzuteilen, welche Schnittstelle verwendet werden soll.

Starten Sie den Container mit:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Hinweis**: Ersetzen Sie `<IFNAME>` durch den Namen der ausgegebenen Schnittstelle aus [1. Netzwerkschnittstellen ermitteln](#1-determine-network-interfaces)

## Ausführen des Modells auf dem Cluster

vLLM verwendet Ray zur Orchestrierung des Clusters und RCCL zur Steuerung der GPU-zu-GPU-Kommunikation zwischen den Knoten. Eine Maschine fungiert als Head-Node (Maschine 1) und koordiniert die Inferenz. Die anderen drei treten als Worker-Nodes bei (Maschinen 2, 3 und 4) und stellen ihren GPU-Speicher und ihre Rechenleistung zur Verfügung.

> **Hinweis**: Ray ist eine optionale Abhängigkeit für vLLM und ist nur innerhalb des vorkonfigurierten Podman-Containers verfügbar.

Beim Start teilt vLLM das Modell mithilfe von Tensor-Parallelität auf alle vier Knoten auf. Sobald das Modell geladen ist, läuft die Inferenz ab, als würde sie auf einem einzigen Beschleuniger ausgeführt.

#### Verhindern von Ray-OOM-Fehlern

Standardmäßig überwacht Ray den Host-Speicher auf jedem Knoten und beendet den größten Prozess, wenn die Speichernutzung 95 % überschreitet. Auf Ihrem Ryzen™ AI Halo teilen sich GPU und Host einen gemeinsamen Speicherpool, sodass das Laden eines Modells einen `ray.exceptions.OutOfMemoryError` auslösen und den Worker-Prozess beenden kann.

Um dies zu verhindern, exportieren wir auf jeder Maschine `RAY_memory_monitor_refresh_ms=0`, bevor der Cluster gestartet wird bzw. ihm beigetreten wird.
### Schritt 1: Ray-Hauptknoten starten (Maschine 1)

Starten Sie auf Maschine 1 den Ray-Hauptknoten, um den Cluster zu initialisieren:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden.

### Schritt 2: Dem Cluster beitreten (Maschinen 2, 3 und 4)

Verbinden Sie auf jeder der Maschinen 2, 3 und 4 den Hauptknoten, um den Cluster zu bilden:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **`<MACHINE_N_IP>` ermitteln**: Führen Sie auf jeder Worker-Maschine `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden.

### Schritt 3: Das Modell bereitstellen (Maschine 1)

Starten Sie auf Maschine 1 den vLLM-Server. Dadurch wird das Modell automatisch heruntergeladen und über alle vier Knoten hinweg bereitgestellt:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
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
| `--gpu-memory-utilization` | Anteil des zu belegenden GPU-Speichers (0,0–1,0) |
| `--dtype` | Datentyp für die Modellgewichte |
| `--tensor-parallel-size` | Anzahl der GPUs, auf die das Modell aufgeteilt wird (auf die Gesamtzahl der GPUs im Cluster setzen) |
| `--distributed-executor-backend` | Backend für die Ausführung über mehrere Knoten (`ray` für Cluster-Bereitstellungen) |
| `--enforce-eager` | Deaktiviert die CUDA-Graph-Kompilierung für Kompatibilität |
| `--language-model-only` | Überspringt das Laden zusätzlicher Modellkomponenten (z. B. Vision-Encoder) |
| `--reasoning-parser` | Aktiviert das strukturierte Parsen von Reasoning-Ausgaben für das Modell |

Eine vollständige Beschreibung der Parameter finden Sie in der [vLLM-Dokumentation](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Zugriff auf das Modell

vLLM stellt eine OpenAI-kompatible API bereit, sodass Sie jeden kompatiblen Client oder jede kompatible Oberfläche mit Ihrem Cluster verbinden können. Eine beliebte Option ist [Open WebUI](https://github.com/open-webui/open-webui), das eine browserbasierte Chat-Oberfläche bietet.

So verbinden Sie Open WebUI mit Ihrem vLLM-Endpunkt:

1. Öffnen Sie **Settings** > **Admin Panel** > **Connections**
2. Klicken Sie auf das **+** bei **Manage OpenAI API Connections**
3. Setzen Sie den **Connection Type** auf **External**
4. Setzen Sie die **URL** auf `http://<MACHINE_1_IP>:7000/v1`
5. Wählen Sie unter **Auth** im Dropdown-Menü **None** aus
6. Lassen Sie **Model IDs** leer, um alle Modelle des Endpunkts automatisch zu erkennen

> **`<MACHINE_1_IP>` ermitteln**: Führen Sie auf Maschine 1 `hostname -I | awk '{print $1}'` aus, um ihre lokale IP-Adresse zu finden. Wenn Sie von Maschine 1 selbst aus auf Open WebUI zugreifen, können Sie `http://localhost:7000/v1` verwenden.

![Verbindungseinstellungen von Open WebUI für den vLLM-Endpunkt](assets/openwebui-connection.png)

Sobald die Verbindung hergestellt ist, wählen Sie das Modell im Modell-Dropdown-Menü von Open WebUI aus und beginnen Sie mit dem Chatten. Das Modell läuft nun über alle vier Ihrer Ryzen AI Halo-Knoten:

![Chatten mit Qwen3.5-397B in Open WebUI](assets/openwebui-chat.png)

## Nächste Schritte

- **Weitere Modelle entdecken**: Entdecken Sie neue Modelle auf [Hugging Face](https://huggingface.co/models?&sort=trending), die in den gemeinsamen GPU-Speicher Ihres Clusters passen
- **Über vier Knoten hinaus skalieren**: Fügen Sie weitere Ryzen AI Halo-Systeme als zusätzliche Ray-Worker hinzu, um Modelle auf noch mehr GPUs aufzuteilen. Führen Sie [Schritt 2: Dem Cluster beitreten](#step-2-join-the-cluster-machines-2-3-and-4) für jeden weiteren Worker aus und erhöhen Sie `--tensor-parallel-size` entsprechend
- **Andere Parallelisierungsstrategien ausprobieren**: vLLM unterstützt [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) für Mixture-of-Experts-Modelle und [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) für höheren Durchsatz. Experimentieren Sie mit `--enable-expert-parallel` und `--data-parallel-size`, um die beste Konfiguration für Ihre Arbeitslast zu finden
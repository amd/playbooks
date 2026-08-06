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


## Übersicht

vLLM ist eine leistungsstarke Inferenz-Engine für große Sprachmodelle (LLMs). Sie bietet optimiertes Serving mit kontinuierlichem Batching für hohen Durchsatz sowie eine OpenAI-kompatible API für die nahtlose Integration in Anwendungen. Dies macht vLLM ideal für Produktionsumgebungen, in denen Geschwindigkeit und Ressourceneffizienz entscheidend sind.

Dieses Playbook zeigt Ihnen, wie Sie LLMs mit containerisiertem vLLM auf der integrierten GPU bereitstellen und über die OpenAI Python API mit Modellen interagieren.

## Was Sie lernen werden

- Wie Sie einen vLLM-Server mit AMD ROCm™-Unterstützung einrichten und starten
- Wie Sie über OpenAI-kompatible API-Endpunkte mit Modellen interagieren
- Wie Sie Prompts mit `vllm-prompt` an den lokalen Server senden

## Festlegen der Speicherkonfiguration

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es über das AMD Ryzen™ AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Installieren der Software-Voraussetzungen

vLLM läuft in einem vorgefertigten Container mit ROCm und passenden Abhängigkeiten. Es ist keine zusätzliche Installation erforderlich.

Es gibt keinen host-seitigen vLLM-Installationsschritt. Starten Sie vLLM mit:

```bash
vllm-launch
```

Der Launcher startet den Container, adressiert die integrierte GPU und stellt einen lokalen OpenAI-kompatiblen vLLM-Server bereit. Alternativ können Sie auf das vLLM-Symbol in der Taskleiste klicken.

## Schnellstart

### 1. Überprüfen, ob der vLLM-Server läuft

`vllm-launch` kann einige Minuten benötigen, um alles zu initialisieren. Sobald der Server gestartet ist, ist er unter `http://localhost:8001` erreichbar. Lassen Sie das Start-Terminal geöffnet, da der Server im Vordergrund läuft, und öffnen Sie ein separates Terminal für die restlichen Schritte. Die folgenden Beispiele verwenden `Qwen/Qwen3-1.7B`; falls Ihr Launcher für ein anderes Modell konfiguriert ist, ersetzen Sie diese Modell-ID in den Anfragen entsprechend.

### 2. Einen Prompt senden

Verwenden Sie das mitgelieferte `vllm-prompt`-Skript, um eine Anfrage an den lokalen OpenAI-kompatiblen vLLM-Server zu senden:

```bash
vllm-prompt "Tell me a story"
```

### 3. Mit dem Modell über die OpenAI Python API chatten

Da vLLM eine OpenAI-kompatible API bereitstellt, können Sie das `openai`-Python-Paket verwenden, um damit zu interagieren.

Erstellen Sie zunächst eine virtuelle Python-Umgebung:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installieren Sie das OpenAI-Paket
```bash
pip install openai
```

Erstellen Sie einen `OpenAI`-Client, der auf den lokalen vLLM-Server statt auf die Server von OpenAI verweist. Der `api_key` wird vom Client benötigt, aber vLLM validiert ihn nicht, daher funktioniert jede beliebige Zeichenfolge:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Senden Sie anschließend eine Chat-Completion-Anfrage. Diese verwendet dasselbe Nachrichtenformat wie die OpenAI-API — eine Liste von Nachrichten mit Rollen wie `"user"` und `"assistant"`. Durch die Einstellung `stream=True` trifft die Antwort schrittweise ein, anstatt auf einmal:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Iterieren Sie abschließend über die gestreamten Chunks und geben Sie jeden Textabschnitt aus, sobald er eintrifft:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Das mitgelieferte Skript [chat_with_model.py](assets/chat_with_model.py) enthält das gesamte Beispiel und kann heruntergeladen werden.


## Auswahl und Konfiguration eines Modells

Standardmäßig stellt `vllm-launch` `Qwen/Qwen3-1.7B` als Testmodell auf Port `8001` bereit. Sie können das Modell, den Port und die vLLM-Serving-Parameter ändern, ohne den Container neu zu erstellen oder zu bearbeiten.

### Von AMD getestete Modelle

Die folgenden Modelle sind vorkonfiguriert und von AMD validiert:

| Modell | Hinweise |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standardmodell. Leichtgewichtig und schnell zu laden. |
| `openai/gpt-oss-20b` | Größeres Modell für qualitativ hochwertigere Antworten. |

### Starten eines anderen Modells

Übergeben Sie die Modell-ID mit `--model` (oder `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Ändern des Ports

Übergeben Sie einen Port über 1024 mit `--port` (oder `-p`); der Standard ist `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Wenn Sie den Port ändern, richten Sie die `base_url` Ihres Clients auf denselben Port aus (zum Beispiel `http://localhost:8080/v1`).

### Übergeben zusätzlicher vLLM-Parameter

Alle zusätzlichen Argumente werden direkt an vLLM weitergeleitet, sodass Sie das Serving-Verhalten wie Kontextlänge oder Datentyp anpassen können. Es gibt zwei Möglichkeiten, diese zu übergeben.

**Inline**, nach den Launcher-Optionen:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Dauerhaft**, in einer Konfigurationsdatei unter `~/.local/share/vLLM/vllm-launch.conf`. Diese Datei existiert standardmäßig nicht — erstellen Sie sie und fügen Sie Ihre Argumente als Bash-Array hinzu:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Verwenden Sie `+=`, um an die Standardargumente anzuhängen, anstatt sie zu ersetzen:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Um jederzeit alle Launcher-Optionen anzuzeigen, führen Sie aus:

```bash
vllm-launch --help
```

### Speicherort der Modelle

`vllm-launch` sucht Modelle an zwei Orten:

| Speicherort | Pfad |
|----------|------|
| Systemmodelle | `/var/cache/models` |
| Benutzermodelle | `~/.local/share/vLLM/models` |

Sie können ein heruntergeladenes Modell in einem der beiden Verzeichnisse ablegen und es starten, indem Sie seinen Pfad oder seine ID an `--model` übergeben:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Hinweis**: Das Ausführen eines eigenen heruntergeladenen Modells auf diese Weise sollte funktionieren, sobald das Modell in einem der oben genannten Verzeichnisse abgelegt wurde, dieser Workflow wurde jedoch noch nicht offiziell von AMD validiert.

## Fehlerbehebung

### Verbindung abgelehnt

Stellen Sie sicher, dass der Server läuft:
```bash
curl http://localhost:8001/health
```

## Zusammenfassung

In diesem Playbook haben Sie gelernt, wie Sie:

- Containerisiertes vLLM mit ROCm-Unterstützung auf der integrierten GPU starten
- Einen vLLM-Server mit OpenAI-kompatiblen API-Endpunkten auf Port 8001 starten
- Prompts mit `vllm-prompt` senden
- API-Aufrufe an den vLLM-Server sowohl mit Streaming- als auch mit Nicht-Streaming-Anfragen durchführen
- Häufige Probleme bei Serverstart, Speicher und Client-Verbindungen beheben

Sie verfügen nun über eine containerisierte vLLM-Bereitstellung zum Servieren großer Sprachmodelle mit optimierter Leistung auf der integrierten GPU.

## Nächste Schritte

- **Verschiedene Modelle ausprobieren** — Verwenden Sie `vllm-launch --model <model>`, um mit unterschiedlichen LLMs zu experimentieren und die Leistung zu vergleichen (siehe [Auswahl und Konfiguration eines Modells](#choosing-and-configuring-a-model)).
- **Eine Anwendung entwickeln** — Nutzen Sie die OpenAI-kompatible API, um vLLM in eine Python-App, einen Chatbot oder einen Automatisierungs-Workflow zu integrieren.
- **Feinabstimmung und Bereitstellung** — Führen Sie eine Feinabstimmung eines Modells mit LoRA oder QLoRA durch und stellen Sie es anschließend mit vLLM für optimierte Inferenz bereit.
## Zusätzliche Ressourcen

- **[vLLM Offizielle Dokumentation](https://docs.vllm.ai/)** — Umfassende Anleitungen und API-Referenzen
- **[vLLM GitHub-Repository](https://github.com/vllm-project/vllm)** — Quellcode, Probleme und Community-Diskussionen
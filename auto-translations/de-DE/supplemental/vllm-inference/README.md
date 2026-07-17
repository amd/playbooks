<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Dieses Playbook verwendet spezielle Tags, die GitHub nicht rendern kann. Bitte besuchen Sie [amd.com/playbooks](https://amd.com/playbooks), um diesen Inhalt korrekt anzuzeigen.
<!-- @github-only:end -->


## Übersicht

vLLM ist eine leistungsstarke Inferenz-Engine für große Sprachmodelle (LLMs). Sie bietet optimiertes Serving mit kontinuierlichem Batching für hohen Durchsatz sowie eine OpenAI-kompatible API für eine nahtlose Anwendungsintegration. Damit eignet sich vLLM hervorragend für Produktionsumgebungen, in denen Geschwindigkeit und Ressourceneffizienz entscheidend sind.

Dieses Playbook zeigt Ihnen, wie Sie LLMs mithilfe von containerisiertem vLLM auf dem integrierten GPU bereitstellen und über die OpenAI Python API mit Modellen interagieren.

## Was Sie lernen werden

- Wie Sie einen vLLM-Server mit AMD ROCm™-Unterstützung einrichten und starten
- Wie Sie über OpenAI-kompatible API-Endpunkte mit Modellen interagieren
- Wie Sie mit `vllm-prompt` Anfragen an den lokalen Server senden

## Speicherkonfiguration festlegen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Auf Software-Updates prüfen

> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es über das AMD Ryzen™ AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-Voraussetzungen installieren

Dieses Playbook verwendet ein vorgefertigtes Container-Image, das vLLM, ROCm-Unterstützung und die Hilfsskripte enthält, die zum Starten des Servers benötigt werden. Sie müssen PyTorch, vLLM oder lokale Playbook-Skripte nicht manuell installieren.

Es gibt keinen hostseitigen vLLM-Installationsschritt. Starten Sie vLLM mit:

```bash
vllm-launch
```

Der Launcher startet den Container, zielt auf den integrierten GPU ab und stellt einen lokalen OpenAI-kompatiblen vLLM-Server bereit. Alternativ können Sie auf das vLLM-Symbol in der Taskleiste klicken.

## Schnellstart

### 1. Bestätigen Sie, dass der vLLM-Server läuft

Das Initialisieren von `vllm-launch` kann einige Minuten dauern. Sobald es gestartet ist, ist der Server unter `http://localhost:8001` verfügbar. Lassen Sie das Launch-Terminal geöffnet, da der Server im Vordergrund läuft, und öffnen Sie dann ein separates Terminal für die verbleibenden Schritte. Die folgenden Beispiele verwenden `Qwen/Qwen3-1.7B`; wenn Ihr Launcher für ein anderes Modell konfiguriert ist, ersetzen Sie diese Modell-ID in den Anfragen.

### 2. Eine Anfrage senden

Verwenden Sie das bereitgestellte `vllm-prompt`-Skript, um eine Anfrage an den lokalen OpenAI-kompatiblen vLLM-Server zu senden:

```bash
vllm-prompt "Tell me a story"
```

### 3. Mit dem Modell über die OpenAI Python API chatten

Da vLLM eine OpenAI-kompatible API bereitstellt, können Sie das `openai` Python-Paket für die Interaktion verwenden.

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

Erstellen Sie einen `OpenAI`-Client, der auf den lokalen vLLM-Server statt auf OpenAIs Server zeigt. Der `api_key` wird vom Client benötigt, aber vLLM validiert ihn nicht, daher funktioniert jede beliebige Zeichenkette:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Senden Sie dann eine Chat-Completion-Anfrage. Diese verwendet dasselbe Nachrichtenformat wie die OpenAI API — eine Liste von Nachrichten mit Rollen wie `"user"` und `"assistant"`. Das Setzen von `stream=True` bedeutet, dass die Antwort schrittweise eintrifft und nicht auf einmal:

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

Das enthaltene Skript [chat_with_model.py](assets/chat_with_model.py) enthält das vollständige Beispiel und kann heruntergeladen werden.


## Fehlerbehebung

### Verbindung abgelehnt

Stellen Sie sicher, dass der Server läuft:
```bash
curl http://localhost:8001/health
```

## Zusammenfassung

In diesem Playbook haben Sie gelernt, wie Sie:

- Containerisiertes vLLM mit ROCm-Unterstützung auf dem integrierten GPU starten
- Einen vLLM-Server mit OpenAI-kompatiblen API-Endpunkten auf Port 8001 starten
- Anfragen mit `vllm-prompt` senden
- API-Aufrufe an den vLLM-Server sowohl mit Streaming als auch ohne Streaming durchführen
- Häufige Probleme beim Serverstart, mit dem Speicher und bei Client-Verbindungen beheben

Sie verfügen nun über eine containerisierte vLLM-Bereitstellung zur Ausführung großer Sprachmodelle mit optimierter Leistung auf dem integrierten GPU.

## Nächste Schritte

- **Verschiedene Modelle ausprobieren** — Tauschen Sie das Modell in der `vllm-launch`-Konfiguration aus, um mit verschiedenen LLMs zu experimentieren und die Leistung zu vergleichen.
- **Eine Anwendung erstellen** — Verwenden Sie die OpenAI-kompatible API, um vLLM in eine Python-App, einen Chatbot oder einen Automatisierungs-Workflow zu integrieren.
- **Feinabstimmung und Bereitstellung** — Führen Sie eine Feinabstimmung eines Modells mit LoRA oder QLoRA durch und stellen Sie es dann mit vLLM für optimierte Inferenz bereit.

## Weitere Ressourcen

- **[Offizielle vLLM-Dokumentation](https://docs.vllm.ai/)** — Umfassende Anleitungen und API-Referenzen
- **[vLLM GitHub-Repository](https://github.com/vllm-project/vllm)** — Quellcode, Issues und Community-Diskussionen
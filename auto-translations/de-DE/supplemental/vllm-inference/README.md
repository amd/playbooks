<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> In diesem Playbook werden spezielle Tags verwendet, die GitHub nicht rendern kann. Bitte besuchen Sie [amd.com/playbooks](https://amd.com/playbooks), um diesen Inhalt korrekt anzuzeigen.
<!-- @github-only:end -->


## Übersicht

vLLM ist eine leistungsstarke Inferenz-Engine für große Sprachmodelle (LLMs). Sie bietet optimiertes Serving mit kontinuierlichem Batching für hohen Durchsatz sowie eine OpenAI-kompatible API für die nahtlose Integration in Anwendungen. Dadurch eignet sich vLLM hervorragend für Produktionsumgebungen, in denen Geschwindigkeit und Ressourceneffizienz entscheidend sind.

Dieses Playbook zeigt Ihnen, wie Sie LLMs mithilfe von containerisiertem vLLM auf der integrierten GPU bereitstellen und über die OpenAI Python API mit Modellen interagieren.

## Was Sie lernen werden

- Wie man einen vLLM-Server mit AMD ROCm™-Unterstützung einrichtet und startet
- Wie man über OpenAI-kompatible API-Endpunkte mit Modellen interagiert
- Wie man mit `vllm-prompt` Prompts an den lokalen Server sendet

## Konfigurieren des Arbeitsspeichers

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Nach Software-Updates suchen

> **Hinweis**: Falls VS Code nicht installiert ist, können Sie es über das AMD Ryzen™ AI Developer Center installieren.

<!-- @require:software-update -->
<!-- @device:end -->

## Software-Voraussetzungen installieren

Dieses Playbook verwendet ein vorgefertigtes Container-Image, das vLLM, ROCm-Unterstützung sowie die zum Starten des Servers benötigten Hilfsskripte enthält. Sie müssen PyTorch, vLLM oder lokale Playbook-Skripte nicht manuell installieren.

Es ist keine hostseitige vLLM-Installation erforderlich. Starten Sie vLLM mit:

```bash
vllm-launch
```

Der Launcher startet den Container, adressiert die integrierte GPU und stellt einen lokalen OpenAI-kompatiblen vLLM-Server bereit. Alternativ können Sie auf das vLLM-Symbol in der Taskleiste klicken.

## Schnellstart

### 1. Überprüfen, ob der vLLM-Server läuft

Der `vllm-launch` benötigt möglicherweise ein paar Minuten, um alles zu initialisieren. Sobald er gestartet ist, ist der Server unter `http://localhost:8001` verfügbar. Lassen Sie das Start-Terminal geöffnet, da der Server im Vordergrund läuft, und öffnen Sie für die restlichen Schritte ein separates Terminal. Die folgenden Beispiele verwenden `Qwen/Qwen3-1.7B`; falls Ihr Launcher für ein anderes Modell konfiguriert ist, ersetzen Sie diese Modell-ID in den Anfragen entsprechend.

### 2. Einen Prompt senden

Verwenden Sie das bereitgestellte `vllm-prompt`-Skript, um eine Anfrage an den lokalen, OpenAI-kompatiblen vLLM-Server zu senden:

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

Erstellen Sie einen `OpenAI`-Client, der auf den lokalen vLLM-Server anstelle der Server von OpenAI verweist. Der `api_key` wird vom Client benötigt, wird von vLLM jedoch nicht validiert, sodass eine beliebige Zeichenfolge funktioniert:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Senden Sie anschließend eine Chat-Completion-Anfrage. Dabei wird dasselbe Nachrichtenformat wie bei der OpenAI-API verwendet — eine Liste von Nachrichten mit Rollen wie `"user"` und `"assistant"`. Durch Setzen von `stream=True` wird die Antwort inkrementell statt auf einmal geliefert:

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

Iterieren Sie abschließend über die gestreamten Chunks und geben Sie jedes eintreffende Textstück aus:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Das mitgelieferte Skript [chat_with_model.py](assets/chat_with_model.py) enthält das vollständige Beispiel und kann heruntergeladen werden.


## Fehlerbehebung

### Verbindung abgelehnt

Stellen Sie sicher, dass der Server läuft:
```bash
curl http://localhost:8001/health
```

## Zusammenfassung

In diesem Playbook haben Sie gelernt, wie man:

- containerisiertes vLLM mit ROCm-Unterstützung auf der integrierten GPU startet
- einen vLLM-Server mit OpenAI-kompatiblen API-Endpunkten auf Port 8001 startet
- Prompts mit `vllm-prompt` sendet
- API-Aufrufe an den vLLM-Server sowohl mit Streaming- als auch mit Nicht-Streaming-Anfragen durchführt
- häufige Probleme beim Serverstart, mit dem Arbeitsspeicher und bei Client-Verbindungen behebt

Sie verfügen nun über eine containerisierte vLLM-Bereitstellung zum Servieren großer Sprachmodelle mit optimierter Leistung auf der integrierten GPU.

## Nächste Schritte

- **Verschiedene Modelle ausprobieren** — Tauschen Sie das Modell in der `vllm-launch`-Konfiguration aus, um mit verschiedenen LLMs zu experimentieren und die Leistung zu vergleichen.
- **Eine Anwendung entwickeln** — Nutzen Sie die OpenAI-kompatible API, um vLLM in eine Python-App, einen Chatbot oder einen Automatisierungsworkflow zu integrieren.
- **Fine-Tuning und Serving** — Führen Sie ein Fine-Tuning eines Modells mit LoRA oder QLoRA durch und stellen Sie es anschließend mit vLLM für optimierte Inferenz bereit.

## Weitere Ressourcen

- **[Offizielle vLLM-Dokumentation](https://docs.vllm.ai/)** — Umfassende Anleitungen und API-Referenzen
- **[vLLM GitHub-Repository](https://github.com/vllm-project/vllm)** — Quellcode, Issues und Community-Diskussionen
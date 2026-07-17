<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Översikt

vLLM är en högpresterande inferensmotor utformad för stora språkmodeller (LLM:er). Den erbjuder optimerad serving med kontinuerlig batchning för hög genomströmning samt ett OpenAI-kompatibelt API för sömlös applikationsintegration. Detta gör vLLM utmärkt för produktionsdriftsättningar där hastighet och resurseffektivitet är avgörande.

Den här playbooken lär dig hur du servar LLM:er med containeriserad vLLM på den integrerade GPU:n och interagerar med modeller via OpenAI Python API.

## Vad du kommer att lära dig

- Hur du konfigurerar och startar en vLLM-server med AMD ROCm™-stöd
- Hur du interagerar med modeller via OpenAI-kompatibla API-endpoints
- Hur du skickar promptar till den lokala servern med `vllm-prompt`

## Ange minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programvaruuppdateringar

> **Obs**: Om VS Code inte är installerat kan du installera det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändiga programvaruförutsättningar

Den här playbooken använder en förbyggd containeravbildning som inkluderar vLLM, ROCm-stöd och hjälpskript som behövs för att starta servern. Du behöver inte installera PyTorch, vLLM eller lokala playbook-skript manuellt.

Det finns inget vLLM-installationssteg på värdsidan. Starta vLLM med:

```bash
vllm-launch
```

Startprogrammet startar containern, riktar in sig på den integrerade GPU:n och exponerar en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klicka på vLLM-ikonen i aktivitetsfältet.

## Snabbstart

### 1. Bekräfta att vLLM-servern körs

`vllm-launch` kan ta ett par minuter att initiera allt. När den väl startar är servern tillgänglig på `http://localhost:8001`. Håll startterminalen öppen eftersom servern körs i förgrunden, öppna sedan en separat terminal för de återstående stegen. Exemplen nedan använder `Qwen/Qwen3-1.7B`; om ditt startprogram är konfigurerat för en annan modell, ersätt det modell-ID:t i förfrågningarna.

### 2. Skicka en prompt

Använd det medföljande `vllm-prompt`-skriptet för att skicka en förfrågan till den lokala vLLM OpenAI-kompatibla servern:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatta med modellen med hjälp av OpenAI Python API

Eftersom vLLM exponerar ett OpenAI-kompatibelt API kan du använda Python-paketet `openai` för att interagera med det.

Skapa först en virtuell Python-miljö:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Installera OpenAI-paketet
```bash
pip install openai
```

Skapa en `OpenAI`-klient som pekar på den lokala vLLM-servern istället för OpenAI:s servrar. `api_key` krävs av klienten men vLLM validerar den inte, så vilken sträng som helst fungerar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Skicka sedan en chattavslutningsförfrågan. Denna använder samma meddelandeformat som OpenAI API — en lista med meddelanden med roller som `"user"` och `"assistant"`. Att ange `stream=True` innebär att svaret anländer stegvis snarare än allt på en gång:

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

Iterera slutligen över de strömmade delarna och skriv ut varje textbit när den anländer:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medföljande skriptet [chat_with_model.py](assets/chat_with_model.py) innehåller hela exemplet och kan laddas ned.


## Felsökning

### Anslutning nekad

Kontrollera att servern körs:
```bash
curl http://localhost:8001/health
```

## Sammanfattning

I den här playbooken lärde du dig hur du:

- Startar containeriserad vLLM med ROCm-stöd på den integrerade GPU:n
- Startar en vLLM-server med OpenAI-kompatibla API-endpoints på port 8001
- Skickar promptar med `vllm-prompt`
- Gör API-anrop till vLLM-servern med både strömmande och icke-strömmande förfrågningar
- Felsöker vanliga problem med serverstart, minne och klientanslutningar

Du har nu en containeriserad vLLM-driftsättning för att serva stora språkmodeller med optimerad prestanda på den integrerade GPU:n.

## Nästa steg

- **Prova olika modeller** — Byt ut modellen i `vllm-launch`-konfigurationen för att experimentera med olika LLM:er och jämföra prestanda.
- **Bygg en applikation** — Använd det OpenAI-kompatibla API:et för att integrera vLLM i en Python-app, chattbot eller automatiseringsarbetsflöde.
- **Finjustera och serva** — Finjustera en modell med LoRA eller QLoRA och driftsätt den sedan med vLLM för optimerad inferens.

## Ytterligare resurser

- **[vLLM officiell dokumentation](https://docs.vllm.ai/)** — Omfattande guider och API-referenser
- **[vLLM GitHub-arkiv](https://github.com/vllm-project/vllm)** — Källkod, ärenden och gemenskapsdiskussioner
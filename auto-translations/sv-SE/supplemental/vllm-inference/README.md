<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Denna spelbok använder speciella taggar som GitHub inte kan rendera. Besök [amd.com/playbooks](https://amd.com/playbooks) för att förhandsgranska detta innehåll korrekt.
<!-- @github-only:end -->


## Översikt

vLLM är en högpresterande inferensmotor utformad för stora språkmodeller (LLM). Den erbjuder optimerad servering med kontinuerlig batchning för hög genomströmning och ett OpenAI-kompatibelt API för sömlös applikationsintegration. Detta gör vLLM utmärkt för produktionsdistributioner där hastighet och resurseffektivitet är avgörande.

Den här spelboken lär dig hur du serverar LLM:er med containeriserad vLLM på den integrerade GPU:n och interagerar med modeller via OpenAI Python-API:et.

## Vad du kommer att lära dig

- Hur du konfigurerar och startar en vLLM-server med stöd för AMD ROCm™
- Hur du interagerar med modeller via OpenAI-kompatibla API-slutpunkter
- Hur du skickar prompter till den lokala servern med `vllm-prompt`

## Konfiguration av minne

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

> **Obs**: Om VS Code inte är installerat kan du installera det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

Den här spelboken använder en förbyggd containeravbildning som innehåller vLLM, ROCm-stöd och de hjälpskript som behövs för att starta servern. Du behöver inte installera PyTorch, vLLM eller lokala spelboksskript manuellt.

Det finns inget installationssteg för vLLM på värdsidan. Starta vLLM med:

```bash
vllm-launch
```

Startprogrammet startar containern, riktar in sig på den integrerade GPU:n och exponerar en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klicka på vLLM-ikonen i aktivitetsfältet.

## Snabbstart

### 1. Bekräfta att vLLM-servern körs

Det kan ta ett par minuter för `vllm-launch` att initiera allt. När den har startat är servern tillgänglig på `http://localhost:8001`. Håll starterminalen öppen eftersom servern körs i förgrunden, och öppna sedan en separat terminal för de återstående stegen. Exemplen nedan använder `Qwen/Qwen3-1.7B`; om ditt startprogram är konfigurerat för en annan modell ska du ersätta det modell-ID:t i förfrågningarna.

### 2. Skicka en prompt

Använd det medföljande skriptet `vllm-prompt` för att skicka en förfrågan till den lokala OpenAI-kompatibla vLLM-servern:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatta med modellen med OpenAI Python-API:et

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

Skapa en `OpenAI`-klient som pekar mot den lokala vLLM-servern istället för OpenAIs servrar. `api_key` krävs av klienten, men vLLM validerar den inte, så vilken sträng som helst fungerar:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Skicka sedan en chattkomplettering. Detta använder samma meddelandeformat som OpenAI-API:et — en lista med meddelanden med roller som `"user"` och `"assistant"`. Genom att sätta `stream=True` kommer svaret att komma inkrementellt istället för på en gång:

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

Slutligen itererar du över de strömmade delarna och skriver ut varje textbit när den kommer in:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medföljande skriptet [chat_with_model.py](assets/chat_with_model.py) innehåller hela exemplet och kan laddas ner.


## Felsökning

### Anslutning nekad

Se till att servern körs:
```bash
curl http://localhost:8001/health
```

## Sammanfattning

I den här spelboken lärde du dig hur du:

- Startar containeriserad vLLM med ROCm-stöd på den integrerade GPU:n
- Startar en vLLM-server med OpenAI-kompatibla API-slutpunkter på port 8001
- Skickar prompter med `vllm-prompt`
- Gör API-anrop till vLLM-servern med både strömmande och icke-strömmande förfrågningar
- Felsöker vanliga problem med serverstart, minne och klientanslutningar

Du har nu en containeriserad vLLM-distribution för att servera stora språkmodeller med optimerad prestanda på den integrerade GPU:n.

## Nästa steg

- **Prova olika modeller** — Byt ut modellen i konfigurationen för `vllm-launch` för att experimentera med olika LLM:er och jämföra prestanda.
- **Bygg en applikation** — Använd det OpenAI-kompatibla API:et för att integrera vLLM i en Python-app, chattbot eller automationsflöde.
- **Finjustera och servera** — Finjustera en modell med LoRA eller QLoRA, och distribuera den sedan med vLLM för optimerad inferens.

## Ytterligare resurser

- **[vLLM officiell dokumentation](https://docs.vllm.ai/)** — Omfattande guider och API-referenser
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Källkod, ärenden och community-diskussioner
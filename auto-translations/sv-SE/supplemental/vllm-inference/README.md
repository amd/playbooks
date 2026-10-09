<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa instruktioner, kommandon, nedladdningar, produkttillgänglighet eller annat innehåll kan variera beroende på språk eller region. Vid eventuella motsägelser eller avvikelser är det den ursprungliga engelska versionen av playbook som gäller och har företräde.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Översikt

vLLM är en högpresterande inferensmotor designad för stora språkmodeller (LLM). Den tillhandahåller optimerad servering med kontinuerlig batchning för hög genomströmning och ett OpenAI-kompatibelt API för smidig applikationsintegration. Detta gör vLLM utmärkt för produktionsdistributioner där hastighet och resurseffektivitet är avgörande.

Den här handledningen lär dig hur du serverar LLM:er med containeriserad vLLM på den integrerade GPU:n och interagerar med modeller via OpenAI Python API.

## Vad du kommer att lära dig

- Hur du konfigurerar och startar en vLLM-server med stöd för AMD ROCm™
- Hur du interagerar med modeller via OpenAI-kompatibla API-slutpunkter
- Hur du skickar prompter till den lokala servern med `vllm-prompt`

## Ställa in minneskonfigurationen

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrollera om det finns programuppdateringar

> **Obs**: Om VS Code inte är installerat kan du installera det med AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Installera nödvändig programvara

vLLM körs i en förbyggd container med ROCm och dess beroenden redan matchade. Ingen ytterligare installation krävs.

Det finns inget installationssteg för vLLM på värdsidan. Starta vLLM med:

```bash
vllm-launch
```

Startprogrammet startar containern, riktar in sig på den integrerade GPU:n och exponerar en lokal OpenAI-kompatibel vLLM-server. Alternativt kan du klicka på vLLM-ikonen i aktivitetsfältet.

## Snabbstart

### 1. Bekräfta att vLLM-servern körs

`vllm-launch` kan ta ett par minuter att initiera allt. När den har startat är servern tillgänglig på `http://localhost:8001`. Håll startterminalen öppen eftersom servern körs i förgrunden, öppna sedan en separat terminal för de återstående stegen. Exemplen nedan använder `Qwen/Qwen3-1.7B`; om ditt startprogram är konfigurerat för en annan modell, ersätt det med det modell-ID:t i förfrågningarna.

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
<!-- @os:end -->

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

Skicka sedan en chattkomplettering-förfrågan. Detta använder samma meddelandeformat som OpenAI API — en lista med meddelanden med roller som `"user"` och `"assistant"`. Om `stream=True` ställs in kommer svaret att komma gradvis istället för allt på en gång:

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

Iterera slutligen över de strömmade bitarna och skriv ut varje textdel allteftersom den tas emot:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Det medföljande skriptet [chat_with_model.py](assets/chat_with_model.py) innehåller hela exemplet och kan laddas ned.


## Välja och konfigurera en modell

Som standard serverar `vllm-launch` `Qwen/Qwen3-1.7B` som en testmodell på port `8001`. Du kan ändra modellen, porten och vLLM-serveringsparametrarna utan att bygga om eller redigera containern.

### Modeller testade av AMD

Följande modeller är förkonfigurerade och validerade av AMD:

| Modell | Anteckningar |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Standardmodell. Lättviktig och snabb att läsa in. |
| `openai/gpt-oss-20b` | Större modell för svar av högre kvalitet. |

### Starta en annan modell

Ange modell-ID med `--model` (eller `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Ändra porten

Ange en port över 1024 med `--port` (eller `-p`); standardvärdet är `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Om du ändrar porten, se till att din klients `base_url` pekar mot samma port (till exempel `http://localhost:8080/v1`).

### Skicka med extra vLLM-parametrar

Alla ytterligare argument vidarebefordras direkt till vLLM, så du kan finjustera serveringsbeteende som kontextlängd eller datatyp. Det finns två sätt att ange dem.

**Infogat**, efter startprogrammets alternativ:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Permanent**, i en konfigurationsfil på `~/.local/share/vLLM/vllm-launch.conf`. Denna fil finns inte som standard — skapa den och lägg till dina argument som en Bash-array:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Använd `+=` för att lägga till standardargumenten istället för att ersätta dem:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

För att se alla startprogramalternativ när som helst, kör:

```bash
vllm-launch --help
```

### Var modeller lagras

`vllm-launch` letar efter modeller på två platser:

| Plats | Sökväg |
|----------|------|
| Systemmodeller | `/var/cache/models` |
| Användarmodeller | `~/.local/share/vLLM/models` |

Du kan placera en nedladdad modell i endera katalogen och starta den genom att ange dess sökväg eller ID till `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Obs**: Att köra din egen nedladdade modell på detta sätt förväntas fungera när modellen har placerats i en av katalogerna ovan, men detta arbetsflöde har ännu inte officiellt validerats av AMD.

## Felsökning

### Anslutning nekad

Se till att servern körs:
```bash
curl http://localhost:8001/health
```

## Sammanfattning

I den här handledningen lärde du dig hur du:

- Startar containeriserad vLLM med stöd för ROCm på den integrerade GPU:n
- Startar en vLLM-server med OpenAI-kompatibla API-slutpunkter på port 8001
- Skickar prompter med `vllm-prompt`
- Gör API-anrop till vLLM-servern med både strömmande och icke-strömmande förfrågningar
- Felsöker vanliga problem med serverstart, minne och klientanslutningar

Du har nu en containeriserad vLLM-distribution för att servera stora språkmodeller med optimerad prestanda på den integrerade GPU:n.

## Nästa steg

- **Prova olika modeller** — Använd `vllm-launch --model <model>` för att experimentera med olika LLM:er och jämföra prestanda (se [Välja och konfigurera en modell](#choosing-and-configuring-a-model)).
- **Bygg en applikation** — Använd det OpenAI-kompatibla API:et för att integrera vLLM i en Python-app, chattbot eller automatiseringsarbetsflöde.
- **Finjustera och servera** — Finjustera en modell med LoRA eller QLoRA, och distribuera den sedan med vLLM för optimerad inferens.
## Ytterligare resurser

- **[vLLM officiella dokumentation](https://docs.vllm.ai/)** — Omfattande guider och API-referenser
- **[vLLM GitHub-repository](https://github.com/vllm-project/vllm)** — Källkod, ärenden och communitydiskussioner
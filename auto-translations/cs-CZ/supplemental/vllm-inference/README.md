<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->
## Přehled

vLLM je vysoce výkonný inferenční engine navržený pro velké jazykové modely (LLM). Poskytuje optimalizované servírování s kontinuálním dávkováním pro vysokou propustnost a API kompatibilní s OpenAI pro bezproblémovou integraci aplikací. Díky tomu je vLLM skvělou volbou pro produkční nasazení, kde jsou klíčové rychlost a efektivní využití zdrojů.

Tato příručka vás naučí, jak servírovat LLM pomocí kontejnerizovaného vLLM na integrovaném GPU a jak interagovat s modely prostřednictvím Python API OpenAI.

## Co se naučíte

- Jak nastavit a spustit vLLM server s podporou AMD ROCm™
- Jak interagovat s modely přes API koncové body kompatibilní s OpenAI
- Jak odesílat prompty na lokální server pomocí `vllm-prompt`

## Nastavení konfigurace paměti
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

> **Poznámka**: Pokud VS Code není nainstalován, můžete jej nainstalovat pomocí AMD Ryzen™ AI Developer Center.
<!-- @require:software-update -->
<!-- @device:end -->
## Instalace softwarových předpokladů

vLLM běží v předpřipraveném kontejneru s ROCm a jeho závislostmi, které jsou předem sladěny. Není nutná žádná další instalace.

Na straně hostitele neexistuje žádný instalační krok pro vLLM. Spusťte vLLM pomocí:

```bash
vllm-launch
```

Launcher spustí kontejner, cílí na integrovanou GPU a zpřístupní lokální OpenAI-kompatibilní vLLM server. Případně klikněte na ikonu vLLM na hlavním panelu.

## Rychlý start

### 1. Ověřte, že vLLM server běží

Inicializace všeho pomocí `vllm-launch` může trvat několik minut. Jakmile se spustí, server je dostupný na adrese `http://localhost:8001`. Terminál se spuštěním nechte otevřený, protože server běží na popředí, a poté otevřete samostatný terminál pro zbývající kroky. Níže uvedené příklady používají `Qwen/Qwen3-1.7B`; pokud je váš launcher nakonfigurován pro jiný model, nahraďte v požadavcích odpovídajícím ID modelu.

### 2. Odešlete prompt

Pomocí přiloženého skriptu `vllm-prompt` odešlete požadavek na lokální OpenAI-kompatibilní vLLM server:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatujte s modelem pomocí OpenAI Python API

Jelikož vLLM poskytuje API kompatibilní s OpenAI, můžete k interakci s ním použít balíček `openai` pro Python.

Nejprve vytvořte virtuální prostředí Pythonu:
<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->
Nainstalujte balíček OpenAI
```bash
pip install openai
```

Vytvořte klienta `OpenAI` nasměrovaného na místní server vLLM namísto serverů OpenAI. Klient vyžaduje `api_key`, ale vLLM jej neověřuje, takže funguje libovolný řetězec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Poté odešlete požadavek na dokončení chatu (chat completion request). Ten používá stejný formát zpráv jako OpenAI API — seznam zpráv s rolemi jako `"user"` a `"assistant"`. Nastavení `stream=True` znamená, že odpověď bude přicházet postupně, nikoli najednou:

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

Nakonec iterujte přes streamovaná data (chunks) a vypisujte jednotlivé části textu, jak postupně přicházejí:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Přiložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý příklad a lze jej stáhnout.

## Výběr a konfigurace modelu

Ve výchozím nastavení `vllm-launch` poskytuje `Qwen/Qwen3-1.7B` jako testovací model na portu `8001`. Model, port a parametry vLLM serving můžete změnit bez nutnosti kontejner znovu sestavovat nebo upravovat.

### Modely testované společností AMD

Následující modely jsou předkonfigurované a ověřené společností AMD:

| Model | Poznámky |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Výchozí model. Odlehčený a rychlý na načtení. |
| `openai/gpt-oss-20b` | Větší model pro kvalitnější odpovědi. |

### Spuštění jiného modelu

Předejte ID modelu pomocí `--model` (nebo `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Změna portu

Předejte port vyšší než 1024 pomocí `--port` (nebo `-p`); výchozí hodnota je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Pokud port změníte, nasměrujte `base_url` svého klienta na stejný port (například `http://localhost:8080/v1`).

### Předávání dalších parametrů vLLM

Jakékoli další argumenty jsou přeposlány přímo do vLLM, takže můžete doladit chování serveru, například délku kontextu nebo datový typ. Existují dva způsoby, jak je zadat.

**Vložené (inline)**, za možnostmi spouštěče:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trvale**, v konfiguračním souboru na `~/.local/share/vLLM/vllm-launch.conf`. Tento soubor ve výchozím stavu neexistuje – vytvořte jej a přidejte své argumenty jako pole Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Pomocí `+=` připojíte hodnoty k výchozím argumentům, místo abyste je nahradili:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Chcete-li kdykoli zobrazit všechny možnosti spouštěče, spusťte:

```bash
vllm-launch --help
```

### Kam se ukládají modely

`vllm-launch` hledá modely na dvou místech:

| Umístění | Cesta |
|----------|------|
| Systémové modely | `/var/cache/models` |
| Uživatelské modely | `~/.local/share/vLLM/models` |

Stažený model můžete umístit do kteréhokoli z těchto adresářů a spustit jej předáním jeho cesty nebo ID parametru `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

**Poznámka**: Spuštění vlastního staženého modelu tímto způsobem by mělo fungovat, jakmile je model umístěn v jednom z výše uvedených adresářů, ale tento pracovní postup zatím nebyl oficiálně ověřen společností AMD.

## Řešení problémů

### Spojení odmítnuto

Ujistěte se, že server běží:
```bash
curl http://localhost:8001/health
```

## Shrnutí

V tomto playbooku jste se naučili:

- Spustit kontejnerizovaný vLLM s podporou ROCm na integrovaném GPU
- Spustit server vLLM s koncovými body API kompatibilními s OpenAI na portu 8001
- Odesílat prompty pomocí `vllm-prompt`
- Provádět volání API na server vLLM pomocí jak streamovaných, tak nestreamovaných požadavků
- Řešit běžné problémy se spuštěním serveru, pamětí a připojením klienta

Nyní máte k dispozici kontejnerizované nasazení vLLM pro poskytování velkých jazykových modelů s optimalizovaným výkonem na integrovaném GPU.

## Další kroky

- **Vyzkoušejte různé modely** — Pomocí `vllm-launch --model <model>` experimentujte s různými LLM a porovnejte výkon (viz [Výběr a konfigurace modelu](#choosing-and-configuring-a-model)).
- **Vytvořte aplikaci** — Použijte API kompatibilní s OpenAI k integraci vLLM do aplikace v Pythonu, chatbota nebo automatizovaného pracovního postupu.
- **Doladění a nasazení** — Doladíte model pomocí LoRA nebo QLoRA a poté jej nasadíte pomocí vLLM pro optimalizovanou inferenci.
## Další zdroje

- **[Oficiální dokumentace vLLM](https://docs.vllm.ai/)** — Komplexní návody a reference k API
- **[Repozitář vLLM na GitHubu](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskuze komunity
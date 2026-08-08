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

vLLM je vysoce výkonný inferenční engine navržený pro velké jazykové modely (LLM). Poskytuje optimalizované obsluhování pomocí kontinuálního dávkování pro vysokou propustnost a OpenAI kompatibilní API pro bezproblémovou integraci aplikací. Díky tomu je vLLM skvělou volbou pro produkční nasazení, kde jsou klíčové rychlost a efektivita využití zdrojů.

Tento playbook vás naučí, jak obsluhovat LLM pomocí kontejnerizovaného vLLM na integrovaném GPU a jak komunikovat s modely prostřednictvím OpenAI Python API.

## Co se naučíte

- Jak nastavit a spustit vLLM server s podporou AMD ROCm™
- Jak komunikovat s modely přes koncové body kompatibilní s OpenAI API
- Jak odesílat prompty na lokální server pomocí `vllm-prompt`

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

> **Poznámka**: Pokud VS Code není nainstalováno, můžete jej nainstalovat pomocí AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

vLLM běží v předpřipraveném kontejneru s ROCm a jeho závislostmi, které jsou již sladěné. Není potřeba žádná další instalace.

Není potřeba žádný krok instalace vLLM na straně hostitele. Spusťte vLLM pomocí:

```bash
vllm-launch
```

Spouštěč (launcher) spustí kontejner, zacílí na integrované GPU a zpřístupní lokální OpenAI kompatibilní vLLM server. Alternativně můžete kliknout na ikonu vLLM v hlavním panelu.

## Rychlý start

### 1. Ověřte, že server vLLM běží

Spuštění pomocí `vllm-launch` může trvat pár minut, než se vše inicializuje. Jakmile se spustí, server je dostupný na adrese `http://localhost:8001`. Nechte terminál se spouštěním otevřený, protože server běží na popředí, a otevřete samostatný terminál pro zbývající kroky. Následující příklady používají `Qwen/Qwen3-1.7B`; pokud je váš spouštěč nakonfigurován pro jiný model, nahraďte v požadavcích toto ID modelu.

### 2. Odešlete prompt

Použijte poskytnutý skript `vllm-prompt` k odeslání požadavku na lokální OpenAI kompatibilní server vLLM:

```bash
vllm-prompt "Tell me a story"
```

### 3. Komunikace s modelem pomocí OpenAI Python API

Jelikož vLLM poskytuje OpenAI kompatibilní API, můžete k interakci s ním použít Python balíček `openai`.

Nejprve vytvořte virtuální prostředí Pythonu:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Nainstalujte balíček OpenAI
```bash
pip install openai
```

Vytvořte klienta `OpenAI` směřujícího na lokální server vLLM namísto serverů OpenAI. Klient vyžaduje `api_key`, ale vLLM jej neověřuje, takže funguje jakýkoli řetězec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Poté odešlete požadavek na dokončení chatu (chat completion). Používá se stejný formát zpráv jako u OpenAI API — seznam zpráv s rolemi jako `"user"` a `"assistant"`. Nastavení `stream=True` znamená, že odpověď bude přicházet postupně, nikoli najednou:

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

Nakonec projděte streamované fragmenty a vypište každou část textu, jakmile dorazí:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Přiložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý příklad a lze jej stáhnout.


## Výběr a konfigurace modelu

Ve výchozím nastavení `vllm-launch` obsluhuje `Qwen/Qwen3-1.7B` jako testovací model na portu `8001`. Model, port a parametry obsluhy vLLM můžete změnit bez opětovného sestavení nebo úpravy kontejneru.

### Modely testované AMD

Následující modely jsou předkonfigurované a ověřené společností AMD:

| Model | Poznámky |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Výchozí model. Odlehčený a rychlý pro načítání. |
| `openai/gpt-oss-20b` | Větší model pro kvalitnější odpovědi. |

### Spuštění jiného modelu

Předejte ID modelu pomocí `--model` (nebo `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Změna portu

Předejte port vyšší než 1024 pomocí `--port` (nebo `-p`); výchozí je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Pokud port změníte, nasměrujte `base_url` klienta na stejný port (například `http://localhost:8080/v1`).

### Předávání dalších parametrů vLLM

Veškeré další argumenty jsou přeposílány přímo do vLLM, takže můžete ladit chování obsluhy, jako je délka kontextu nebo datový typ. Existují dva způsoby, jak je zadat.

**Inline**, za volbami spouštěče:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trvale**, v konfiguračním souboru `~/.local/share/vLLM/vllm-launch.conf`. Tento soubor ve výchozím stavu neexistuje — vytvořte jej a přidejte své argumenty jako pole Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Použijte `+=` k připojení k výchozím argumentům namísto jejich nahrazení:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Chcete-li kdykoli zobrazit všechny možnosti spouštěče, spusťte:

```bash
vllm-launch --help
```

### Kde jsou modely uloženy

`vllm-launch` hledá modely na dvou místech:

| Umístění | Cesta |
|----------|------|
| Systémové modely | `/var/cache/models` |
| Uživatelské modely | `~/.local/share/vLLM/models` |

Stažený model můžete umístit do kteréhokoli z těchto adresářů a spustit jej předáním jeho cesty nebo ID parametru `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Poznámka**: Očekává se, že spuštění vlastního staženého modelu tímto způsobem bude fungovat, jakmile je model umístěn do jednoho z výše uvedených adresářů, ale tento postup zatím nebyl oficiálně ověřen společností AMD.

## Řešení problémů

### Connection refused

Ujistěte se, že server běží:
```bash
curl http://localhost:8001/health
```

## Shrnutí

V tomto playbooku jste se naučili, jak:

- Spustit kontejnerizované vLLM s podporou ROCm na integrovaném GPU
- Spustit server vLLM s koncovými body kompatibilními s OpenAI API na portu 8001
- Odesílat prompty pomocí `vllm-prompt`
- Provádět volání API na server vLLM pomocí streamovaných i nestreamovaných požadavků
- Řešit běžné problémy se spuštěním serveru, pamětí a připojením klienta

Nyní máte kontejnerizované nasazení vLLM pro obsluhu velkých jazykových modelů s optimalizovaným výkonem na integrovaném GPU.

## Další kroky

- **Vyzkoušejte různé modely** — Použijte `vllm-launch --model <model>` k experimentování s různými LLM a porovnání výkonu (viz [Výběr a konfigurace modelu](#choosing-and-configuring-a-model)).
- **Vytvořte aplikaci** — Použijte OpenAI kompatibilní API k integraci vLLM do Python aplikace, chatbota nebo automatizovaného pracovního postupu.
- **Doladit a nasadit** — Doladit model pomocí LoRA nebo QLoRA a poté jej nasadit pomocí vLLM pro optimalizovanou inferenci.
## Další zdroje

- **[Oficiální dokumentace vLLM](https://docs.vllm.ai/)** — Komplexní příručky a odkazy na API
- **[Repozitář vLLM na GitHubu](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskuze komunity
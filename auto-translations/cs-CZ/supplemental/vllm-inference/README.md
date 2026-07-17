<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální tagy, které GitHub nedokáže zobrazit. Pro správné zobrazení tohoto obsahu navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Přehled

vLLM je vysoce výkonný inferenční engine navržený pro velké jazykové modely (LLM). Poskytuje optimalizované nasazení s kontinuálním dávkováním pro vysokou propustnost a OpenAI-kompatibilní API pro bezproblémovou integraci aplikací. Díky tomu je vLLM skvělý pro produkční nasazení, kde jsou klíčové rychlost a efektivita využití zdrojů.

Tento playbook vás naučí, jak obsluhovat LLM pomocí kontejnerizovaného vLLM na integrovaném GPU a jak komunikovat s modely prostřednictvím OpenAI Python API.

## Co se naučíte

- Jak nastavit a spustit server vLLM s podporou AMD ROCm™
- Jak komunikovat s modely prostřednictvím OpenAI-kompatibilních API endpointů
- Jak odesílat prompty na lokální server pomocí `vllm-prompt`

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

> **Poznámka**: Pokud VS Code není nainstalován, můžete ho nainstalovat pomocí AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

Tento playbook používá předpřipravený obraz kontejneru, který obsahuje vLLM, podporu ROCm a pomocné skripty potřebné ke spuštění serveru. Není třeba ručně instalovat PyTorch, vLLM ani lokální skripty playbooku.

Na straně hostitele není žádný krok instalace vLLM. Spusťte vLLM pomocí:

```bash
vllm-launch
```

Spouštěč nastartuje kontejner, zacílí na integrovaný GPU a zpřístupní lokální OpenAI-kompatibilní server vLLM. Případně klikněte na ikonu vLLM v hlavním panelu.

## Rychlý start

### 1. Ověřte, že server vLLM běží

Inicializace `vllm-launch` může trvat několik minut. Po spuštění je server dostupný na adrese `http://localhost:8001`. Nechte spouštěcí terminál otevřený, protože server běží v popředí, a pro zbývající kroky otevřete samostatný terminál. Níže uvedené příklady používají `Qwen/Qwen3-1.7B`; pokud je váš spouštěč nakonfigurován pro jiný model, nahraďte v požadavcích toto ID modelu.

### 2. Odeslání promptu

Pomocí poskytnutého skriptu `vllm-prompt` odešlete požadavek na lokální OpenAI-kompatibilní server vLLM:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatování s modelem pomocí OpenAI Python API

Protože vLLM zpřístupňuje OpenAI-kompatibilní API, můžete k interakci s ním použít balíček `openai` pro Python.

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

Vytvořte klienta `OpenAI` nasměrovaného na lokální server vLLM místo serverů OpenAI. Parametr `api_key` je klientem vyžadován, ale vLLM ho neověřuje, takže postačí libovolný řetězec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Poté odešlete požadavek na dokončení chatu. Používá stejný formát zpráv jako OpenAI API — seznam zpráv s rolemi jako `"user"` a `"assistant"`. Nastavení `stream=True` znamená, že odpověď bude přicházet postupně, nikoli najednou:

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

Nakonec iterujte přes streamované části a vytiskněte každý kousek textu při jeho příchodu:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Přiložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý příklad a lze ho stáhnout.


## Řešení problémů

### Odmítnuté připojení

Ujistěte se, že server běží:
```bash
curl http://localhost:8001/health
```

## Shrnutí

V tomto playbooku jste se naučili, jak:

- Spustit kontejnerizovaný vLLM s podporou ROCm na integrovaném GPU
- Spustit server vLLM s OpenAI-kompatibilními API endpointy na portu 8001
- Odesílat prompty pomocí `vllm-prompt`
- Volat API serveru vLLM pomocí streamovaných i nestreamovaných požadavků
- Řešit běžné problémy se spuštěním serveru, pamětí a připojeními klientů

Nyní máte kontejnerizované nasazení vLLM pro obsluhu velkých jazykových modelů s optimalizovaným výkonem na integrovaném GPU.

## Další kroky

- **Vyzkoušejte různé modely** — Vyměňte model v konfiguraci `vllm-launch` a experimentujte s různými LLM a porovnávejte výkon.
- **Vytvořte aplikaci** — Použijte OpenAI-kompatibilní API k integraci vLLM do Python aplikace, chatbota nebo automatizačního workflow.
- **Dolaďte a nasaďte** — Dolaďte model pomocí LoRA nebo QLoRA a poté ho nasaďte s vLLM pro optimalizovanou inferenci.

## Další zdroje

- **[Oficiální dokumentace vLLM](https://docs.vllm.ai/)** — Komplexní průvodci a reference API
- **[Repozitář vLLM na GitHub](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a komunitní diskuse
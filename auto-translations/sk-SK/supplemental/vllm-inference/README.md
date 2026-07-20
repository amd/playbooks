<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->

> [!IMPORTANT]
> Táto príručka používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Ak chcete tento obsah zobraziť správne, navštívte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Prehľad

vLLM je vysoko výkonný inferenčný nástroj navrhnutý pre veľké jazykové modely (LLM). Poskytuje optimalizované poskytovanie služieb s priebežným dávkovaním pre vysokú priepustnosť a rozhranie API kompatibilné s OpenAI pre bezproblémovú integráciu aplikácií. Vďaka tomu je vLLM skvelou voľbou pre produkčné nasadenia, kde je kľúčová rýchlosť a efektívne využívanie zdrojov.

Táto príručka vás naučí, ako poskytovať LLM pomocou kontajnerizovaného vLLM na integrovanej GPU a ako komunikovať s modelmi prostredníctvom OpenAI Python API.

## Čo sa naučíte

- Ako nastaviť a spustiť server vLLM s podporou AMD ROCm™
- Ako komunikovať s modelmi prostredníctvom koncových bodov API kompatibilných s OpenAI
- Ako odosielať výzvy na lokálny server pomocou `vllm-prompt`

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

> **Poznámka**: Ak nemáte nainštalovaný VS Code, môžete ho nainštalovať pomocou AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

Táto príručka používa vopred zostavený obraz kontajnera, ktorý zahŕňa vLLM, podporu ROCm a pomocné skripty potrebné na spustenie servera. Nie je potrebné manuálne inštalovať PyTorch, vLLM ani lokálne skripty príručky.

Neexistuje žiadny krok inštalácie vLLM na strane hostiteľa. Spustite vLLM pomocou:

```bash
vllm-launch
```

Spúšťač spustí kontajner, zacieli na integrovanú GPU a sprístupní lokálny server vLLM kompatibilný s OpenAI. Alternatívne kliknite na ikonu vLLM na paneli úloh.

## Rýchly štart

### 1. Potvrďte, že server vLLM beží

Príkazu `vllm-launch` môže inicializácia všetkého trvať niekoľko minút. Po spustení je server dostupný na adrese `http://localhost:8001`. Nechajte terminál so spusteným serverom otvorený, pretože server beží na popredí, a na zvyšné kroky si otvorte samostatný terminál. Nižšie uvedené príklady používajú `Qwen/Qwen3-1.7B`; ak je váš spúšťač nakonfigurovaný pre iný model, v požiadavkách nahraďte príslušným ID modelu.

### 2. Odošlite výzvu

Na odoslanie požiadavky na lokálny server vLLM kompatibilný s OpenAI použite priložený skript `vllm-prompt`:

```bash
vllm-prompt "Tell me a story"
```

### 3. Komunikujte s modelom pomocou OpenAI Python API

Keďže vLLM poskytuje rozhranie API kompatibilné s OpenAI, môžete na komunikáciu s ním použiť balík `openai` pre Python.

Najprv vytvorte virtuálne prostredie Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Nainštalujte balík OpenAI
```bash
pip install openai
```

Vytvorte klienta `OpenAI` nasmerovaného na lokálny server vLLM namiesto serverov OpenAI. Klient vyžaduje `api_key`, ale vLLM ho neoveruje, takže funguje akýkoľvek reťazec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Následne odošlite požiadavku na dokončenie chatu. Tá používa rovnaký formát správ ako API OpenAI — zoznam správ s rolami ako `"user"` a `"assistant"`. Nastavenie `stream=True` znamená, že odpoveď bude prichádzať postupne, nie naraz:

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

Nakoniec prejdite streamované časti a vypíšte každú časť textu hneď, ako prichádza:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý príklad a je možné ho stiahnuť.


## Riešenie problémov

### Connection refused

Uistite sa, že server beží:
```bash
curl http://localhost:8001/health
```

## Zhrnutie

V tejto príručke ste sa naučili, ako:

- Spustiť kontajnerizované vLLM s podporou ROCm na integrovanej GPU
- Spustiť server vLLM s koncovými bodmi API kompatibilnými s OpenAI na porte 8001
- Odosielať výzvy pomocou `vllm-prompt`
- Vykonávať volania API na server vLLM pomocou streamovaných aj nestreamovaných požiadaviek
- Riešiť bežné problémy so spúšťaním servera, pamäťou a pripojeniami klientov

Teraz máte kontajnerizované nasadenie vLLM na poskytovanie veľkých jazykových modelov s optimalizovaným výkonom na integrovanej GPU.

## Ďalšie kroky

- **Vyskúšajte rôzne modely** — Zmeňte model v konfigurácii `vllm-launch`, aby ste mohli experimentovať s rôznymi LLM a porovnať ich výkon.
- **Vytvorte aplikáciu** — Použite rozhranie API kompatibilné s OpenAI na integráciu vLLM do Python aplikácie, chatbota alebo automatizovaného pracovného postupu.
- **Doladenie a nasadenie** — Doladte model pomocou LoRA alebo QLoRA a následne ho nasaďte pomocou vLLM pre optimalizovanú inferenciu.

## Ďalšie zdroje

- **[Oficiálna dokumentácia vLLM](https://docs.vllm.ai/)** — Komplexné návody a referencie API
- **[Repozitár vLLM na GitHube](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskusie komunity
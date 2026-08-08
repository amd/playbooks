<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový preklad.** Táto stránka bola automaticky preložená z angličtiny a nebola skontrolovaná človekom. Môže obsahovať chyby a niektoré pokyny, príkazy, súbory na stiahnutie, dostupnosť produktov alebo iný obsah sa môžu líšiť v závislosti od jazyka alebo regiónu. V prípade akéhokoľvek nesúladu alebo rozdielu je rozhodujúca a záväzná pôvodná anglická verzia playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Prehľad

vLLM je vysokovýkonný inferenčný nástroj navrhnutý pre veľké jazykové modely (LLM). Poskytuje optimalizované poskytovanie s priebežným dávkovaním (continuous batching) pre vysokú priepustnosť a rozhranie API kompatibilné s OpenAI pre bezproblémovú integráciu aplikácií. Vďaka tomu je vLLM vhodné pre produkčné nasadenia, kde sú kľúčové rýchlosť a efektívne využitie zdrojov.

Táto príručka vás naučí, ako poskytovať LLM pomocou kontajnerizovaného vLLM na integrovanej GPU a ako komunikovať s modelmi prostredníctvom OpenAI Python API.

## Čo sa naučíte

- Ako nastaviť a spustiť server vLLM s podporou AMD ROCm™
- Ako komunikovať s modelmi prostredníctvom koncových bodov API kompatibilných s OpenAI
- Ako odosielať výzvy (prompty) na lokálny server pomocou `vllm-prompt`

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

> **Poznámka**: Ak nie je nainštalovaný VS Code, môžete ho nainštalovať pomocou AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

vLLM beží v preddefinovanom kontajneri s ROCm a jeho vopred priradenými závislosťami. Nie je potrebná žiadna ďalšia inštalácia.

Neexistuje žiadny krok inštalácie vLLM na strane hostiteľa. Spustite vLLM pomocou:

```bash
vllm-launch
```

Spúšťač spustí kontajner, zacieli na integrovanú GPU a sprístupní lokálny server vLLM kompatibilný s OpenAI. Alternatívne kliknite na ikonu vLLM na paneli úloh.

## Rýchly štart

### 1. Overte, či server vLLM beží

Príkazu `vllm-launch` môže trvať niekoľko minút, kým všetko inicializuje. Po spustení je server dostupný na adrese `http://localhost:8001`. Ponechajte spúšťací terminál otvorený, pretože server beží na popredí, a otvorte samostatný terminál pre ďalšie kroky. Nižšie uvedené príklady používajú `Qwen/Qwen3-1.7B`; ak je váš spúšťač nakonfigurovaný pre iný model, nahraďte v požiadavkách toto ID modelu.

### 2. Odošlite výzvu

Použite poskytnutý skript `vllm-prompt` na odoslanie požiadavky na lokálny server vLLM kompatibilný s OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Komunikujte s modelom pomocou OpenAI Python API

Keďže vLLM sprístupňuje API kompatibilné s OpenAI, môžete na komunikáciu s ním použiť balík `openai` pre Python.

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

Následne odošlite požiadavku na dokončenie chatu (chat completion). Používa sa rovnaký formát správ ako v API OpenAI — zoznam správ s rolami ako `"user"` a `"assistant"`. Nastavenie `stream=True` znamená, že odpoveď bude prichádzať postupne, nie naraz:

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

Nakoniec prejdite streamované časti a vypíšte každý úsek textu tak, ako prichádza:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý príklad a je možné ho stiahnuť.


## Výber a konfigurácia modelu

Predvolene `vllm-launch` poskytuje `Qwen/Qwen3-1.7B` ako testovací model na porte `8001`. Model, port a parametre poskytovania vLLM môžete zmeniť bez opätovného zostavovania alebo úpravy kontajnera.

### Modely testované spoločnosťou AMD

Nasledujúce modely sú vopred nakonfigurované a overené spoločnosťou AMD:

| Model | Poznámky |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Predvolený model. Ľahký a rýchlo sa načítava. |
| `openai/gpt-oss-20b` | Väčší model pre kvalitnejšie odpovede. |

### Spustenie iného modelu

Odovzdajte ID modelu pomocou `--model` (alebo `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Zmena portu

Odovzdajte port nad 1024 pomocou `--port` (alebo `-p`); predvolená hodnota je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Ak zmeníte port, nasmerujte `base_url` klienta na rovnaký port (napríklad `http://localhost:8080/v1`).

### Odovzdávanie ďalších parametrov vLLM

Akékoľvek ďalšie argumenty sa priamo preposielajú do vLLM, takže môžete doladiť správanie poskytovania, ako je napríklad dĺžka kontextu alebo dátový typ. Existujú dva spôsoby ich zadania.

**V riadku (inline)**, za voľbami spúšťača:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trvalo**, v konfiguračnom súbore `~/.local/share/vLLM/vllm-launch.conf`. Tento súbor predvolene neexistuje — vytvorte ho a pridajte svoje argumenty ako pole (array) v jazyku Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Použite `+=` na pripojenie k predvoleným argumentom namiesto ich nahradenia:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Ak si chcete kedykoľvek pozrieť všetky možnosti spúšťača, spustite:

```bash
vllm-launch --help
```

### Kde sa ukladajú modely

`vllm-launch` hľadá modely na dvoch miestach:

| Umiestnenie | Cesta |
|----------|------|
| Systémové modely | `/var/cache/models` |
| Používateľské modely | `~/.local/share/vLLM/models` |

Stiahnutý model môžete umiestniť do ktoréhokoľvek z týchto adresárov a spustiť ho odovzdaním jeho cesty alebo ID do `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Poznámka**: Očakáva sa, že spustenie vlastného stiahnutého modelu týmto spôsobom bude fungovať, keď je model umiestnený v jednom z vyššie uvedených adresárov, avšak tento pracovný postup zatiaľ nebol oficiálne overený spoločnosťou AMD.

## Riešenie problémov

### Pripojenie odmietnuté

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
- Riešiť bežné problémy so spustením servera, pamäťou a pripojeniami klientov

Teraz máte kontajnerizované nasadenie vLLM na poskytovanie veľkých jazykových modelov s optimalizovaným výkonom na integrovanej GPU.

## Ďalšie kroky

- **Vyskúšajte rôzne modely** — Použite `vllm-launch --model <model>` na experimentovanie s rôznymi LLM a porovnanie výkonu (pozrite si [Výber a konfigurácia modelu](#choosing-and-configuring-a-model)).
- **Vytvorte aplikáciu** — Použite API kompatibilné s OpenAI na integráciu vLLM do aplikácie v Pythone, chatbota alebo automatizačného pracovného postupu.
- **Doladenie a poskytovanie** — Doladte model pomocou LoRA alebo QLoRA a potom ho nasaďte pomocou vLLM pre optimalizovanú inferenciu.
## Ďalšie zdroje

- **[Oficiálna dokumentácia vLLM](https://docs.vllm.ai/)** — Komplexné príručky a referencie API
- **[GitHub repozitár vLLM](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskusie komunity
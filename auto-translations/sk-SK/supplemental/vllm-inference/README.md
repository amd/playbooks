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

vLLM je vysokovýkonný inferenčný nástroj navrhnutý pre veľké jazykové modely (LLM). Poskytuje optimalizované poskytovanie služieb s priebežným dávkovaním (continuous batching) pre vysokú priepustnosť a API kompatibilné s OpenAI pre bezproblémovú integráciu aplikácií. Vďaka tomu je vLLM skvelou voľbou pre produkčné nasadenia, kde sú rýchlosť a efektívne využitie zdrojov kľúčové.

Táto príručka vás naučí, ako poskytovať LLM pomocou kontajnerizovaného vLLM na integrovanej GPU a ako komunikovať s modelmi prostredníctvom OpenAI Python API.

## Čo sa naučíte

- Ako nastaviť a spustiť server vLLM s podporou AMD ROCm™
- Ako komunikovať s modelmi prostredníctvom API koncových bodov kompatibilných s OpenAI
- Ako odosielať prompty na lokálny server pomocou `vllm-prompt`

## Nastavenie konfigurácie pamäte
<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou AMD Ryzen™ AI Developer Center.
<!-- @require:software-update -->
<!-- @device:end -->
## Inštalácia softvérových predpokladov

vLLM beží v predpripravenom kontajneri s ROCm a jeho závislosťami, ktoré sú vopred zladené. Nie je potrebná žiadna ďalšia inštalácia.

Na strane hostiteľa neexistuje žiadny inštalačný krok pre vLLM. Spustite vLLM pomocou:

```bash
vllm-launch
```

Spúšťač spustí kontajner, zacieli na integrovanú GPU a sprístupní lokálny OpenAI-kompatibilný vLLM server. Prípadne kliknite na ikonu vLLM na paneli úloh.

## Rýchly štart

### 1. Overte, že vLLM server beží

Príkazu `vllm-launch` môže inicializácia všetkého trvať niekoľko minút. Po spustení je server dostupný na adrese `http://localhost:8001`. Nechajte terminál, v ktorom prebehlo spustenie, otvorený, pretože server beží na popredí, a následne otvorte samostatný terminál pre zvyšné kroky. Príklady nižšie používajú `Qwen/Qwen3-1.7B`; ak je váš spúšťač nakonfigurovaný na iný model, v požiadavkách nahraďte toto ID modelu príslušným modelom.

### 2. Odošlite prompt

Na odoslanie požiadavky na lokálny OpenAI-kompatibilný vLLM server použite priložený skript `vllm-prompt`:

```bash
vllm-prompt "Tell me a story"
```

### 3. Konverzácia s modelom pomocou OpenAI Python API

Keďže vLLM poskytuje API kompatibilné s OpenAI, môžete na interakciu s ním použiť balík `openai` pre Python.

Najprv vytvorte virtuálne prostredie Python:
<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->
Nainštalujte balík OpenAI
```bash
pip install openai
```

Vytvorte klienta `OpenAI` smerujúceho na lokálny vLLM server namiesto serverov OpenAI. `api_key` je klientom vyžadovaný, ale vLLM ho nevaliduje, takže funguje akýkoľvek reťazec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Potom odošlite požiadavku na doplnenie konverzácie (chat completion). Používa sa rovnaký formát správ ako v OpenAI API — zoznam správ s rolami ako `"user"` a `"assistant"`. Nastavenie `stream=True` znamená, že odpoveď bude prichádzať postupne, nie naraz naraz:

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

Nakoniec prejdite iteráciou cez streamované bloky (chunks) a vypisujte každý kúsok textu hneď, ako príde:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý príklad a je možné ho stiahnuť.


## Výber a konfigurácia modelu

V predvolenom nastavení `vllm-launch` poskytuje `Qwen/Qwen3-1.7B` ako testovací model na porte `8001`. Model, port a parametre poskytovania vLLM môžete zmeniť bez opätovného zostavovania alebo úpravy kontajnera.

### Modely testované spoločnosťou AMD

Nasledujúce modely sú vopred nakonfigurované a overené spoločnosťou AMD:

| Model | Poznámky |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Predvolený model. Ľahký a rýchlo sa načítava. |
| `openai/gpt-oss-20b` | Väčší model pre kvalitnejšie odpovede. |

### Spustenie iného modelu

Zadajte ID modelu pomocou `--model` (alebo `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Zmena portu

Zadajte port vyšší ako 1024 pomocou `--port` (alebo `-p`); predvolená hodnota je `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Ak zmeníte port, nasmerujte `base_url` svojho klienta na rovnaký port (napríklad `http://localhost:8080/v1`).

### Odovzdávanie ďalších parametrov vLLM

Akékoľvek ďalšie argumenty sú presmerované priamo do vLLM, takže môžete doladiť správanie obsluhy, napríklad dĺžku kontextu alebo dátový typ. Existujú dva spôsoby, ako ich zadať.

**Vložene**, za možnosťami spúšťača:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Trvalo**, v konfiguračnom súbore na `~/.local/share/vLLM/vllm-launch.conf`. Tento súbor štandardne neexistuje — vytvorte ho a pridajte svoje argumenty ako pole Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Použite `+=` na pridanie k predvoleným argumentom namiesto ich nahradenia:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Ak chcete kedykoľvek zobraziť všetky možnosti spúšťača, spustite:

```bash
vllm-launch --help
```

### Kde sú modely uložené

`vllm-launch` hľadá modely na dvoch miestach:

| Umiestnenie | Cesta |
|----------|------|
| Systémové modely | `/var/cache/models` |
| Používateľské modely | `~/.local/share/vLLM/models` |

Stiahnutý model môžete umiestniť do ktoréhokoľvek z týchto adresárov a spustiť ho odovzdaním jeho cesty alebo ID parametru `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

**Poznámka**: Očakáva sa, že spustenie vlastného stiahnutého modelu týmto spôsobom bude fungovať po umiestnení modelu do jedného z vyššie uvedených adresárov, avšak tento pracovný postup zatiaľ nebol oficiálne overený spoločnosťou AMD.

## Riešenie problémov

### Spojenie odmietnuté

Uistite sa, že server beží:
```bash
curl http://localhost:8001/health
```

## Zhrnutie

V tomto návode ste sa naučili, ako:

- Spustiť kontajnerizovaný vLLM s podporou ROCm na integrovanej GPU
- Spustiť server vLLM s koncovými bodmi API kompatibilnými s OpenAI na porte 8001
- Odosielať výzvy pomocou `vllm-prompt`
- Vykonávať volania API na server vLLM pomocou streamovaných aj nestreamovaných požiadaviek
- Riešiť bežné problémy so spúšťaním servera, pamäťou a klientskymi pripojeniami

Teraz máte k dispozícii kontajnerizované nasadenie vLLM na obsluhu veľkých jazykových modelov s optimalizovaným výkonom na integrovanej GPU.

## Ďalšie kroky

- **Vyskúšajte rôzne modely** — Použite `vllm-launch --model <model>` na experimentovanie s rôznymi LLM a porovnanie výkonu (pozrite si [Výber a konfigurácia modelu](#choosing-and-configuring-a-model)).
- **Vytvorte aplikáciu** — Použite API kompatibilné s OpenAI na integráciu vLLM do Python aplikácie, chatbota alebo automatizovaného pracovného postupu.
- **Doladenie a nasadenie** — Doladte model pomocou LoRA alebo QLoRA a následne ho nasaďte pomocou vLLM na optimalizovanú inferenciu.
## Ďalšie zdroje

- **[Oficiálna dokumentácia vLLM](https://docs.vllm.ai/)** — Komplexné návody a referencie API
- **[Repozitár vLLM na GitHub](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskusie komunity
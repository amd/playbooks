<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používa špeciálne značky, ktoré GitHub nedokáže vykresliť. Správny náhľad tohto obsahu nájdete na [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Prehľad

vLLM je vysokovýkonný inferenčný engine navrhnutý pre veľké jazykové modely (LLM). Poskytuje optimalizované nasadenie s kontinuálnym dávkovaním pre vysokú priepustnosť a OpenAI-kompatibilné API pre bezproblémovú integráciu aplikácií. Vďaka tomu je vLLM skvelý pre produkčné nasadenia, kde sú rýchlosť a efektívnosť zdrojov kritické.

Tento playbook vás naučí, ako obsluhovať LLM pomocou kontajnerizovaného vLLM na integrovanom GPU a ako komunikovať s modelmi prostredníctvom OpenAI Python API.

## Čo sa naučíte

- Ako nastaviť a spustiť server vLLM s podporou AMD ROCm™
- Ako komunikovať s modelmi cez OpenAI-kompatibilné API endpointy
- Ako odosielať výzvy na lokálny server pomocou `vllm-prompt`

## Nastavenie konfigurácie pamäte

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizácií softvéru

> **Poznámka**: Ak VS Code nie je nainštalovaný, môžete ho nainštalovať pomocou AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Inštalácia softvérových predpokladov

Tento playbook používa vopred zostavený obraz kontajnera, ktorý obsahuje vLLM, podporu ROCm a pomocné skripty potrebné na spustenie servera. Nie je potrebné manuálne inštalovať PyTorch, vLLM ani lokálne skripty playbooku.

Na strane hostiteľa nie je žiadny krok inštalácie vLLM. Spustite vLLM pomocou:

```bash
vllm-launch
```

Spúšťač spustí kontajner, zacieli na integrovaný GPU a sprístupní lokálny OpenAI-kompatibilný server vLLM. Prípadne kliknite na ikonu vLLM na paneli úloh.

## Rýchly štart

### 1. Potvrďte, že server vLLM beží

Inicializácia `vllm-launch` môže trvať niekoľko minút. Po spustení je server dostupný na adrese `http://localhost:8001`. Nechajte terminál so spúšťačom otvorený, pretože server beží v popredí, a potom otvorte samostatný terminál pre zostávajúce kroky. Nasledujúce príklady používajú `Qwen/Qwen3-1.7B`; ak je váš spúšťač nakonfigurovaný pre iný model, nahraďte toto ID modelu v požiadavkách.

### 2. Odoslanie výzvy

Použite poskytnutý skript `vllm-prompt` na odoslanie požiadavky na lokálny OpenAI-kompatibilný server vLLM:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatovanie s modelom pomocou OpenAI Python API

Keďže vLLM sprístupňuje OpenAI-kompatibilné API, môžete na komunikáciu s ním použiť balík `openai` pre Python.

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

Vytvorte klienta `OpenAI` nasmerovaného na lokálny server vLLM namiesto serverov OpenAI. Klient vyžaduje `api_key`, ale vLLM ho neoveruje, takže postačí akýkoľvek reťazec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Potom odošlite požiadavku na dokončenie chatu. Používa rovnaký formát správ ako OpenAI API — zoznam správ s rolami ako `"user"` a `"assistant"`. Nastavenie `stream=True` znamená, že odpoveď bude prichádzať postupne, nie naraz:

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

Nakoniec iterujte cez streamované časti a vytlačte každý kúsok textu hneď po jeho príchode:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Priložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý príklad a je možné ho stiahnuť.


## Riešenie problémov

### Odmietnuté pripojenie

Uistite sa, že server beží:
```bash
curl http://localhost:8001/health
```

## Zhrnutie

V tomto playbooku ste sa naučili, ako:

- Spustiť kontajnerizovaný vLLM s podporou ROCm na integrovanom GPU
- Spustiť server vLLM s OpenAI-kompatibilnými API endpointmi na porte 8001
- Odosielať výzvy pomocou `vllm-prompt`
- Volať API servera vLLM pomocou streamovaných aj nestreamovaných požiadaviek
- Riešiť bežné problémy so spustením servera, pamäťou a pripojeniami klientov

Teraz máte kontajnerizované nasadenie vLLM na obsluhu veľkých jazykových modelov s optimalizovaným výkonom na integrovanom GPU.

## Ďalšie kroky

- **Vyskúšajte rôzne modely** — Zmeňte model v konfigurácii `vllm-launch` a experimentujte s rôznymi LLM a porovnávajte výkon.
- **Vytvorte aplikáciu** — Použite OpenAI-kompatibilné API na integráciu vLLM do Python aplikácie, chatbota alebo automatizačného pracovného toku.
- **Dolaďte a nasaďte** — Dolaďte model pomocou LoRA alebo QLoRA a potom ho nasaďte pomocou vLLM pre optimalizovanú inferenciu.

## Ďalšie zdroje

- **[Oficiálna dokumentácia vLLM](https://docs.vllm.ai/)** — Komplexné príručky a referencie API
- **[Repozitár vLLM na GitHub](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskusie komunity
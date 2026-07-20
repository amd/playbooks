<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez az útmutató olyan speciális címkéket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom megfelelő megtekintéséhez látogasson el a [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->


## Áttekintés

A vLLM egy nagy teljesítményű következtetési motor, amelyet nagy nyelvi modellek (LLM-ek) számára terveztek. Optimalizált kiszolgálást biztosít folyamatos kötegeléssel a nagy átviteli sebesség érdekében, valamint egy OpenAI-kompatibilis API-t a zökkenőmentes alkalmazásintegrációhoz. Ez teszi a vLLM-et kiválóvá olyan éles környezetű üzembe helyezésekhez, ahol a sebesség és az erőforrás-hatékonyság kritikus fontosságú.

Ez az útmutató megtanítja, hogyan szolgáltasson LLM-eket konténerizált vLLM használatával az integrált GPU-n, és hogyan lépjen kapcsolatba a modellekkel az OpenAI Python API-n keresztül.

## Amit meg fog tanulni

- Hogyan állítson be és indítson el egy vLLM szervert AMD ROCm™ támogatással
- Hogyan lépjen kapcsolatba a modellekkel OpenAI-kompatibilis API végpontokon keresztül
- Hogyan küldjön promptokat a helyi szerverre a `vllm-prompt` használatával

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti az AMD Ryzen™ AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## A szükséges szoftverek telepítése

Ez az útmutató egy előre elkészített konténerképet használ, amely tartalmazza a vLLM-et, a ROCm támogatást, valamint a szerver indításához szükséges segédszkripteket. Nem szükséges manuálisan telepítenie a PyTorch-ot, a vLLM-et vagy a helyi útmutató szkripteket.

Nincs szükség host oldali vLLM telepítési lépésre. Indítsa el a vLLM-et a következővel:

```bash
vllm-launch
```

Az indító elindítja a konténert, az integrált GPU-t célozza meg, és elérhetővé tesz egy helyi OpenAI-kompatibilis vLLM szervert. Alternatív megoldásként kattintson a vLLM ikonra a tálcán.

## Gyorsindítás

### 1. A vLLM szerver futásának ellenőrzése

A `vllm-launch` néhány percet vehet igénybe az inicializáláshoz. Miután elindult, a szerver a `http://localhost:8001` címen érhető el. Tartsa nyitva az indító terminált, mivel a szerver előtérben fut, majd nyisson meg egy külön terminált a fennmaradó lépésekhez. Az alábbi példák a `Qwen/Qwen3-1.7B` modellt használják; ha az indítója más modellre van konfigurálva, helyettesítse be azt a modellazonosítót a kérésekben.

### 2. Prompt küldése

Használja a mellékelt `vllm-prompt` szkriptet, hogy kérést küldjön a helyi vLLM OpenAI-kompatibilis szervernek:

```bash
vllm-prompt "Tell me a story"
```

### 3. Csevegés a modellel az OpenAI Python API használatával

Mivel a vLLM egy OpenAI-kompatibilis API-t biztosít, az `openai` Python csomaggal léphet vele kapcsolatba.

Először hozzon létre egy Python virtuális környezetet:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Telepítse az OpenAI csomagot
```bash
pip install openai
```

Hozzon létre egy `OpenAI` klienst, amely a helyi vLLM szerverre mutat az OpenAI szerverei helyett. Az `api_key` szükséges a klienshez, de a vLLM nem ellenőrzi, így bármilyen karakterlánc megfelel:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ezután küldjön egy csevegés-kiegészítési kérést. Ez ugyanazt az üzenetformátumot használja, mint az OpenAI API — üzenetek listáját olyan szerepekkel, mint a `"user"` és `"assistant"`. A `stream=True` beállítása azt jelenti, hogy a válasz fokozatosan, nem pedig egyszerre érkezik meg:

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

Végül iteráljon végig a streamelt darabokon, és írja ki a szöveg minden egyes részét, ahogy megérkezik:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

A mellékelt [chat_with_model.py](assets/chat_with_model.py) szkript tartalmazza a teljes példát, és letölthető.


## Hibaelhárítás

### Connection refused

Győződjön meg arról, hogy a szerver fut:
```bash
curl http://localhost:8001/health
```

## Összefoglalás

Ebben az útmutatóban megtanulta, hogyan:

- Indítson konténerizált vLLM-et ROCm támogatással az integrált GPU-n
- Indítson egy vLLM szervert OpenAI-kompatibilis API végpontokkal a 8001-es porton
- Küldjön promptokat a `vllm-prompt` használatával
- Hajtson végre API hívásokat a vLLM szerverhez mind streamelt, mind nem streamelt kérésekkel
- Hárítson el gyakori problémákat a szerver indításával, a memóriával és a kliens kapcsolatokkal kapcsolatban

Most már rendelkezik egy konténerizált vLLM üzembe helyezéssel, amely nagy nyelvi modelleket szolgál ki optimalizált teljesítménnyel az integrált GPU-n.

## Következő lépések

- **Próbáljon ki különböző modelleket** — Cserélje ki a modellt a `vllm-launch` konfigurációban, hogy kísérletezzen különböző LLM-ekkel, és összehasonlítsa a teljesítményt.
- **Építsen alkalmazást** — Használja az OpenAI-kompatibilis API-t a vLLM integrálásához egy Python alkalmazásba, chatbotba vagy automatizálási munkafolyamatba.
- **Finomhangolás és kiszolgálás** — Finomhangoljon egy modellt LoRA vagy QLoRA használatával, majd telepítse a vLLM-mel optimalizált következtetéshez.

## További források

- **[vLLM hivatalos dokumentáció](https://docs.vllm.ai/)** — Átfogó útmutatók és API-referenciák
- **[vLLM GitHub tároló](https://github.com/vllm-project/vllm)** — Forráskód, hibajegyek és közösségi beszélgetések
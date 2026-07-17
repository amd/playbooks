<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Ez a playbook speciális tageket használ, amelyeket a GitHub nem tud megjeleníteni. A tartalom helyes előnézetéhez látogasson el az [amd.com/playbooks](https://amd.com/playbooks) oldalra.
<!-- @github-only:end -->


## Áttekintés

A vLLM egy nagy teljesítményű következtetési motor, amelyet nagy nyelvi modellekhez (LLM-ekhez) terveztek. Optimalizált kiszolgálást biztosít folyamatos kötegeléssel a nagy átviteli sebesség érdekében, valamint OpenAI-kompatibilis API-t a zökkenőmentes alkalmazásintegrációhoz. Ez teszi a vLLM-et kiválóvá az éles környezetű telepítésekhez, ahol a sebesség és az erőforrás-hatékonyság kritikus fontosságú.

Ez a playbook megtanítja, hogyan kell LLM-eket kiszolgálni konténerizált vLLM segítségével az integrált GPU-n, és hogyan lehet modellekkel kommunikálni az OpenAI Python API-n keresztül.

## Mit fog megtanulni

- Hogyan állítson be és indítson el egy vLLM szervert AMD ROCm™ támogatással
- Hogyan kommunikáljon modellekkel OpenAI-kompatibilis API végpontokon keresztül
- Hogyan küldjön promptokat a helyi szervernek a `vllm-prompt` segítségével

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

> **Megjegyzés**: Ha a VS Code nincs telepítve, az AMD Ryzen™ AI Developer Center segítségével telepítheti.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftver-előfeltételek telepítése

Ez a playbook egy előre elkészített konténerképet használ, amely tartalmazza a vLLM-et, a ROCm támogatást és a szerver indításához szükséges segédszkripteket. Nem szükséges manuálisan telepíteni a PyTorch-ot, a vLLM-et vagy a helyi playbook szkripteket.

Nincs gazdagép oldali vLLM telepítési lépés. Indítsa el a vLLM-et a következővel:

```bash
vllm-launch
```

Az indító elindítja a konténert, az integrált GPU-t célozza meg, és egy helyi OpenAI-kompatibilis vLLM szervert tesz elérhetővé. Alternatívaként kattintson a vLLM ikonra a tálcán.

## Gyors kezdés

### 1. Ellenőrizze, hogy a vLLM szerver fut-e

A `vllm-launch` néhány percet vehet igénybe az inicializáláshoz. Miután elindul, a szerver a `http://localhost:8001` címen érhető el. Tartsa nyitva az indítási terminált, mivel a szerver az előtérben fut, majd nyisson meg egy külön terminált a további lépésekhez. Az alábbi példák a `Qwen/Qwen3-1.7B` modellt használják; ha az indítója más modellre van konfigurálva, helyettesítse azt a modell azonosítóval a kérésekben.

### 2. Prompt küldése

Használja a mellékelt `vllm-prompt` szkriptet, hogy kérést küldjön a helyi vLLM OpenAI-kompatibilis szervernek:

```bash
vllm-prompt "Tell me a story"
```

### 3. Csevegés a modellel az OpenAI Python API segítségével

Mivel a vLLM OpenAI-kompatibilis API-t tesz elérhetővé, az `openai` Python csomaggal kommunikálhat vele.

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

Hozzon létre egy `OpenAI` klienst, amely a helyi vLLM szerverre mutat az OpenAI szerverei helyett. Az `api_key` szükséges a kliens számára, de a vLLM nem ellenőrzi, így bármilyen karakterlánc megfelel:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ezután küldjön egy csevegés-kiegészítési kérést. Ez ugyanazt az üzenetformátumot használja, mint az OpenAI API — szerepekkel ellátott üzenetek listája, mint például `"user"` és `"assistant"`. A `stream=True` beállítása azt jelenti, hogy a válasz fokozatosan érkezik meg, nem egyszerre:

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

Végül iteráljon a streamelt darabokon, és nyomtassa ki az egyes szövegrészeket, ahogy megérkeznek:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

A mellékelt [chat_with_model.py](assets/chat_with_model.py) szkript tartalmazza a teljes példát, és letölthető.


## Hibaelhárítás

### Kapcsolat megtagadva

Győződjön meg arról, hogy a szerver fut:
```bash
curl http://localhost:8001/health
```

## Összefoglalás

Ebben a playbookban megtanulta, hogyan kell:

- Konténerizált vLLM-et indítani ROCm támogatással az integrált GPU-n
- vLLM szervert elindítani OpenAI-kompatibilis API végpontokkal a 8001-es porton
- Promptokat küldeni a `vllm-prompt` segítségével
- API hívásokat intézni a vLLM szerverhez streaming és nem streaming kérések segítségével
- Általános problémákat elhárítani a szerver indításával, a memóriával és a kliens kapcsolatokkal kapcsolatban

Most már rendelkezik egy konténerizált vLLM telepítéssel a nagy nyelvi modellek optimalizált teljesítménnyel történő kiszolgálásához az integrált GPU-n.

## Következő lépések

- **Próbáljon ki különböző modelleket** — Cserélje le a modellt a `vllm-launch` konfigurációban, hogy különböző LLM-ekkel kísérletezzen és hasonlítsa össze a teljesítményt.
- **Építsen alkalmazást** — Használja az OpenAI-kompatibilis API-t a vLLM integrálásához egy Python alkalmazásba, chatbotba vagy automatizálási munkafolyamatba.
- **Finomhangolja és kiszolgálja** — Finomhangolja a modellt LoRA vagy QLoRA segítségével, majd telepítse vLLM-mel az optimalizált következtetéshez.

## További erőforrások

- **[vLLM hivatalos dokumentáció](https://docs.vllm.ai/)** — Átfogó útmutatók és API referenciák
- **[vLLM GitHub adattár](https://github.com/vllm-project/vllm)** — Forráskód, hibajegyek és közösségi megbeszélések
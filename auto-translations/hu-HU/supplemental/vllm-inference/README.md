<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Áttekintés

A vLLM egy nagy teljesítményű következtetési motor, amelyet nagy nyelvi modellekhez (LLM-ekhez) terveztek. Optimalizált kiszolgálást biztosít folyamatos kötegeléssel (continuous batching) a nagy áteresztőképesség érdekében, valamint OpenAI-kompatibilis API-t a zökkenőmentes alkalmazásintegrációhoz. Mindez a vLLM-et kiválóan alkalmassá teszi éles üzemi telepítésekhez, ahol a sebesség és az erőforrás-hatékonyság kritikus fontosságú.

Ez a playbook megtanítja, hogyan szolgálj ki LLM-eket konténerizált vLLM segítségével az integrált GPU-n, és hogyan lépj kapcsolatba a modellekkel az OpenAI Python API-n keresztül.

## Amit tanulni fogsz

- Hogyan állíts be és indíts el egy vLLM szervert AMD ROCm™ támogatással
- Hogyan lépj kapcsolatba modellekkel OpenAI-kompatibilis API végpontokon keresztül
- Hogyan küldj promptokat a helyi szerverre a `vllm-prompt` használatával

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések ellenőrzése

> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheted az AMD Ryzen™ AI Developer Centerrel.

<!-- @require:software-update -->
<!-- @device:end -->

## Szoftveres előfeltételek telepítése

A vLLM egy előre elkészített konténerben fut, amelyben a ROCm és annak függőségei előre összehangolva vannak. Nincs szükség további telepítésre.

Nincs host-oldali vLLM telepítési lépés. Indítsd el a vLLM-et ezzel:

```bash
vllm-launch
```

Az indító elindítja a konténert, az integrált GPU-t célozza meg, és közzéteszi a helyi OpenAI-kompatibilis vLLM szervert. Alternatív megoldásként kattints a vLLM ikonra a tálcán.

## Gyorsindítás

### 1. Erősítsd meg, hogy a vLLM szerver fut

A `vllm-launch` néhány percet vehet igénybe az inicializáláshoz. Amint elindul, a szerver elérhető a `http://localhost:8001` címen. Hagyd nyitva az indító terminált, mert a szerver előtérben fut, majd nyiss egy másik terminált a további lépésekhez. Az alábbi példák a `Qwen/Qwen3-1.7B` modellt használják; ha az indítód másik modellre van konfigurálva, a kérésekben helyettesítsd be az adott modell azonosítóját.

### 2. Küldj egy promptot

Használd a mellékelt `vllm-prompt` szkriptet, hogy kérést küldj a helyi OpenAI-kompatibilis vLLM szervernek:

```bash
vllm-prompt "Tell me a story"
```

### 3. Chatelj a modellel az OpenAI Python API segítségével

Mivel a vLLM OpenAI-kompatibilis API-t biztosít, a vele való kapcsolattartáshoz használhatod az `openai` Python csomagot.

Először hozz létre egy Python virtuális környezetet:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->
<!-- @os:end -->

Telepítsd az OpenAI csomagot
```bash
pip install openai
```

Hozz létre egy `OpenAI` klienst, amely a helyi vLLM szerverre mutat az OpenAI szerverei helyett. Az `api_key` megadása kötelező a kliens számára, de a vLLM nem validálja azt, így bármilyen karakterlánc megfelel:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ezután küldj egy chat completion kérést. Ez ugyanazt az üzenetformátumot használja, mint az OpenAI API — üzenetek listáját, olyan szerepekkel, mint a `"user"` és az `"assistant"`. A `stream=True` beállítása azt jelenti, hogy a válasz fokozatosan érkezik, nem pedig egyszerre:

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

Végül iterálj végig a streamelt darabokon, és írd ki az egyes szövegrészeket, ahogy megérkeznek:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

A mellékelt [chat_with_model.py](assets/chat_with_model.py) szkript tartalmazza a teljes példát, és letölthető.


## Modell kiválasztása és konfigurálása

Alapértelmezés szerint a `vllm-launch` a `Qwen/Qwen3-1.7B` modellt szolgálja ki tesztmodellként a `8001`-es porton. A modellt, a portot és a vLLM kiszolgálási paramétereket a konténer újraépítése vagy szerkesztése nélkül módosíthatod.

### AMD által tesztelt modellek

Az alábbi modellek előre konfiguráltak és az AMD által validáltak:

| Modell | Megjegyzések |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Alapértelmezett modell. Könnyű és gyorsan betölthető. |
| `openai/gpt-oss-20b` | Nagyobb modell a jobb minőségű válaszokhoz. |

### Másik modell indítása

Add meg a modell azonosítóját a `--model` (vagy `-m`) kapcsolóval:

```bash
vllm-launch --model openai/gpt-oss-20b
```

### A port megváltoztatása

Adj meg egy 1024 fölötti portot a `--port` (vagy `-p`) kapcsolóval; az alapértelmezett érték a `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Ha megváltoztatod a portot, a kliensed `base_url` paraméterét is ugyanarra a portra irányítsd (például `http://localhost:8080/v1`).

### További vLLM paraméterek átadása

Minden további argumentum közvetlenül a vLLM-nek lesz továbbítva, így finomhangolhatod a kiszolgálási viselkedést, például a kontextushosszt vagy az adattípust. Kétféleképpen adhatod meg ezeket.

**Soron belül (inline)**, az indító beállításai után:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Tartósan**, egy konfigurációs fájlban a `~/.local/share/vLLM/vllm-launch.conf` helyen. Ez a fájl alapértelmezés szerint nem létezik — hozd létre, és add hozzá az argumentumaidat Bash tömbként:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Használd a `+=` operátort, hogy hozzáfűzd az alapértelmezett argumentumokhoz, ahelyett hogy lecserélnéd őket:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Az összes indítási opció megtekintéséhez bármikor futtasd:

```bash
vllm-launch --help
```

### Hol tárolódnak a modellek

A `vllm-launch` két helyen keresi a modelleket:

| Hely | Útvonal |
|----------|------|
| Rendszer modellek | `/var/cache/models` |
| Felhasználói modellek | `~/.local/share/vLLM/models` |

Egy letöltött modellt bármelyik könyvtárba elhelyezhetsz, és elindíthatod az útvonalának vagy azonosítójának a `--model` kapcsolóval történő megadásával:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Megjegyzés**: A saját letöltött modell ilyen módon történő futtatása várhatóan működik, amint a modellt a fenti könyvtárak egyikébe helyezed, de ezt a munkafolyamatot az AMD még nem validálta hivatalosan.

## Hibaelhárítás

### Kapcsolat megtagadva (Connection refused)

Győződj meg róla, hogy a szerver fut:
```bash
curl http://localhost:8001/health
```

## Összefoglalás

Ebben a playbookban megtanultad, hogyan:

- Indíts konténerizált vLLM-et ROCm támogatással az integrált GPU-n
- Indíts el egy vLLM szervert OpenAI-kompatibilis API végpontokkal a 8001-es porton
- Küldj promptokat a `vllm-prompt` használatával
- Végezz API hívásokat a vLLM szerverhez, mind streamelt, mind nem streamelt kérésekkel
- Háríts el gyakori problémákat a szerver indításával, a memóriával és a kliens kapcsolatokkal kapcsolatban

Mostantól rendelkezel egy konténerizált vLLM telepítéssel, amely nagy nyelvi modellek kiszolgálására szolgál, optimalizált teljesítménnyel az integrált GPU-n.

## Következő lépések

- **Próbálj ki különböző modelleket** — Használd a `vllm-launch --model <model>` parancsot, hogy kísérletezz különböző LLM-ekkel, és összehasonlítsd a teljesítményüket (lásd [Modell kiválasztása és konfigurálása](#choosing-and-configuring-a-model)).
- **Építs alkalmazást** — Használd az OpenAI-kompatibilis API-t, hogy integráld a vLLM-et egy Python alkalmazásba, chatbotba vagy automatizálási munkafolyamatba.
- **Finomhangolás és kiszolgálás** — Finomhangolj egy modellt LoRA vagy QLoRA segítségével, majd telepítsd a vLLM-mel az optimalizált következtetéshez.
## További erőforrások

- **[vLLM hivatalos dokumentáció](https://docs.vllm.ai/)** — Átfogó útmutatók és API-referenciák
- **[vLLM GitHub-tárhely](https://github.com/vllm-project/vllm)** — Forráskód, hibajegyek és közösségi megbeszélések
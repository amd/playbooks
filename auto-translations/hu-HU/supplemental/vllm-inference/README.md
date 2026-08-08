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

A vLLM egy nagy teljesítményű következtetési motor, amelyet nagy nyelvi modellekhez (LLM-ekhez) terveztek. Optimalizált kiszolgálást biztosít folyamatos kötegeléssel a nagy áteresztőképesség érdekében, valamint OpenAI-kompatibilis API-t a zökkenőmentes alkalmazásintegrációhoz. Mindez kiválóan alkalmassá teszi a vLLM-et olyan éles környezetű telepítésekhez, ahol a sebesség és az erőforrás-hatékonyság kritikus fontosságú.

Ez a playbook megtanítja, hogyan szolgáltasson LLM-eket konténerizált vLLM segítségével az integrált GPU-n, és hogyan lépjen kapcsolatba a modellekkel az OpenAI Python API-n keresztül.

## Amit meg fog tanulni

- Hogyan állítson be és indítson el egy vLLM-kiszolgálót AMD ROCm™ támogatással
- Hogyan lépjen kapcsolatba a modellekkel OpenAI-kompatibilis API-végpontokon keresztül
- Hogyan küldjön promptokat a helyi kiszolgálónak a `vllm-prompt` segítségével

## A memóriakonfiguráció beállítása

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Szoftverfrissítések keresése

> **Megjegyzés**: Ha a VS Code nincs telepítve, telepítheti az AMD Ryzen™ AI Developer Center segítségével.

<!-- @require:software-update -->
<!-- @device:end -->

## A szükséges szoftverek telepítése

A vLLM egy előre elkészített konténerben fut, amelyben a ROCm és annak függőségei már előre összeegyeztetve vannak. Nincs szükség további telepítésre.

Nincs gazdagépoldali vLLM-telepítési lépés. Indítsa el a vLLM-et a következővel:

```bash
vllm-launch
```

Az indítóprogram elindítja a konténert, az integrált GPU-t célozza meg, és felkínál egy helyi OpenAI-kompatibilis vLLM-kiszolgálót. Alternatívaként kattintson a vLLM ikonra a tálcán.

## Gyors kezdés

### 1. Ellenőrizze, hogy a vLLM-kiszolgáló fut-e

A `vllm-launch` inicializálása néhány percig tarthat. Az indulást követően a kiszolgáló a `http://localhost:8001` címen érhető el. Tartsa nyitva az indító terminált, mert a kiszolgáló előtérben fut, majd nyisson egy külön terminált a további lépésekhez. Az alábbi példák a `Qwen/Qwen3-1.7B` modellt használják; ha az indítóprogram másik modellre van konfigurálva, helyettesítse be a kérésekben azt a modellazonosítót.

### 2. Prompt küldése

Használja a rendelkezésre álló `vllm-prompt` szkriptet, hogy kérést küldjön a helyi, OpenAI-kompatibilis vLLM-kiszolgálónak:

```bash
vllm-prompt "Tell me a story"
```

### 3. Csevegés a modellel az OpenAI Python API segítségével

Mivel a vLLM OpenAI-kompatibilis API-t kínál, a modellel az `openai` Python csomag segítségével léphet kapcsolatba.

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

Hozzon létre egy `OpenAI` klienst, amely az OpenAI kiszolgálói helyett a helyi vLLM-kiszolgálóra mutat. Az `api_key` szükséges a klienshez, de a vLLM nem ellenőrzi azt, így bármilyen karakterlánc megfelel:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Ezután küldjön el egy chat completion kérést. Ez ugyanazt az üzenetformátumot használja, mint az OpenAI API — üzenetek listáját olyan szerepekkel, mint a `"user"` és az `"assistant"`. A `stream=True` beállítása azt jelenti, hogy a válasz fokozatosan érkezik meg, nem pedig egyszerre:

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

Végül iteráljon végig a streamelt darabokon (chunk), és nyomtassa ki a szöveg egyes részeit, ahogy megérkeznek:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

A mellékelt [chat_with_model.py](assets/chat_with_model.py) szkript tartalmazza a teljes példát, és letölthető.


## Modell kiválasztása és konfigurálása

Alapértelmezés szerint a `vllm-launch` a `Qwen/Qwen3-1.7B` modellt szolgáltatja tesztmodellként a `8001`-es porton. A modellt, a portot és a vLLM kiszolgálási paramétereit a konténer újraépítése vagy szerkesztése nélkül is megváltoztathatja.

### Az AMD által tesztelt modellek

Az alábbi modellek előre konfiguráltak és az AMD által validáltak:

| Modell | Megjegyzések |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Alapértelmezett modell. Könnyű és gyorsan betölthető. |
| `openai/gpt-oss-20b` | Nagyobb modell, jobb minőségű válaszokhoz. |

### Másik modell indítása

Adja meg a modellazonosítót a `--model` (vagy `-m`) kapcsolóval:

```bash
vllm-launch --model openai/gpt-oss-20b
```

### A port módosítása

Adjon meg egy 1024-nél nagyobb portot a `--port` (vagy `-p`) kapcsolóval; az alapértelmezett érték `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Ha módosítja a portot, állítsa be a kliens `base_url` értékét ugyanarra a portra (például `http://localhost:8080/v1`).

### További vLLM-paraméterek megadása

Bármely további argumentum közvetlenül továbbításra kerül a vLLM felé, így finomhangolhatja a kiszolgálási viselkedést, például a kontextushosszt vagy az adattípust. Ezeket kétféleképpen adhatja meg.

**Soron belül**, az indítóprogram opciói után:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Tartósan**, egy konfigurációs fájlban a `~/.local/share/vLLM/vllm-launch.conf` helyen. Ez a fájl alapértelmezés szerint nem létezik — hozza létre, és adja hozzá az argumentumait Bash tömbként:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Használja a `+=` operátort, hogy az alapértelmezett argumentumokhoz fűzze hozzá, ahelyett hogy lecserélné őket:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Az összes indítóprogram-opció megtekintéséhez bármikor futtassa a következőt:

```bash
vllm-launch --help
```

### Hol tárolódnak a modellek

A `vllm-launch` két helyen keresi a modelleket:

| Hely | Elérési út |
|----------|------|
| Rendszermodellek | `/var/cache/models` |
| Felhasználói modellek | `~/.local/share/vLLM/models` |

A letöltött modellt bármelyik könyvtárba elhelyezheti, majd elindíthatja az elérési útjának vagy azonosítójának megadásával a `--model` kapcsolónál:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Megjegyzés**: A saját letöltött modell ilyen módon történő futtatása várhatóan működik, amint a modell a fenti könyvtárak valamelyikébe kerül, de ezt a munkafolyamatot az AMD még nem validálta hivatalosan.

## Hibaelhárítás

### Elutasított kapcsolat

Győződjön meg arról, hogy a kiszolgáló fut:
```bash
curl http://localhost:8001/health
```

## Összefoglalás

Ebben a playbookban megtanulta, hogyan kell:

- Konténerizált vLLM-et indítani ROCm támogatással az integrált GPU-n
- vLLM-kiszolgálót indítani OpenAI-kompatibilis API-végpontokkal a 8001-es porton
- Promptokat küldeni a `vllm-prompt` segítségével
- API-hívásokat végezni a vLLM-kiszolgáló felé streamelt és nem streamelt kérésekkel egyaránt
- Elhárítani a kiszolgáló indításával, a memóriával és a kliens-kapcsolatokkal kapcsolatos gyakori problémákat

Mostantól rendelkezik egy konténerizált vLLM-telepítéssel, amely optimalizált teljesítménnyel szolgáltat nagy nyelvi modelleket az integrált GPU-n.

## Következő lépések

- **Próbáljon ki különböző modelleket** — Használja a `vllm-launch --model <model>` parancsot, hogy különböző LLM-ekkel kísérletezzen, és összehasonlítsa a teljesítményüket (lásd: [Modell kiválasztása és konfigurálása](#choosing-and-configuring-a-model)).
- **Építsen alkalmazást** — Használja az OpenAI-kompatibilis API-t, hogy integrálja a vLLM-et egy Python-alkalmazásba, chatbotba vagy automatizált munkafolyamatba.
- **Finomhangolás és kiszolgálás** — Finomhangoljon egy modellt LoRA vagy QLoRA segítségével, majd telepítse vLLM-mel az optimalizált következtetéshez.
## További források

- **[vLLM hivatalos dokumentáció](https://docs.vllm.ai/)** — Átfogó útmutatók és API-referenciák
- **[vLLM GitHub-tárolója](https://github.com/vllm-project/vllm)** — Forráskód, hibajegyek és közösségi beszélgetések
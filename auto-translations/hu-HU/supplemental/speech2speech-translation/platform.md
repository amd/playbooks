<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

Ez a dokumentum ismerteti a playbook futtatásához szükséges elvárt platformkonfigurációkat.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platform eszközön. Minden más eszköz esetén a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch csomagot. Kérjük, tekintse meg az operációs rendszerének megfelelő szakaszt:

### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszköz esetén manuálisan kell telepíteni |

### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszköz esetén manuálisan kell telepíteni |

## Szükséges modellek

Az alábbi modellek le lettek tesztelve és optimalizálva vannak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3 milliárd | ~10GB | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszköz esetén manuálisan kell telepíteni |

A modellek automatikusan letöltésre kerülnek a Hugging Face gyorsítótár könyvtárba:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Gondoskodjon legalább **20 GB szabad tárhelyről** a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internet-hozzáférés szükséges a modellek Hugging Face-ről történő letöltéséhez. A letöltés után a playbook offline is futtatható.

- Az első alkalommal történő modellletöltés a modell méretétől és a kapcsolat sebességétől függően **5-10 percet** vehet igénybe
- A modellek helyben gyorsítótárazásra kerülnek, így nem szükséges őket újra letölteni
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angol nyelvről, és emberi ellenőrzésen nem esett át. Hibákat tartalmazhat, és bizonyos utasítások, parancsok, letöltések, termékelérhetőség vagy egyéb tartalmak nyelvenként vagy régiónként eltérhetnek. Bármilyen eltérés vagy ellentmondás esetén a playbook eredeti angol nyelvű változata az irányadó.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges platformkonfigurációkat.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platform eszközön. Minden más eszközön a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch-ot. Az operációs rendszerének megfelelő szakaszért lásd az alábbiakat:

### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

## Szükséges modellek

Az alábbi modellek tesztelve és optimalizálva vannak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

A modellek automatikusan letöltésre kerülnek a Hugging Face gyorsítótár-könyvtárba:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Győződjön meg róla, hogy legalább **50GB szabad hely** áll rendelkezésre a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről történő letöltéséhez. A letöltés után a playbook offline is futtatható.

- Az első alkalommal történő modell-letöltések a modell méretétől és a kapcsolat sebességétől függően **5-10 percet** vehetnek igénybe
- A modellek helyben gyorsítótárazva vannak, és nem szükséges újra letölteni őket
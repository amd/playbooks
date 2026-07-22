<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Gépi fordítás.** Ez az oldal automatikusan lett lefordítva angolról, és emberi lektorálás nem történt. Hibákat tartalmazhat, és egyes lépések, parancsok, letöltések vagy termékelérhetőségek eltérhetnek az Ön nyelvében vagy régiójában. Ha bármi hibásnak tűnik, tekintse az eredeti angol nyelvű playbookot mérvadó forrásnak.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges elvárt platformkonfigurációkat.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platformon. Minden más eszköz esetén a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch-ot. Kérjük, tekintse meg az operációs rendszerének megfelelő szakaszt:


### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |


### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |


## Szükséges modellek

A következő modellek le vannak tesztelve és optimalizálva vannak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Letöltés HF-ről

A modellek automatikusan letöltésre kerülnek a Hugging Face gyorsítótár-könyvtárába: `~/.cache/huggingface/hub/`

Gondoskodjon legalább **20 GB szabad tárhelyről** a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről történő letöltéséhez. A letöltés után a playbook offline is futtatható.

- Az első alkalommal történő modell-letöltések a modell méretétől és a kapcsolat sebességétől függően **5-10 percet** vehetnek igénybe
- A modellek helyben tárolódnak a gyorsítótárban, így nincs szükség ismételt letöltésre
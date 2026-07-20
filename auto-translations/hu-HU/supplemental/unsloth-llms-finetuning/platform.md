# Platform Configuration

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges platformkonfigurációkat.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platformon. Minden más eszköz esetében a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch-ot. Kérjük, tekintse meg az operációs rendszerének megfelelő szakaszt:


### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |


### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |


## Szükséges modellek

Az alábbi modellek tesztelve és optimalizálva vannak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Letöltés a HF-ről

A modellek automatikusan letöltésre kerülnek a Hugging Face gyorsítótár könyvtárába: `~/.cache/huggingface/hub/`

Gondoskodjon legalább **20 GB szabad tárhelyről** a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről történő letöltéséhez. A letöltés után a playbook offline is futtatható.

- A modellek első letöltése a modell méretétől és a kapcsolat sebességétől függően **5–10 percet** vehet igénybe
- A modellek helyben, gyorsítótárazva kerülnek tárolásra, így nincs szükség ismételt letöltésre
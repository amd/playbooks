# Platform-konfiguráció

Ez a dokumentum ismerteti a jelen playbook futtatásához szükséges platformkonfigurációkat.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platformon. Minden más eszközön a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch-ot. Kérjük, tekintse meg az operációs rendszerének megfelelő szakaszt:

### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |

### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb    | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |

## Szükséges modellek

A következő modellek le vannak tesztelve és optimalizálva vannak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3B | ~10GB | Előre telepítve az AMD Ryzen AI Halo Developer Platformon; minden más eszközön manuálisan kell telepíteni |

A modellek automatikusan letöltésre kerülnek a Hugging Face gyorsítótár-könyvtárba:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Gondoskodjon legalább **20 GB szabad tárhelyről** a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről történő letöltéséhez. A letöltés után a playbook offline is futtatható.

- Az első alkalommal történő modell-letöltések a modell méretétől és a kapcsolat sebességétől függően **5-10 percet** vehetnek igénybe
- A modellek helyileg gyorsítótárazásra kerülnek, és nem szükséges őket ismételten letölteni
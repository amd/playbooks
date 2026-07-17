# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációkat írja le.

## Előfeltételek

PyTorch ROCm-támogatással előre telepítve van az AMD Ryzen™ AI Halo Developer Platform eszközön. Minden más eszköz esetén a felhasználóknak manuálisan kell telepíteniük a PyTorch-ot ROCm-támogatással. Kérjük, tekintse meg az operációs rendszerének megfelelő részt:

### Windows

| Összetevő     | Verzió          | Megjegyzések                      |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb  | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

### Linux

| Összetevő     | Verzió          | Megjegyzések                      |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 vagy újabb  | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

## Szükséges modellek

A következő modellek teszteltek és optimalizáltak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|--------|-------------|-------|----------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |

A modellek automatikusan letöltődnek a Hugging Face gyorsítótár könyvtárába:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Győződjön meg arról, hogy legalább **20 GB szabad hely** áll rendelkezésre a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről való letöltéséhez. A letöltés után a playbook offline módban is futtatható.

- Az első modellletöltések a modell méretétől és a kapcsolat sebességétől függően **5–10 percet** vehetnek igénybe
- A modellek helyben gyorsítótárazódnak, és nem szükséges újra letölteni őket
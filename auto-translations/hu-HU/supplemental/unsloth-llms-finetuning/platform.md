# Platform Configuration

Ez a dokumentum a playbook futtatásához szükséges platform-konfigurációkat írja le.

## Előfeltételek

A ROCm támogatással rendelkező PyTorch előre telepítve van az AMD Ryzen™ AI Halo Developer Platform eszközön. Minden más eszköz esetén a felhasználóknak manuálisan kell telepíteniük a ROCm támogatással rendelkező PyTorch-ot. Kérjük, tekintse meg az operációs rendszerének megfelelő részt:


### Windows

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |


### Linux

| Komponens     | Verzió         | Megjegyzések                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Előre telepítve az AMD Ryzen AI Halo Developer Platform eszközön; minden más eszközön manuálisan kell telepíteni |


## Szükséges modellek

A következő modellek teszteltek és optimalizáltak az Ön platformjához:

| Modell | Paraméterek | Méret | Letöltési hely |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Letöltés a HF-ről

A modellek automatikusan letöltődnek a Hugging Face gyorsítótár könyvtárába: `~/.cache/huggingface/hub/`

Gondoskodjon legalább **20 GB szabad területről** a modellek tárolásához.

## Hálózati követelmények

A kezdeti beállításhoz internetkapcsolat szükséges a modellek Hugging Face-ről való letöltéséhez. A letöltés után a playbook offline módban is futtatható.

- Az első modellletöltések a modell méretétől és a kapcsolat sebességétől függően **5–10 percet** vehetnek igénybe
- A modellek helyben gyorsítótárazódnak, és nem szükséges újra letölteni őket
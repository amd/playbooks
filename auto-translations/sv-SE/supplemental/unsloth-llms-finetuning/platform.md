# Plattformskonfiguration

Det här dokumentet beskriver de förväntade plattformskonfigurationerna för att köra den här spelboken.

## Förutsättningar

PyTorch med ROCm-stöd är förinstallerat på AMD Ryzen™ AI Halo Developer Platform. För alla andra enheter måste användare manuellt installera PyTorch med ROCm-stöd. Se relevant avsnitt för ditt operativsystem:

### Windows

| Komponent     | Version         | Anteckningar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |


### Linux

| Komponent     | Version         | Anteckningar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |


## Nödvändiga modeller

Följande modeller är testade och optimerade för din plattform:

| Modell | Parametrar | Storlek | Nedladdningsplats |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Ladda ned från HF

Modeller laddas automatiskt ned till Hugging Face-cachekatalogen: `~/.cache/huggingface/hub/`

Se till att det finns minst **20 GB ledigt utrymme** för modelllagring.

## Nätverkskrav

Den inledande installationen kräver internetåtkomst för att ladda ned modeller från Hugging Face. Efter nedladdningen kan spelboken köras offline.

- Första gångens modellnedladdningar kan ta **5–10 minuter** beroende på modellstorlek och anslutningshastighet
- Modeller cachas lokalt och behöver inte laddas ned igen
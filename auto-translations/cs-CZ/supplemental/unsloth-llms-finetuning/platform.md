# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadavky

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. U všech ostatních zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Přečtěte si prosím příslušnou část podle vašeho operačního systému:


### Windows

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |


### Linux

| Component     | Version         | Notes                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |


## Požadované modely

Následující modely jsou otestované a optimalizované pro vaši platformu:

| Model | Parameters | Size | Download Location |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Stáhnout z HF

Modely budou automaticky staženy do mezipaměti Hugging Face: `~/.cache/huggingface/hub/`

Zajistěte alespoň **20 GB volného místa** pro ukládání modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu pro stažení modelů z Hugging Face. Po stažení může playbook fungovat offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy lokálně v mezipaměti a není nutné je stahovat znovu
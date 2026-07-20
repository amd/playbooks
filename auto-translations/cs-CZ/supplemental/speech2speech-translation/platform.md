# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadavky

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. U všech ostatních zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Postupujte podle příslušné sekce pro váš operační systém:

### Windows

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 nebo novější    | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

### Linux

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 nebo novější    | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

## Požadované modely

Následující modely jsou otestovány a optimalizovány pro vaši platformu:

| Model | Parametry | Velikost | Umístění ke stažení |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

Modely budou automaticky staženy do mezipaměti Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zajistěte alespoň **20 GB volného místa** pro ukládání modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu ke stažení modelů z Hugging Face. Po stažení může playbook fungovat offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy lokálně v mezipaměti a není potřeba je znovu stahovat
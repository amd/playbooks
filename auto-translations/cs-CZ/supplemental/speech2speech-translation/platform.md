# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Předpoklady

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. Pro všechna ostatní zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Prosím, přečtěte si příslušnou část pro váš operační systém:

### Windows

| Komponenta    | Verze           | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 nebo novější | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

### Linux

| Komponenta    | Verze           | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 nebo novější | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

## Požadované modely

Následující modely jsou otestovány a optimalizovány pro vaši platformu:

| Model | Parametry | Velikost | Umístění ke stažení |
|-------|-----------|----------|---------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10 GB | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

Modely budou automaticky staženy do adresáře mezipaměti Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zajistěte alespoň **20 GB volného místa** pro uložení modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu pro stažení modelů z Hugging Face. Po stažení může playbook běžet offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy v místní mezipaměti a není třeba je znovu stahovat
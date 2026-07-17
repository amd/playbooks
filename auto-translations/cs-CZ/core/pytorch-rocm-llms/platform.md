<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Předpoklady

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. Pro všechna ostatní zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Postupujte prosím podle příslušné části pro váš operační systém:

### Windows

| Komponenta    | Verze           | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 nebo novější | Předinstalován na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

### Linux

| Komponenta    | Verze           | Poznámky                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 nebo novější | Předinstalován na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

## Požadované modely

Následující modely jsou otestovány a optimalizovány pro vaši platformu:

| Model | Parametry | Velikost | Umístění ke stažení |
|-------|-----------|----------|---------------------|
| **openai/gpt-oss-20b** | 20B | ~40 GB | Předinstalován na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutná ruční instalace |

Modely budou automaticky staženy do adresáře mezipaměti Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zajistěte alespoň **50 GB volného místa** pro uložení modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu pro stažení modelů z Hugging Face. Po stažení může playbook běžet offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy v místní mezipaměti a není třeba je znovu stahovat
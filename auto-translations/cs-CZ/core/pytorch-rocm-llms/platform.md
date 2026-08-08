<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění tohoto playbooku.

## Požadavky

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. U všech ostatních zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Postupujte podle příslušné části pro váš operační systém:

### Windows

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 nebo novější    | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

### Linux

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 nebo novější    | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

## Požadované modely

Následující modely jsou otestovány a optimalizovány pro vaši platformu:

| Model | Parametry | Velikost | Umístění ke stažení |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |

Modely budou automaticky stahovány do mezipaměti Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zajistěte alespoň **50 GB volného místa** pro úložiště modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu ke stažení modelů z Hugging Face. Po stažení může playbook fungovat offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy lokálně v mezipaměti a není třeba je stahovat znovu
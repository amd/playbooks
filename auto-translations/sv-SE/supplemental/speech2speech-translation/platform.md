<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Maskinöversättning.** Den här sidan har automatiskt översatts från engelska och har inte granskats av en människa. Den kan innehålla fel, och vissa steg, kommandon, nedladdningar eller produkttillgänglighet kan skilja sig åt i ditt språk eller din region. Om något verkar fel bör du betrakta den ursprungliga engelska spelboken som den korrekta källan.
<!-- auto-translated-disclaimer:end -->

# Plattformskonfiguration

Detta dokument beskriver de förväntade plattformskonfigurationerna för att köra denna playbook.

## Förutsättningar

PyTorch med ROCm-stöd är förinstallerat på AMD Ryzen™ AI Halo Developer Platform. För alla andra enheter måste användare manuellt installera PyTorch med ROCm-stöd. Se relevant avsnitt för ditt operativsystem:

### Windows

| Komponent     | Version         | Anteckningar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyare    | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |

### Linux

| Komponent     | Version         | Anteckningar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 eller nyare    | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |

## Nödvändiga modeller

Följande modeller är testade och optimerade för din plattform:

| Modell | Parametrar | Storlek | Nedladdningsplats |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2,3B | ~10GB | Förinstallerad på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |

Modeller laddas automatiskt ned till Hugging Face-cachekatalogen:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Se till att ha minst **20 GB ledigt utrymme** för modellagring.

## Nätverkskrav

Den första installationen kräver internetåtkomst för att ladda ned modeller från Hugging Face. Efter nedladdningen kan playbooken köras offline.

- Första nedladdningen av modeller kan ta **5–10 minuter** beroende på modellstorlek och anslutningshastighet
- Modeller cachas lokalt och behöver inte laddas ned igen
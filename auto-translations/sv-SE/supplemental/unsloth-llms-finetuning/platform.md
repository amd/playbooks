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
| **PyTorch**   | 2.11.x + ROCm 7.13  | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |


### Linux

| Komponent     | Version         | Anteckningar                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Förinstallerat på AMD Ryzen AI Halo Developer Platform; måste installeras manuellt på alla andra enheter |


## Obligatoriska modeller

Följande modeller är testade och optimerade för din plattform:

| Modell | Parametrar | Storlek | Nedladdningsplats |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Ladda ner från HF

Modeller laddas automatiskt ner till Hugging Face-cachekatalogen: `~/.cache/huggingface/hub/`

Se till att det finns minst **20 GB ledigt utrymme** för modellagring.

## Nätverkskrav

Den initiala installationen kräver internetåtkomst för att ladda ner modeller från Hugging Face. Efter nedladdningen kan playbooken köras offline.

- Nedladdning av modeller för första gången kan ta **5–10 minuter** beroende på modellstorlek och anslutningshastighet
- Modeller cachas lokalt och behöver inte laddas ner igen
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Strojový překlad.** Tato stránka byla automaticky přeložena z angličtiny a nebyla zkontrolována člověkem. Může obsahovat chyby a určité pokyny, příkazy, soubory ke stažení, dostupnost produktů nebo jiný obsah se může lišit podle jazyka nebo regionu. V případě jakéhokoli nesouladu nebo rozporu je rozhodující původní anglická verze playbooku.
<!-- auto-translated-disclaimer:end -->

# Konfigurace platformy

Tento dokument popisuje očekávané konfigurace platformy pro spuštění této příručky (playbook).

## Požadavky

PyTorch s podporou ROCm je předinstalován na platformě AMD Ryzen™ AI Halo Developer Platform. U všech ostatních zařízení musí uživatelé nainstalovat PyTorch s podporou ROCm ručně. Přejděte prosím do příslušné sekce pro váš operační systém:


### Windows

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |


### Linux

| Komponenta     | Verze         | Poznámky                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Předinstalováno na platformě AMD Ryzen AI Halo Developer Platform; na všech ostatních zařízeních je nutné nainstalovat ručně |


## Požadované modely

Následující modely jsou otestovány a optimalizovány pro vaši platformu:

| Model | Parametry | Velikost | Umístění ke stažení |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Stáhnout z HF

Modely budou automaticky staženy do mezipaměti Hugging Face: `~/.cache/huggingface/hub/`

Zajistěte alespoň **20 GB volného místa** pro uložení modelů.

## Požadavky na síť

Počáteční nastavení vyžaduje přístup k internetu pro stažení modelů z Hugging Face. Po stažení může příručka (playbook) běžet offline.

- První stažení modelů může trvat **5–10 minut** v závislosti na velikosti modelu a rychlosti připojení
- Modely jsou uloženy v místní mezipaměti a není nutné je znovu stahovat
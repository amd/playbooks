<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika (playbook).

## Preduslovi

PyTorch sa ROCm podrškom je unapred instaliran na AMD Ryzen™ AI Halo Developer Platform. Za sve ostale uređaje, korisnici moraju ručno instalirati PyTorch sa ROCm podrškom. Pogledajte relevantnu sekciju za vaš operativni sistem:

### Windows

| Komponenta     | Verzija         | Napomene                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ili novija    | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

### Linux

| Komponenta     | Verzija         | Napomene                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 ili novija    | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

## Potrebni modeli

Sledeći modeli su testirani i optimizovani za vašu platformu:

| Model | Parametri | Veličina | Lokacija preuzimanja |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

Modeli će automatski biti preuzeti u Hugging Face keš direktorijum:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Obezbedite najmanje **20GB slobodnog prostora** za skladištenje modela.

## Mrežni zahtevi

Početno podešavanje zahteva pristup internetu za preuzimanje modela sa Hugging Face. Nakon preuzimanja, priručnik može da radi bez internet konekcije.

- Prvo preuzimanje modela može trajati **5-10 minuta** u zavisnosti od veličine modela i brzine konekcije
- Modeli se keširaju lokalno i ne moraju se ponovo preuzimati
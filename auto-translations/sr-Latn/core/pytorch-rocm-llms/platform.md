<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika.

## Preduslovi

PyTorch sa ROCm podrškom je unapred instaliran na AMD Ryzen™ AI Halo Developer Platform. Za sve ostale uređaje, korisnici moraju ručno instalirati PyTorch sa ROCm podrškom. Pogledajte odgovarajući odeljak za vaš operativni sistem:

### Windows

| Komponenta    | Verzija         | Napomene                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ili noviji  | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

### Linux

| Komponenta    | Verzija         | Napomene                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ili noviji  | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

## Potrebni modeli

Sledeći modeli su testirani i optimizovani za vašu platformu:

| Model | Parametri | Veličina | Lokacija za preuzimanje |
|-------|-----------|----------|-------------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

Modeli će biti automatski preuzeti u Hugging Face direktorijum keša:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Osigurajte najmanje **50GB slobodnog prostora** za skladištenje modela.

## Mrežni zahtevi

Početno podešavanje zahteva pristup internetu radi preuzimanja modela sa Hugging Face. Nakon preuzimanja, priručnik može da radi bez interneta.

- Prvo preuzimanje modela može trajati **5-10 minuta** u zavisnosti od veličine modela i brzine veze
- Modeli se keširaju lokalno i ne moraju ponovo da se preuzimaju
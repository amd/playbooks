<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Mašinski prevod.** Ova stranica je automatski prevedena sa engleskog jezika i nije proveravana od strane čoveka. Može sadržati greške, a određena uputstva, komande, preuzimanja, dostupnost proizvoda ili drugi sadržaj mogu se razlikovati u zavisnosti od jezika ili regiona. U slučaju bilo kakve nedoslednosti ili neslaganja, merodavna je originalna verzija playbook-a na engleskom jeziku.
<!-- auto-translated-disclaimer:end -->

# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika (playbook).

## Preduslovi

PyTorch sa ROCm podrškom je unapred instaliran na AMD Ryzen™ AI Halo Developer Platform. Za sve ostale uređaje, korisnici moraju ručno instalirati PyTorch sa ROCm podrškom. Pogledajte odgovarajući odeljak za svoj operativni sistem:

### Windows

| Komponenta     | Verzija         | Napomene                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ili novija    | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

### Linux

| Komponenta     | Verzija         | Napomene                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 ili novija    | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

## Potrebni modeli

Sledeći modeli su testirani i optimizovani za vašu platformu:

| Model | Parametri | Veličina | Lokacija preuzimanja |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

Modeli će se automatski preuzeti u keš direktorijum za Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Obezbedite najmanje **50GB slobodnog prostora** za skladištenje modela.

## Mrežni zahtevi

Za početno podešavanje potreban je pristup internetu radi preuzimanja modela sa Hugging Face. Nakon preuzimanja, priručnik može da radi bez internetske veze.

- Prvo preuzimanje modela može trajati **5-10 minuta**, u zavisnosti od veličine modela i brzine veze
- Modeli se keširaju lokalno i ne moraju ponovo da se preuzimaju
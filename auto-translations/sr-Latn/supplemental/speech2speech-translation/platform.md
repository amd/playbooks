# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog playbook-a.

## Preduslovi

PyTorch sa ROCm podrškom je unapred instaliran na AMD Ryzen™ AI Halo Developer Platform. Za sve ostale uređaje, korisnici moraju ručno instalirati PyTorch sa ROCm podrškom. Pogledajte odgovarajući odeljak za vaš operativni sistem:

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

| Model | Parametri | Veličina | Lokacija za preuzimanje |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |

Modeli će automatski biti preuzeti u keš direktorijum za Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Obezbedite najmanje **20GB slobodnog prostora** za skladištenje modela.

## Zahtevi za mrežu

Početno podešavanje zahteva pristup internetu za preuzimanje modela sa Hugging Face. Nakon preuzimanja, playbook može da radi bez internet konekcije.

- Prvo preuzimanje modela može trajati **5-10 minuta**, u zavisnosti od veličine modela i brzine konekcije
- Modeli se lokalno keširaju i nije ih potrebno ponovo preuzimati
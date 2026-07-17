# Konfiguracija platforme

Ovaj dokument opisuje očekivane konfiguracije platforme za pokretanje ovog priručnika.

## Preduslovi

PyTorch sa ROCm podrškom je unapred instaliran na AMD Ryzen™ AI Halo Developer Platform. Za sve ostale uređaje, korisnici moraju ručno instalirati PyTorch sa ROCm podrškom. Pogledajte odgovarajući odeljak za vaš operativni sistem:

### Windows

| Komponenta    | Verzija         | Napomene                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |


### Linux

| Komponenta    | Verzija         | Napomene                          |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Unapred instaliran na AMD Ryzen AI Halo Developer Platform; mora se ručno instalirati na svim ostalim uređajima |


## Potrebni modeli

Sledeći modeli su testirani i optimizovani za vašu platformu:

| Model | Parametri | Veličina | Lokacija za preuzimanje |
|-------|-----------|----------|-------------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Preuzmi sa HF

Modeli će biti automatski preuzeti u Hugging Face direktorijum keša: `~/.cache/huggingface/hub/`

Osigurajte najmanje **20GB slobodnog prostora** za skladištenje modela.

## Mrežni zahtevi

Početno podešavanje zahteva pristup internetu radi preuzimanja modela sa Hugging Face. Nakon preuzimanja, priručnik može da radi bez interneta.

- Prvo preuzimanje modela može trajati **5-10 minuta** u zavisnosti od veličine modela i brzine veze
- Modeli se keširaju lokalno i ne moraju ponovo da se preuzimaju
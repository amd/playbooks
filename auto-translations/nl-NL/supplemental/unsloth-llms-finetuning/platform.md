# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van deze playbook.

## Vereisten

PyTorch met ROCm-ondersteuning is vooraf geïnstalleerd op het AMD Ryzen™ AI Halo Developer Platform. Voor alle andere apparaten moeten gebruikers PyTorch met ROCm-ondersteuning handmatig installeren. Raadpleeg de relevante sectie voor uw besturingssysteem:


### Windows

| Component     | Versie         | Opmerkingen                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |


### Linux

| Component     | Versie         | Opmerkingen                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |


## Vereiste modellen

De volgende modellen zijn getest en geoptimaliseerd voor uw platform:

| Model | Parameters | Grootte | Downloadlocatie |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Downloaden van HF

Modellen worden automatisch gedownload naar de Hugging Face-cachemap: `~/.cache/huggingface/hub/`

Zorg voor ten minste **20GB vrije ruimte** voor modelopslag.

## Netwerkvereisten

Bij de eerste installatie is internettoegang vereist om modellen van Hugging Face te downloaden. Na het downloaden kan de playbook offline worden uitgevoerd.

- Het downloaden van modellen kan de eerste keer **5-10 minuten** duren, afhankelijk van de modelgrootte en verbindingssnelheid
- Modellen worden lokaal opgeslagen in de cache en hoeven niet opnieuw te worden gedownload
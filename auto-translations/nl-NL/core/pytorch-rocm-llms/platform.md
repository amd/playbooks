<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereisten

PyTorch met ROCm-ondersteuning is vooraf geïnstalleerd op het AMD Ryzen™ AI Halo Developer Platform. Voor alle andere apparaten moeten gebruikers PyTorch met ROCm-ondersteuning handmatig installeren. Raadpleeg de relevante sectie voor uw besturingssysteem:

### Windows

| Component     | Versie          | Opmerkingen                       |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 of nieuwer  | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

### Linux

| Component     | Versie          | Opmerkingen                       |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 of nieuwer  | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

## Vereiste modellen

De volgende modellen zijn getest en geoptimaliseerd voor uw platform:

| Model | Parameters | Grootte | Downloadlocatie |
|-------|------------|---------|-----------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

Modellen worden automatisch gedownload naar de Hugging Face-cachemap:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zorg voor minimaal **50 GB vrije ruimte** voor modelopslag.

## Netwerkvereisten

Voor de initiële installatie is internettoegang vereist om modellen te downloaden van Hugging Face. Na het downloaden kan het playbook offline worden uitgevoerd.

- Eerste modeldownloads kunnen **5 tot 10 minuten** duren, afhankelijk van de modelgrootte en verbindingssnelheid
- Modellen worden lokaal gecached en hoeven niet opnieuw te worden gedownload
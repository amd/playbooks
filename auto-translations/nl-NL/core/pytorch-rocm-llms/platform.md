<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Machinevertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Deze pagina kan fouten bevatten en bepaalde instructies, opdrachten, downloads, productbeschikbaarheid of andere inhoud kan per taal of regio verschillen. In geval van tegenstrijdigheid of discrepantie is de oorspronkelijke Engelse versie van de playbook doorslaggevend en prevaleert deze.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van dit playbook.

## Vereisten

PyTorch met ROCm-ondersteuning is vooraf geïnstalleerd op het AMD Ryzen™ AI Halo Developer Platform. Voor alle andere apparaten moeten gebruikers PyTorch met ROCm-ondersteuning handmatig installeren. Raadpleeg het relevante gedeelte voor uw besturingssysteem:

### Windows

| Component     | Versie          | Opmerkingen                        |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 of nieuwer  | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

### Linux

| Component     | Versie          | Opmerkingen                        |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 of nieuwer  | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

## Vereiste modellen

De volgende modellen zijn getest en geoptimaliseerd voor uw platform:

| Model | Parameters | Grootte | Downloadlocatie |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | Vooraf geïnstalleerd op het AMD Ryzen AI Halo Developer Platform; moet handmatig worden geïnstalleerd op alle andere apparaten |

Modellen worden automatisch gedownload naar de Hugging Face-cachemap:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Zorg voor ten minste **50GB vrije ruimte** voor modelopslag.

## Netwerkvereisten

Voor de eerste installatie is internettoegang nodig om modellen van Hugging Face te downloaden. Na het downloaden kan het playbook offline worden uitgevoerd.

- Het downloaden van modellen voor de eerste keer kan **5-10 minuten** duren, afhankelijk van de modelgrootte en verbindingssnelheid
- Modellen worden lokaal in de cache opgeslagen en hoeven niet opnieuw te worden gedownload
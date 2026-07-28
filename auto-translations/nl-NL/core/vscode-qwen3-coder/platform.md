<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Automatische vertaling.** Deze pagina is automatisch vertaald vanuit het Engels en is niet door een mens gecontroleerd. Ze kan fouten bevatten en sommige stappen, commando's, downloads of productbeschikbaarheid kunnen afwijken in uw taal of regio. Raadpleeg bij twijfel de originele Engelstalige playbook als bron van waarheid.
<!-- auto-translated-disclaimer:end -->

# Platformconfiguratie

Dit document beschrijft de verwachte platformconfiguraties voor het uitvoeren van deze playbook.

## Windows

### LM Studio-installatie

LM Studio moet vooraf zijn geïnstalleerd:

| Component | Versie | Locatie |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Model downloaden

De volgende modellen moeten al aanwezig zijn in de LM Studio-modellenmap (`C:\Users\...\.lmstudio\models`):

| Modeltype | Kwantisatie | Grootte | Locatie |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio-installatie

Zie lmstudio.md (in de map dependencies) voor meer details.

### Model downloaden

Hetzelfde als op Windows.
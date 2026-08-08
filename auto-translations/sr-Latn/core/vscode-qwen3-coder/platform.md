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

## Windows

### Instalacija LM Studio

LM Studio treba biti unapred instaliran:

| Komponenta | Verzija | Lokacija |
|-----------|---------|----------|
| **LM Studio (Modeli + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Keš)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Preuzimanje modela

Sledeći modeli bi već trebalo da se nalaze u direktorijumu modela LM Studio (`C:\Users\...\.lmstudio\models`):

| Tip modela | Kvantizacija | Veličina | Lokacija |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalacija LM Studio

Pogledajte lmstudio.md (unutar foldera dependencies) za više detalja.

### Preuzimanje modela

Isto kao na Windows-u.
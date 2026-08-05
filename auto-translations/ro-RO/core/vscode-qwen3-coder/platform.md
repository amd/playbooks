<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurare platformă

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Windows

### Instalarea LM Studio

LM Studio ar trebui să fie preinstalat:

| Componentă | Versiune | Locație |
|-----------|---------|----------|
| **LM Studio (Modele + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Descărcarea modelului

Următoarele modele ar trebui să fie deja prezente în directorul de modele LM Studio (`C:\Users\...\.lmstudio\models`):

| Tip model | Cuantizare | Dimensiune | Locație |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Instalarea LM Studio

Consultați lmstudio.md (în folderul dependencies) pentru mai multe detalii.

### Descărcarea modelului

La fel ca pe Windows.
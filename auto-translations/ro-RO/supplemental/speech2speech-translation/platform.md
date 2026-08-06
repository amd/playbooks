<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

# Configurația platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Cerințe preliminare

PyTorch cu suport ROCm este preinstalat pe AMD Ryzen™ AI Halo Developer Platform. Pentru toate celelalte dispozitive, utilizatorii trebuie să instaleze manual PyTorch cu suport ROCm. Vă rugăm să consultați secțiunea relevantă pentru sistemul dvs. de operare:

### Windows

| Componentă     | Versiune         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 sau mai nouă    | Preinstalat pe AMD Ryzen AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |

### Linux

| Componentă     | Versiune         | Note                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 sau mai nouă    | Preinstalat pe AMD Ryzen AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |

## Modele necesare

Următoarele modele sunt testate și optimizate pentru platforma dvs.:

| Model | Parametri | Dimensiune | Locație de descărcare |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | Preinstalat pe AMD Ryzen AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |

Modelele vor fi descărcate automat în directorul cache Hugging Face:
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

Asigurați-vă că aveți cel puțin **20GB spațiu liber** pentru stocarea modelelor.

## Cerințe de rețea

Configurarea inițială necesită acces la internet pentru a descărca modele de pe Hugging Face. După descărcare, playbook-ul poate rula offline.

- Descărcările inițiale ale modelelor pot dura **5-10 minute**, în funcție de dimensiunea modelului și viteza conexiunii
- Modelele sunt stocate local în cache și nu trebuie descărcate din nou
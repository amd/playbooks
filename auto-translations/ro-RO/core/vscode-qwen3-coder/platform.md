<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurarea Platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Windows

### Instalarea LM Studio

LM Studio ar trebui să fie pre-instalat:

| Componentă | Versiune | Locație |
|-----------|---------|----------|
| **LM Studio (Modele + Diverse)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Descărcarea Modelelor

Următoarele modele ar trebui să fie deja prezente în directorul de modele LM Studio (`C:\Users\...\.lmstudio\models`):

| Tip Model | Cuantizare | Dimensiune | Locație |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18,2 GB | `models\lmstudio-community` |

---

## Linux

### Instalarea LM Studio

Consultați lmstudio.md (din folderul de dependențe) pentru mai multe detalii.

### Descărcarea Modelelor

La fel ca pe Windows.
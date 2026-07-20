<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configurazione della piattaforma

Questo documento descrive le configurazioni della piattaforma previste per l'esecuzione di questo playbook.

## Windows

### Installazione di LM Studio

LM Studio dovrebbe essere già preinstallato:

| Componente | Versione | Posizione |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Download del modello

I seguenti modelli dovrebbero essere già presenti nella directory dei modelli di LM Studio (`C:\Users\...\.lmstudio\models`):

| Tipo di modello | Quantizzazione | Dimensione | Posizione |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Installazione di LM Studio

Per maggiori dettagli, consultare lmstudio.md (all'interno della cartella dependencies).

### Download del modello

Come su Windows.
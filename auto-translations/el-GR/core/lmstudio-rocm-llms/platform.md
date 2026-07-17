<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Διαμόρφωση Πλατφόρμας

Αυτό το έγγραφο περιγράφει τις αναμενόμενες διαμορφώσεις πλατφόρμας για την εκτέλεση αυτού του playbook.

## Windows

### Εγκατάσταση LM Studio

Το LM Studio θα πρέπει να είναι προεγκατεστημένο:

| Στοιχείο | Έκδοση | Τοποθεσία |
|-----------|---------|----------|
| **LM Studio (Μοντέλα + Διάφορα)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Πρόγραμμα)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Λήψη Μοντέλου

Τα παρακάτω μοντέλα θα πρέπει να υπάρχουν ήδη στον κατάλογο μοντέλων του LM Studio (`C:\Users\...\.lmstudio\models`):

| Συσκευή | Τύπος Μοντέλου | Κβαντοποίηση | Μέγεθος (GB) | Τοποθεσία |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### Εγκατάσταση LM Studio

Δείτε το [lmstudio.md](../../dependencies/lmstudio.md) για περισσότερες λεπτομέρειες.

### Λήψη Μοντέλου

Ίδια με τα Windows.
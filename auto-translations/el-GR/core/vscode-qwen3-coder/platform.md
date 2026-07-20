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
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### Λήψη Μοντέλου

Τα ακόλουθα μοντέλα θα πρέπει να βρίσκονται ήδη στον κατάλογο μοντέλων του LM Studio (`C:\Users\...\.lmstudio\models`):

| Τύπος Μοντέλου | Κβαντισμός | Μέγεθος | Τοποθεσία |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### Εγκατάσταση LM Studio

Δείτε το lmstudio.md (μέσα στον φάκελο dependencies) για περισσότερες λεπτομέρειες.

### Λήψη Μοντέλου

Ίδια διαδικασία με τα Windows.
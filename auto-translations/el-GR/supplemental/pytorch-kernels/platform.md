<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

# Platform Configuration

Αυτό το έγγραφο περιγράφει την αναμενόμενη διαμόρφωση πλατφόρμας για την εκτέλεση αυτού του playbook.

## Required Apps / Frameworks

| Component       | Expected Configuration               | Notes                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python with `venv` support         | Χρησιμοποιείται για τη δημιουργία και ενεργοποίηση του `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 package family             | Εγκαθίσταται μέσω της ροής εξαρτήσεων του playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Απαιτείται για τα `torch.cuda`, το HIP runtime, τη μεταγλώττιση JIT, και το `CUDAExtension` |
| GPU Driver      | AMD GPU driver with ROCm/HIP support | Απαιτείται πριν το PyTorch μπορέσει να εντοπίσει την AMD GPU                               |

> Σημείωση: Εάν εκτελείτε σε AMD Ryzen™ AI Halo Developer Platform, το λογισμικό AMD ROCm™ και το PyTorch είναι προεγκατεστημένα.

## Linux Prerequisites

Απαιτούνται τα ακόλουθα πακέτα συστήματος:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* Το `python3-venv` απαιτείται για τη δημιουργία του `kernel-env`.
* Τα `build-essential`, `gcc`, και `g++` απαιτούνται για τους οδηγούς επεκτάσεων C++.
* Το `amd-smi` χρησιμοποιείται για ελέγχους ορατότητας/χρήσης GPU σε Linux.

Τα παραδείγματα επεκτάσεων C++ δημιουργούν εγγενή αρθρώματα `.so` από αρχεία `.cu` χρησιμοποιώντας το μονοπάτι `CUDAExtension` του PyTorch.

## Windows Prerequisites

Οι εκτελεστές Windows απαιτούν:

* Διαθέσιμη Python μέσω `python`
* Εγκατάσταση της πιο πρόσφατης έκδοσης: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ή [νεότερο](https://visualstudio.microsoft.com/vs/community/) με το φόρτο εργασίας **Desktop development with C++**

Το περιβάλλον Visual Studio C++ πρέπει να παρέχει:
* `vcvars64.bat`
* `cl.exe`
* Διαδρομές include και library του Windows SDK

Τα παραδείγματα επεκτάσεων C++ δημιουργούν εγγενή αρθρώματα `.pyd` από αρχεία `.cu` χρησιμοποιώντας το μονοπάτι `CUDAExtension` του PyTorch.
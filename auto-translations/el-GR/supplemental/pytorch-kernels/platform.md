<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Διαμόρφωση Πλατφόρμας

Αυτό το έγγραφο περιγράφει την αναμενόμενη διαμόρφωση πλατφόρμας για την εκτέλεση αυτού του playbook.

## Απαιτούμενες Εφαρμογές / Frameworks

| Component       | Expected Configuration               | Notes                                                                        |
| --------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Python          | Python με υποστήριξη `venv`         | Χρησιμοποιείται για τη δημιουργία και ενεργοποίηση του `kernel-env`                                     |
| ROCm Python SDK | ROCm 7.13 package family             | Εγκαθίσταται μέσω της ροής εξαρτήσεων του playbook                               |
| PyTorch ROCm    | PyTorch 2.11.0 + ROCm 7.13           | Απαιτείται για `torch.cuda`, HIP runtime, JIT compilation και `CUDAExtension` |
| GPU Driver      | AMD GPU driver με υποστήριξη ROCm/HIP | Απαιτείται πριν το PyTorch μπορέσει να εντοπίσει το AMD GPU                               |

> Σημείωση: Εάν εκτελείτε σε AMD Ryzen™ AI Halo Developer Platform, το AMD ROCm™ software και το PyTorch είναι προεγκατεστημένα.

## Προαπαιτούμενα Linux

Απαιτούνται τα ακόλουθα πακέτα συστήματος:

```bash
sudo apt update
sudo apt install -y python3-venv build-essential gcc g++
```

* Το `python3-venv` απαιτείται για τη δημιουργία του `kernel-env`.
* Τα `build-essential`, `gcc` και `g++` απαιτούνται για τις αναλυτικές παρουσιάσεις επέκτασης C++.
* Το `amd-smi` χρησιμοποιείται για ελέγχους ορατότητας/χρήσης GPU στο Linux.

Τα παραδείγματα επέκτασης C++ δημιουργούν εγγενή modules `.so` από αρχεία `.cu` χρησιμοποιώντας το μονοπάτι `CUDAExtension` του PyTorch.

## Προαπαιτούμενα Windows

Οι εκτελεστές Windows απαιτούν:

* Python διαθέσιμο μέσω `python`
* Εγκατάσταση της πιο πρόσφατης έκδοσης: [AMD Software: Adrenalin Edition™](https://www.amd.com/en/products/software/adrenalin.html)
* [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) ή [νεότερη](https://visualstudio.microsoft.com/vs/community/) με το φόρτο εργασίας **Desktop development with C++**

Το περιβάλλον C++ του Visual Studio πρέπει να παρέχει:
* `vcvars64.bat`
* `cl.exe`
* Διαδρομές include και library του Windows SDK

Τα παραδείγματα επέκτασης C++ δημιουργούν εγγενή modules `.pyd` από αρχεία `.cu` χρησιμοποιώντας το μονοπάτι `CUDAExtension` του PyTorch.
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του GPT-OSS 120B στο LM Studio

<!-- @device:halo_box -->
> **Σημείωση:** Αν αυτό το μοντέλο είναι ήδη διαθέσιμο στο LM Studio, μπορείτε να παραλείψετε αυτή την ενότητα. Διαφορετικά, ακολουθήστε τα παρακάτω βήματα για να το κατεβάσετε.
<!-- @device:end -->

Για να κατεβάσετε το μοντέλο GPT-OSS 120B:

1. Πατήστε "Ctrl" + "Shift" + "M" στο πληκτρολόγιό σας ή κάντε κλικ στην καρτέλα "Discover" (εικονίδιο μεγεθυντικού φακού) στην πλαϊνή μπάρα αριστερά
2. Αναζητήστε `ggml-org/gpt-oss-120b-GGUF`
3. Επιλέξτε `mxfp4` και κάντε κλικ στο Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

Το LM Studio θα κατεβάσει αυτόματα και θα τοποθετήσει το μοντέλο στον σωστό κατάλογο.

Αν επιθυμείτε να κατεβάσετε επιπλέον μοντέλα, μπορείτε να τα αναζητήσετε στην καρτέλα Discover και το LM Studio θα αναλάβει τα υπόλοιπα.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->
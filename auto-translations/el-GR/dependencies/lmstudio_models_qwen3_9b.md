<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3.5 9B στο LM Studio

Για να κατεβάσετε το μοντέλο Qwen3.5 9B:

1. Πατήστε "Ctrl" + "Shift" + "M" στο πληκτρολόγιό σας ή κάντε κλικ στην καρτέλα "Discover" (εικονίδιο Μεγεθυντικού Φακού) στην αριστερή πλαϊνή μπάρα
2. Αναζητήστε `Qwen3.5 9B`
3. Επιλέξτε μια κβαντοποίηση (το προτεινόμενο `Q4_K_M` είναι μια καλή ισορροπία μεγέθους και ποιότητας) και κάντε κλικ στο Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

Το LM Studio θα κατεβάσει αυτόματα το μοντέλο και θα το τοποθετήσει στον σωστό κατάλογο.

Αν επιθυμείτε να κατεβάσετε επιπλέον μοντέλα, μπορείτε να τα αναζητήσετε στην καρτέλα Discover και το LM Studio θα αναλάβει τα υπόλοιπα.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->
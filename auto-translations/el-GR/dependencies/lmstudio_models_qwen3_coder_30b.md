<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3-Coder 30B στο LM Studio

Για να κατεβάσετε το μοντέλο Qwen3-Coder 30B:

1. Πατήστε "Ctrl" + "Shift" + "M" στο πληκτρολόγιό σας ή κάντε κλικ στην καρτέλα "Discover" (εικονίδιο μεγεθυντικού φακού) στην πλευρική γραμμή αριστερά
2. Αναζητήστε `Qwen3-Coder-30B-A3B`
3. Επιλέξτε μια κβαντοποίηση (η προτεινόμενη `Q4_K_M` προσφέρει καλή ισορροπία μεγέθους και ποιότητας) και κάντε κλικ στο Download

Το LM Studio θα κατεβάσει αυτόματα και θα τοποθετήσει το μοντέλο στον σωστό κατάλογο.

Εάν επιθυμείτε να κατεβάσετε επιπλέον μοντέλα, μπορείτε να τα αναζητήσετε στην καρτέλα Discover και το LM Studio θα αναλάβει τα υπόλοιπα.

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->
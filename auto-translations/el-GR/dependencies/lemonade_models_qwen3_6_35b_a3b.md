<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3.6 35B A3B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Η εντολή `lemonade run Qwen3.6-35B-A3B-GGUF` επίσης κατεβάζει το μοντέλο με την πρώτη χρήση εάν δεν είναι ήδη διαθέσιμο, και στη συνέχεια το φορτώνει για συμπερασμό.

Το μοντέλο εμφανίζεται στη λίστα κατεβασμένων μοντέλων του διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
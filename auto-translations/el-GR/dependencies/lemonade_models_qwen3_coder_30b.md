<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3-Coder 30B A3B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Η εντολή `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` κάνει επίσης λήψη του μοντέλου κατά την πρώτη χρήση, εφόσον δεν υπάρχει ήδη, και στη συνέχεια το φορτώνει για συμπερασμό (inference).

Το μοντέλο εμφανίζεται στη λίστα των ληφθέντων μοντέλων του διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
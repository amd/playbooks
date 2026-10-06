<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3.5 4B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

Η εντολή `lemonade run Qwen3.5-4B-GGUF` κατεβάζει επίσης το μοντέλο κατά την πρώτη χρήση αν δεν υπάρχει ήδη, και στη συνέχεια το φορτώνει για εξαγωγή συμπερασμάτων (inference).

Το μοντέλο εμφανίζεται στη λίστα των μοντέλων που έχουν ληφθεί στον διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
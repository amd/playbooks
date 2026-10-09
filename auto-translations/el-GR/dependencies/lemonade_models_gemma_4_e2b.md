<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Gemma-4 E2B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

Η εντολή `lemonade run Gemma-4-E2B-it-GGUF` κατεβάζει επίσης το μοντέλο κατά την πρώτη χρήση, εάν δεν υπάρχει ήδη, και στη συνέχεια το φορτώνει για συμπερασμό (inference).

Το μοντέλο εμφανίζεται στη λίστα των μοντέλων που έχουν ληφθεί στον διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη. Οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του SDXL-Turbo για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο SDXL-Turbo (`SDXL-Turbo`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull SDXL-Turbo
```

Η εντολή `lemonade run SDXL-Turbo` κατεβάζει επίσης το μοντέλο κατά την πρώτη χρήση, εφόσον δεν υπάρχει ήδη, και στη συνέχεια το φορτώνει για συμπερασμό (inference).

Το μοντέλο εμφανίζεται στη λίστα κατεβασμένων μοντέλων του διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->
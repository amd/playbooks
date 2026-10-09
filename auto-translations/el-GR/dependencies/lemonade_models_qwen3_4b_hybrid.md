<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του Qwen3 4B Hybrid για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), το οποίο εκτελείται στο NPU και στο GPU των επεξεργαστών Ryzen AI. Για να το κατεβάσετε εκ των προτέρων:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Το μοντέλο εμφανίζεται στη λίστα μοντέλων που έχουν ληφθεί στον διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· ο παρακάτω έλεγχος επιβεβαιώνει ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->
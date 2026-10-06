<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του GPT-OSS 20B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

Η εντολή `lemonade run gpt-oss-20b-mxfp4-GGUF` κατεβάζει επίσης το μοντέλο κατά την πρώτη χρήση, εάν δεν είναι ήδη διαθέσιμο, και στη συνέχεια το φορτώνει για εξαγωγή συμπερασμάτων (inference).

Το μοντέλο εμφανίζεται στη λίστα κατεβασμένων μοντέλων του διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι διαθέσιμο στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
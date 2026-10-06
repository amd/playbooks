<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του GPT-OSS 120B για το Lemonade

Ο διακομιστής Lemonade εξυπηρετεί το μοντέλο GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Για να το κατεβάσετε εκ των προτέρων:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Η εντολή `lemonade run gpt-oss-120b-mxfp-GGUF` κατεβάζει επίσης το μοντέλο κατά την πρώτη χρήση αν δεν υπάρχει ήδη, και στη συνέχεια το φορτώνει για εξαγωγή συμπερασμάτων (inference).

Το μοντέλο εμφανίζεται στη λίστα κατεβασμένων μοντέλων του διακομιστή Lemonade μόλις ολοκληρωθεί η λήψη· οι παρακάτω έλεγχοι επιβεβαιώνουν ότι είναι παρόν στο μηχάνημα.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
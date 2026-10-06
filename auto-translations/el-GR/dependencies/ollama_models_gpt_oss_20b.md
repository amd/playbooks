<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Λήψη του GPT-OSS 20B για το Ollama

Κάντε pull το μοντέλο GPT-OSS 20B στο Ollama:

```bash
ollama pull gpt-oss:20b
```

Ο διακομιστής Ollama πρέπει να εκτελείται για να ολοκληρωθεί επιτυχώς το pull· η εντολή `ollama serve` τον εκκινεί εάν δεν εκτελείται ήδη.

Επιβεβαιώστε ότι το μοντέλο υπάρχει:

```bash
ollama list
```

Θα πρέπει να δείτε το `gpt-oss:20b` στο αποτέλεσμα, μαζί με το μέγεθός του και την ημερομηνία τελευταίας τροποποίησης.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Διαμόρφωση Πλατφόρμας

Αυτό το έγγραφο περιγράφει τις αναμενόμενες διαμορφώσεις πλατφόρμας για την εκτέλεση αυτού του playbook.

## Προαπαιτούμενα

### Windows

| Στοιχείο | Έκδοση | Σημειώσεις |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Προεγκατεστημένο και διαθέσιμο στο PATH στην AMD Ryzen™ AI Halo Developer Platform· πρέπει να εγκατασταθεί χειροκίνητα σε όλες τις άλλες συσκευές |
| **Lemonade Server** | latest | Εκτελείται στο `http://localhost:13305/api/v1` |

### Linux

| Στοιχείο | Έκδοση | Σημειώσεις |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Προεγκατεστημένο και διαθέσιμο στο PATH στην AMD Ryzen™ AI Halo Developer Platform· πρέπει να εγκατασταθεί χειροκίνητα σε όλες τις άλλες συσκευές |
| **Lemonade Server** | latest | Εκτελείται στο `http://localhost:13305/api/v1` |


## Lemonade LLM

Ο διακομιστής Lemonade θα πρέπει να εκτελείται με το κατάλληλο μοντέλο για τη συσκευή φορτωμένο (δείτε το README για την εντολή `lemonade run` για τη συσκευή σας):

| Συσκευή | Endpoint | Μοντέλο |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |
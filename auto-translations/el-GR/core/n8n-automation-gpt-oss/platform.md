<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

# Διαμόρφωση Πλατφόρμας

Αυτό το έγγραφο περιγράφει τις αναμενόμενες διαμορφώσεις πλατφόρμας για την εκτέλεση αυτού του playbook.

## Προαπαιτούμενα

### Windows

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Προεγκατεστημένο και διαθέσιμο στο PATH στην πλατφόρμα AMD Ryzen™ AI Halo Developer Platform· πρέπει να εγκατασταθεί χειροκίνητα σε όλες τις άλλες συσκευές |
| **Lemonade Server** | latest | Εκτελείται στο `http://localhost:13305/api/v1` |

### Linux

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Προεγκατεστημένο και διαθέσιμο στο PATH στην πλατφόρμα AMD Ryzen™ AI Halo Developer Platform· πρέπει να εγκατασταθεί χειροκίνητα σε όλες τις άλλες συσκευές |
| **Lemonade Server** | latest | Εκτελείται στο `http://localhost:13305/api/v1` |


## Lemonade LLM

Ο Lemonade server θα πρέπει να εκτελείται με το κατάλληλο για τη συσκευή μοντέλο φορτωμένο (ανατρέξτε στο README για την εντολή `lemonade run` για τη συσκευή σας):

| Device | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |
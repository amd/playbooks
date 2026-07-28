<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v1 -->
> [!WARNING]
> **Αυτόματη μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει επανεξεταστεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένα βήματα, εντολές, λήψεις ή η διαθεσιμότητα προϊόντων μπορεί να διαφέρουν στη γλώσσα ή την περιοχή σας. Εάν κάτι φαίνεται λανθασμένο, θεωρήστε το πρωτότυπο αγγλικό playbook ως την πηγή αλήθειας.
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
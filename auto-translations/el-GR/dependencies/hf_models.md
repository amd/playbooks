<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Μοντέλα και σύνολα δεδομένων Hugging Face

Το playbook κατεβάζει τα μοντέλα και τα σύνολα δεδομένων του Hugging Face την πρώτη φορά που τα χρησιμοποιεί και τα διατηρεί στην προσωρινή μνήμη (cache) του Hugging Face (`~/.cache/huggingface/hub` εκτός αν το `HF_HOME` ή το `HF_HUB_CACHE` υποδεικνύουν διαφορετική τοποθεσία), ώστε οι επόμενες εκτελέσεις να ξεκινούν χωρίς να τα κατεβάζουν ξανά.
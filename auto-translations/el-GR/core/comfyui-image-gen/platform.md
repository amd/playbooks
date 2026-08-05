<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

# Ρύθμιση παραμέτρων πλατφόρμας

Αυτό το έγγραφο περιγράφει τις αναμενόμενες ρυθμίσεις παραμέτρων πλατφόρμας για την εκτέλεση αυτού του playbook.

## Απαιτούμενες εφαρμογές/πλαίσια
### Windows/Linux

Το ComfyUI θα πρέπει να είναι προεγκατεστημένο χρησιμοποιώντας τις οδηγίες που παρέχονται στον [Οδηγό εγκατάστασης ComfyUI](../../dependencies/comfyui.md).

## Απαιτούμενα μοντέλα

### Windows/Linux

Τα ακόλουθα μοντέλα πρέπει να υπάρχουν στον κατάλογο όπου είναι εγκατεστημένο το ComfyUI, μέσα στον φάκελο `models`.

| Τύπος μοντέλου | Όνομα αρχείου | Μέγεθος | Τοποθεσία | Λήψη |
|------------|----------|------|----------|----------|
| Text Encoder | `qwen_3_4b.safetensors` | 7.49 GB | `models/text_encoders/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162.25 MB | `models/loras/` | [Σύνδεσμος](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Diffusion Model | `z_image_turbo_bf16.safetensors` | 11.46 GB | `models/diffusion_models/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319.77 MB | `models/vae/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Για να ελέγξετε αν τα μοντέλα έχουν τοποθετηθεί σωστά, [κάντε προεπισκόπηση του playbook ComfyUI χρησιμοποιώντας τον ιστότοπο εισαγωγής χρηστών](../../README.md#previewing-the-playbooks) και ακολουθήστε τις οδηγίες. Τα μοντέλα έχουν τοποθετηθεί σωστά αν δεν εμφανιστεί η σελίδα "Models not found" κατά την εκκίνηση του προτύπου Z-Image Turbo.
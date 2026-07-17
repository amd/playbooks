<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Διαμόρφωση Πλατφόρμας

Αυτό το έγγραφο περιγράφει τις αναμενόμενες διαμορφώσεις πλατφόρμας για την εκτέλεση αυτού του playbook.

## Απαιτούμενες Εφαρμογές/Frameworks
### Windows/Linux

Το ComfyUI θα πρέπει να είναι προεγκατεστημένο χρησιμοποιώντας τις οδηγίες που παρέχονται στον [Οδηγό Εγκατάστασης ComfyUI](../../dependencies/comfyui.md).

## Απαιτούμενα Μοντέλα

### Windows/Linux

Τα παρακάτω μοντέλα πρέπει να βρίσκονται στον κατάλογο όπου είναι εγκατεστημένο το ComfyUI, μέσα στον φάκελο `models`.

| Τύπος Μοντέλου | Όνομα Αρχείου | Μέγεθος | Τοποθεσία | Λήψη |
|------------|----------|------|----------|----------|
| Κωδικοποιητής Κειμένου | `qwen_3_4b.safetensors` | 7,49 GB | `models/text_encoders/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors) |
| LoRA | `pixel_art_style_z_image_turbo.safetensors` | 162,25 MB | `models/loras/` | [Σύνδεσμος](https://huggingface.co/tarn59/pixel_art_style_lora_z_image_turbo/resolve/main/pixel_art_style_z_image_turbo.safetensors) |
| Μοντέλο Διάχυσης | `z_image_turbo_bf16.safetensors` | 11,46 GB | `models/diffusion_models/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors) |
| VAE | `ae.safetensors` | 319,77 MB | `models/vae/` | [Σύνδεσμος](https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors) |


Για να ελέγξετε αν τα μοντέλα έχουν τοποθετηθεί σωστά, [κάντε προεπισκόπηση του playbook ComfyUI μέσω της ιστοσελίδας εισαγωγής](../../README.md#previewing-the-playbooks) και ακολουθήστε τις οδηγίες. Τα μοντέλα έχουν τοποθετηθεί σωστά εάν δεν εμφανιστεί καμία σελίδα "Τα μοντέλα δεν βρέθηκαν" κατά την εκκίνηση του προτύπου Z-Image Turbo.
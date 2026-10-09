<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Modele și seturi de date Hugging Face

Playbook-ul descarcă modelele și seturile de date Hugging Face la prima utilizare și le păstrează în cache-ul Hugging Face (`~/.cache/huggingface/hub`, cu excepția cazului în care `HF_HOME` sau `HF_HUB_CACHE` indică spre altă locație), astfel încât rulările ulterioare să înceapă fără a le descărca din nou.
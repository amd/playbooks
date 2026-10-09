<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face -mallit ja -datasetit

Ohjekirja lataa Hugging Face -mallinsa ja -datasettinsa ensimmäisellä käyttökerralla ja säilyttää ne Hugging Face -välimuistissa (`~/.cache/huggingface/hub`, ellei `HF_HOME` tai `HF_HUB_CACHE` osoita muualle), joten myöhemmät ajot käynnistyvät lataamatta niitä uudelleen.
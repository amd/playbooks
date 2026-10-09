<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hugging Face-Modelle und -Datensätze

Das Playbook lädt seine Hugging Face-Modelle und -Datensätze beim ersten Gebrauch herunter und speichert sie im Hugging Face-Cache (`~/.cache/huggingface/hub`, sofern nicht `HF_HOME` oder `HF_HUB_CACHE` auf einen anderen Ort verweist), sodass spätere Ausführungen starten können, ohne sie erneut herunterzuladen.
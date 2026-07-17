# Configurarea Platformei

Acest document descrie configurațiile de platformă așteptate pentru rularea acestui playbook.

## Cerințe preliminare

PyTorch cu suport ROCm este preinstalat pe AMD Ryzen™ AI Halo Developer Platform. Pentru toate celelalte dispozitive, utilizatorii trebuie să instaleze manual PyTorch cu suport ROCm. Consultați secțiunea relevantă pentru sistemul dvs. de operare:


### Windows

| Componentă    | Versiune        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | Preinstalat pe AMD Ryzen AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |


### Linux

| Componentă    | Versiune        | Note                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | Preinstalat pe AMD Ryzen AI Halo Developer Platform; trebuie instalat manual pe toate celelalte dispozitive |


## Modele necesare

Următoarele modele sunt testate și optimizate pentru platforma dvs.:

| Model | Parametri | Dimensiune | Locație descărcare |
|-------|-----------|------------|--------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | Descărcați de pe HF

Modelele vor fi descărcate automat în directorul cache Hugging Face: `~/.cache/huggingface/hub/`

Asigurați-vă că aveți cel puțin **20 GB spațiu liber** pentru stocarea modelelor.

## Cerințe de rețea

Configurarea inițială necesită acces la internet pentru a descărca modele de pe Hugging Face. După descărcare, playbook-ul poate rula offline.

- Primele descărcări de modele pot dura **5-10 minute** în funcție de dimensiunea modelului și viteza conexiunii
- Modelele sunt stocate local în cache și nu trebuie descărcate din nou
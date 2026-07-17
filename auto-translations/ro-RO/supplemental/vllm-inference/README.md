<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Acest playbook folosește etichete speciale pe care GitHub nu le poate reda. Vă rugăm să vizitați [amd.com/playbooks](https://amd.com/playbooks) pentru a previzualiza corect acest conținut.
<!-- @github-only:end -->


## Prezentare generală

vLLM este un motor de inferență de înaltă performanță conceput pentru modele de limbaj de mari dimensiuni (LLM-uri). Oferă servire optimizată cu procesare continuă în loturi pentru un randament ridicat și un API compatibil cu OpenAI pentru integrarea fără probleme a aplicațiilor. Acest lucru face ca vLLM să fie excelent pentru implementările în producție unde viteza și eficiența resurselor sunt critice.

Acest playbook vă învață cum să serviți LLM-uri folosind vLLM containerizat pe GPU-ul integrat și să interacționați cu modelele prin intermediul API-ului Python OpenAI.

## Ce veți învăța

- Cum să configurați și să porniți un server vLLM cu suport AMD ROCm™
- Cum să interacționați cu modelele prin intermediul endpoint-urilor API compatibile cu OpenAI
- Cum să trimiteți prompturi către serverul local cu `vllm-prompt`

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificarea actualizărilor de software

> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor preliminare de software

Acest playbook folosește o imagine de container preconstruită care include vLLM, suport ROCm și scripturile auxiliare necesare pentru a lansa serverul. Nu este nevoie să instalați manual PyTorch, vLLM sau scripturile locale ale playbook-ului.

Nu există niciun pas de instalare vLLM pe partea gazdă. Porniți vLLM cu:

```bash
vllm-launch
```

Lansatorul pornește containerul, vizează GPU-ul integrat și expune un server vLLM local compatibil cu OpenAI. Alternativ, faceți clic pe pictograma vLLM din bara de activități.

## Pornire rapidă

### 1. Confirmați că serverul vLLM rulează

`vllm-launch` poate dura câteva minute pentru a inițializa totul. Odată pornit, serverul este disponibil la `http://localhost:8001`. Mențineți terminalul de lansare deschis deoarece serverul rulează în prim-plan, apoi deschideți un terminal separat pentru pașii rămași. Exemplele de mai jos folosesc `Qwen/Qwen3-1.7B`; dacă lansatorul dvs. este configurat pentru un model diferit, substituiți acel ID de model în cereri.

### 2. Trimiteți un prompt

Folosiți scriptul `vllm-prompt` furnizat pentru a trimite o cerere către serverul local vLLM compatibil cu OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Conversați cu modelul folosind API-ul Python OpenAI

Deoarece vLLM expune un API compatibil cu OpenAI, puteți folosi pachetul Python `openai` pentru a interacționa cu acesta.

Mai întâi, creați un mediu virtual Python:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Instalați pachetul OpenAI
```bash
pip install openai
```

Creați un client `OpenAI` îndreptat către serverul vLLM local în loc de serverele OpenAI. `api_key` este necesar de client, dar vLLM nu îl validează, deci orice șir de caractere funcționează:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Apoi, trimiteți o cerere de completare a conversației. Aceasta folosește același format de mesaje ca API-ul OpenAI — o listă de mesaje cu roluri precum `"user"` și `"assistant"`. Setarea `stream=True` înseamnă că răspunsul va sosi incremental, nu dintr-o dată:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

În final, iterați peste fragmentele transmise în flux și afișați fiecare bucată de text pe măsură ce sosește:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Scriptul [chat_with_model.py](assets/chat_with_model.py) inclus conține întregul exemplu și poate fi descărcat.


## Depanare

### Conexiune refuzată

Asigurați-vă că serverul rulează:
```bash
curl http://localhost:8001/health
```

## Rezumat

În acest playbook, ați învățat cum să:

- Porniți vLLM containerizat cu suport ROCm pe GPU-ul integrat
- Porniți un server vLLM cu endpoint-uri API compatibile cu OpenAI pe portul 8001
- Trimiteți prompturi cu `vllm-prompt`
- Efectuați apeluri API către serverul vLLM folosind atât cereri cu flux, cât și fără flux
- Depanați problemele comune legate de pornirea serverului, memorie și conexiunile clientului

Acum aveți o implementare vLLM containerizată pentru servirea modelelor de limbaj de mari dimensiuni cu performanță optimizată pe GPU-ul integrat.

## Pași următori

- **Încercați modele diferite** — Schimbați modelul din configurația `vllm-launch` pentru a experimenta cu diferite LLM-uri și a compara performanța.
- **Construiți o aplicație** — Folosiți API-ul compatibil cu OpenAI pentru a integra vLLM într-o aplicație Python, un chatbot sau un flux de lucru de automatizare.
- **Ajustați fin și serviți** — Ajustați fin un model folosind LoRA sau QLoRA, apoi implementați-l cu vLLM pentru inferență optimizată.

## Resurse suplimentare

- **[Documentația oficială vLLM](https://docs.vllm.ai/)** — Ghiduri complete și referințe API
- **[Depozitul vLLM GitHub](https://github.com/vllm-project/vllm)** — Cod sursă, probleme și discuții ale comunității
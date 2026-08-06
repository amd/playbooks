<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducere automată.** Această pagină a fost tradusă automat din limba engleză și nu a fost revizuită de o persoană. Aceasta poate conține erori, iar anumite instrucțiuni, comenzi, descărcări, disponibilitatea produselor sau alt conținut pot varia în funcție de limbă sau regiune. În cazul oricărei neconcordanțe sau discrepanțe, versiunea originală în limba engleză a playbook-ului prevalează.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->


## Prezentare generală

vLLM este un motor de inferență de înaltă performanță conceput pentru modele de limbaj de mari dimensiuni (LLM-uri). Acesta oferă servire optimizată cu batching continuu pentru un randament ridicat și un API compatibil cu OpenAI pentru integrarea fără probleme cu aplicațiile. Acest lucru face ca vLLM să fie excelent pentru implementările de producție unde viteza și eficiența resurselor sunt esențiale.

Acest playbook vă învață cum să serviți LLM-uri utilizând vLLM containerizat pe GPU-ul integrat și cum să interacționați cu modelele prin intermediul API-ului Python OpenAI.

## Ce veți învăța

- Cum să configurați și să porniți un server vLLM cu suport AMD ROCm™
- Cum să interacționați cu modelele prin intermediul endpoint-urilor API compatibile cu OpenAI
- Cum să trimiteți prompturi către serverul local cu `vllm-prompt`

## Configurarea memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați actualizările software-ului

> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea cerințelor prealabile software

vLLM rulează într-un container preconstruit cu ROCm și dependențele sale pre-potrivite. Nu este necesară nicio instalare suplimentară.

Nu există niciun pas de instalare vLLM pe partea de gazdă. Porniți vLLM cu:

```bash
vllm-launch
```

Programul de lansare pornește containerul, vizează GPU-ul integrat și expune un server vLLM local compatibil cu OpenAI. Alternativ, faceți clic pe pictograma vLLM din bara de sarcini.

## Ghid rapid de pornire

### 1. Confirmați că serverul vLLM rulează

`vllm-launch` poate dura câteva minute pentru a inițializa totul. Odată pornit, serverul este disponibil la `http://localhost:8001`. Păstrați terminalul de lansare deschis deoarece serverul rulează în prim-plan, apoi deschideți un terminal separat pentru pașii rămași. Exemplele de mai jos utilizează `Qwen/Qwen3-1.7B`; dacă programul de lansare este configurat pentru un model diferit, înlocuiți acel ID de model în cereri.

### 2. Trimiteți un prompt

Utilizați scriptul furnizat `vllm-prompt` pentru a trimite o cerere către serverul local vLLM compatibil cu OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Discutați cu modelul utilizând API-ul Python OpenAI

Deoarece vLLM expune un API compatibil cu OpenAI, puteți utiliza pachetul Python `openai` pentru a interacționa cu acesta.

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

Creați un client `OpenAI` care indică către serverul local vLLM în locul serverelor OpenAI. `api_key` este necesar de către client, dar vLLM nu îl validează, așa că orice șir de caractere funcționează:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Apoi, trimiteți o cerere de finalizare a conversației. Aceasta utilizează același format de mesaje ca API-ul OpenAI — o listă de mesaje cu roluri precum `"user"` și `"assistant"`. Setarea `stream=True` înseamnă că răspunsul va sosi incremental, nu tot dintr-o dată:

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

În final, iterați prin fragmentele transmise în flux și afișați fiecare bucată de text pe măsură ce sosește:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Scriptul inclus [chat_with_model.py](assets/chat_with_model.py) conține exemplul complet și poate fi descărcat.


## Alegerea și configurarea unui model

În mod implicit, `vllm-launch` servește `Qwen/Qwen3-1.7B` ca model de test pe portul `8001`. Puteți schimba modelul, portul și parametrii de servire vLLM fără a reconstrui sau edita containerul.

### Modele testate de AMD

Următoarele modele sunt preconfigurate și validate de AMD:

| Model | Note |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Model implicit. Ușor și rapid de încărcat. |
| `openai/gpt-oss-20b` | Model mai mare pentru răspunsuri de calitate superioară. |

### Lansarea unui model diferit

Transmiteți ID-ul modelului cu `--model` (sau `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Schimbarea portului

Transmiteți un port peste 1024 cu `--port` (sau `-p`); valoarea implicită este `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Dacă schimbați portul, direcționați `base_url` al clientului dumneavoastră către același port (de exemplu, `http://localhost:8080/v1`).

### Transmiterea de parametri vLLM suplimentari

Orice argumente suplimentare sunt redirecționate direct către vLLM, astfel încât puteți ajusta comportamentul de servire, cum ar fi lungimea contextului sau tipul de date. Există două moduri de a le furniza.

**Inline**, după opțiunile programului de lansare:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Persistent**, într-un fișier de configurare la `~/.local/share/vLLM/vllm-launch.conf`. Acest fișier nu există implicit — creați-l și adăugați argumentele dumneavoastră ca un array Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Utilizați `+=` pentru a adăuga la argumentele implicite în loc să le înlocuiți:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Pentru a vedea toate opțiunile programului de lansare în orice moment, rulați:

```bash
vllm-launch --help
```

### Unde sunt stocate modelele

`vllm-launch` caută modele în două locații:

| Locație | Cale |
|----------|------|
| Modele de sistem | `/var/cache/models` |
| Modele de utilizator | `~/.local/share/vLLM/models` |

Puteți plasa un model descărcat în oricare dintre directoare și îl puteți lansa transmițând calea sau ID-ul acestuia către `--model`:

```bash
vllm-launch --model /var/cache/models/my-model
```

> **Notă**: Rularea propriului model descărcat în acest mod este de așteptat să funcționeze odată ce modelul este plasat în unul dintre directoarele de mai sus, dar acest flux de lucru nu a fost încă validat oficial de AMD.

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
- Efectuați apeluri API către serverul vLLM utilizând atât cereri cu flux continuu, cât și fără flux continuu
- Depanați probleme comune legate de pornirea serverului, memorie și conexiunile clientului

Acum aveți o implementare vLLM containerizată pentru servirea modelelor de limbaj de mari dimensiuni cu performanță optimizată pe GPU-ul integrat.

## Pașii următori

- **Încercați modele diferite** — Utilizați `vllm-launch --model <model>` pentru a experimenta cu diferite LLM-uri și a compara performanța (consultați [Alegerea și configurarea unui model](#choosing-and-configuring-a-model)).
- **Construiți o aplicație** — Utilizați API-ul compatibil cu OpenAI pentru a integra vLLM într-o aplicație Python, un chatbot sau un flux de lucru automatizat.
- **Ajustați fin și serviți** — Ajustați fin un model utilizând LoRA sau QLoRA, apoi implementați-l cu vLLM pentru inferență optimizată.
## Resurse suplimentare

- **[Documentația oficială vLLM](https://docs.vllm.ai/)** — Ghiduri complete și referințe API
- **[Repozitoriul GitHub vLLM](https://github.com/vllm-project/vllm)** — Cod sursă, probleme și discuții din comunitate
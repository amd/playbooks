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

vLLM este un motor de inferență de înaltă performanță conceput pentru modele de limbaj de mari dimensiuni (LLM-uri). Oferă servire optimizată cu batching continuu pentru un debit ridicat și un API compatibil cu OpenAI pentru integrarea perfectă a aplicațiilor. Acest lucru face ca vLLM să fie excelent pentru implementările de producție în care viteza și eficiența resurselor sunt esențiale.

Acest ghid vă învață cum să serviți LLM-uri folosind vLLM containerizat pe GPU-ul integrat și cum să interacționați cu modelele prin API-ul Python OpenAI.

## Ce veți învăța

- Cum să configurați și să porniți un server vLLM cu suport AMD ROCm™
- Cum să interacționați cu modelele prin punctele finale API compatibile cu OpenAI
- Cum să trimiteți prompturi către serverul local cu `vllm-prompt`

## Configurarea Memoriei

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificați Actualizările Software

> **Notă**: Dacă VS Code nu este instalat, îl puteți instala cu AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalarea Cerințelor Software Preliminare

vLLM rulează într-un container prealcătuit cu ROCm și dependențele sale pre-potrivite. Nu este necesară nicio instalare suplimentară.

Nu există niciun pas de instalare vLLM pe gazdă. Porniți vLLM cu:

```bash
vllm-launch
```

Lansatorul pornește containerul, vizează GPU-ul integrat și expune un server vLLM local compatibil cu OpenAI. Alternativ, faceți clic pe pictograma vLLM din bara de activități.

## Start Rapid

### 1. Confirmați Că Serverul vLLM Rulează

`vllm-launch` poate dura câteva minute pentru a inițializa totul. Odată ce pornește, serverul este disponibil la `http://localhost:8001`. Păstrați terminalul de lansare deschis deoarece serverul rulează în prim-plan, apoi deschideți un terminal separat pentru pașii rămași. Exemplele de mai jos folosesc `Qwen/Qwen3-1.7B`; dacă lansatorul dumneavoastră este configurat pentru un model diferit, înlocuiți acel ID de model în cereri.

### 2. Trimiteți un Prompt

Folosiți scriptul furnizat `vllm-prompt` pentru a trimite o cerere către serverul local vLLM compatibil cu OpenAI:

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
<!-- @os:end -->

Instalați pachetul OpenAI
```bash
pip install openai
```

Creați un client `OpenAI` îndreptat către serverul local vLLM în locul serverelor OpenAI. `api_key` este necesar de către client, dar vLLM nu îl validează, deci orice șir de caractere funcționează:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Apoi, trimiteți o cerere de completare a conversației. Aceasta folosește același format de mesaj ca API-ul OpenAI — o listă de mesaje cu roluri precum `"user"` și `"assistant"`. Setarea `stream=True` înseamnă că răspunsul va sosi incremental, nu dintr-o dată:

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

În final, parcurgeți fragmentele transmise în flux și afișați fiecare bucată de text pe măsură ce sosește:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Scriptul inclus [chat_with_model.py](assets/chat_with_model.py) conține întregul exemplu și poate fi descărcat.


## Alegerea și Configurarea unui Model

În mod implicit, `vllm-launch` servește `Qwen/Qwen3-1.7B` ca model de test pe portul `8001`. Puteți schimba modelul, portul și parametrii de servire vLLM fără a reconstrui sau edita containerul.

### Modele testate de AMD

Următoarele modele sunt pre-configurate și validate de AMD:

| Model | Note |
|-------|-------|
| `Qwen/Qwen3-1.7B` | Model implicit. Ușor și rapid de încărcat. |
| `openai/gpt-oss-20b` | Model mai mare pentru răspunsuri de calitate superioară. |

### Lansarea unui model diferit

Treceți ID-ul modelului cu `--model` (sau `-m`):

```bash
vllm-launch --model openai/gpt-oss-20b
```

### Schimbarea portului

Treceți un port peste 1024 cu `--port` (sau `-p`); valoarea implicită este `8001`:

```bash
vllm-launch --port 8080 --model openai/gpt-oss-20b
```

Dacă schimbați portul, îndreptați `base_url` al clientului dumneavoastră către același port (de exemplu `http://localhost:8080/v1`).

### Transmiterea parametrilor suplimentari vLLM

Orice argumente suplimentare sunt transmise direct către vLLM, astfel încât puteți ajusta comportamentul de servire, cum ar fi lungimea contextului sau tipul de date. Există două modalități de a le furniza.

**În linie**, după opțiunile lansatorului:

```bash
vllm-launch --model openai/gpt-oss-20b --max-model-len 8192
```

**Persistent**, într-un fișier de configurare la `~/.local/share/vLLM/vllm-launch.conf`. Acest fișier nu există în mod implicit — creați-l și adăugați argumentele dumneavoastră ca un array Bash:

```bash
VLLM_EXTRA_ARGS=(--max-model-len 8192 --dtype float16)
```

Folosiți `+=` pentru a adăuga la argumentele implicite în loc să le înlocuiți:

```bash
VLLM_EXTRA_ARGS+=(--max-model-len 8192)
```

Pentru a vedea toate opțiunile lansatorului în orice moment, rulați:

```bash
vllm-launch --help
```

### Unde sunt stocate modelele

`vllm-launch` caută modele în două locații:

| Locație | Cale |
|----------|------|
| Modele de sistem | `/var/cache/models` |
| Modele utilizator | `~/.local/share/vLLM/models` |

Puteți plasa un model descărcat în oricare dintre directoare și îl puteți lansa trecând calea sau ID-ul acestuia la `--model`:

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

În acest ghid, ați învățat cum să:

- Porniți vLLM containerizat cu suport ROCm pe GPU-ul integrat
- Porniți un server vLLM cu puncte finale API compatibile cu OpenAI pe portul 8001
- Trimiteți prompturi cu `vllm-prompt`
- Efectuați apeluri API către serverul vLLM folosind atât cereri în flux, cât și cereri fără flux
- Depanați probleme comune legate de pornirea serverului, memorie și conexiunile clientului

Acum aveți o implementare vLLM containerizată pentru servirea modelelor de limbaj de mari dimensiuni cu performanță optimizată pe GPU-ul integrat.

## Pașii Următori

- **Încercați diferite modele** — Folosiți `vllm-launch --model <model>` pentru a experimenta cu diferite LLM-uri și a compara performanța (vezi [Alegerea și Configurarea unui Model](#choosing-and-configuring-a-model)).
- **Construiți o aplicație** — Folosiți API-ul compatibil cu OpenAI pentru a integra vLLM într-o aplicație Python, un chatbot sau un flux de lucru automatizat.
- **Ajustați fin și serviți** — Ajustați fin un model folosind LoRA sau QLoRA, apoi implementați-l cu vLLM pentru inferență optimizată.
## Resurse suplimentare

- **[Documentația oficială vLLM](https://docs.vllm.ai/)** — Ghiduri complete și referințe API
- **[Repozitoriul GitHub vLLM](https://github.com/vllm-project/vllm)** — Cod sursă, probleme și discuții ale comunității
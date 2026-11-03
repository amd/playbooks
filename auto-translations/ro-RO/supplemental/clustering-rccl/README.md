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

# Clustering pentru două sisteme Ryzen™ AI Halo cu RCCL

## Prezentare generală

Sistemul dumneavoastră Ryzen™ AI Halo este deja capabil să ruleze modele de limbaj de mari dimensiuni (LLM) local. Clustering-ul duce acest lucru mai departe, combinând memoria GPU a mai multor sisteme printr-o rețea locală, oferindu-vă acces la modele și mai mari, cu raționament mai puternic, generare de cod îmbunătățită și o înțelegere multilingvistică mai profundă, totul în întregime pe propriul dumneavoastră hardware.

Acest ghid vă învață cum să faceți clustering pentru două sisteme Ryzen AI Halo folosind RCCL (ROCm Communication Collectives Library) împreună cu vLLM și cum să rulați Qwen3.5-397B, un model cu 397 miliarde de parametri, pe ambele mașini, cu accelerare ROCm.

## Ce veți învăța

- Cum să extindeți alocarea VRAM pe sistemele Ryzen AI Halo
- Lansarea vLLM cu suport ROCm
- Configurarea RCCL pentru inferență tensor-parallel pe mai multe noduri, între două sisteme Ryzen AI Halo
- Rularea unui model cu 397 miliarde de parametri pe două sisteme Ryzen AI Halo conectate în rețea

## Cerințe preliminare

### Hardware

Acest ghid necesită două unități Ryzen AI Halo și un switch Ethernet, conectate într-o topologie stea, fiecare unitate fiind conectată direct la switch.

| Componentă | Cantitate | Descriere |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Noduri de calcul care formează clusterul |
| Switch Ethernet de 10Gbps | 1 | Switch central care permite comunicarea între mai multe noduri Ryzen AI Halo (cel puțin 2 porturi) |
| Cablu Ethernet | 2 | Conectează fiecare unitate Halo la switch (se recomandă Cat 7 sau superior) |

> **Notă**: Sunt necesare două porturi de switch Ethernet pentru a conecta cele două unități Ryzen AI Halo. Este necesar un al treilea port dacă accesați modelul de pe o mașină client separată, în loc de pe una dintre unitățile Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurarea hardware-ului fizic

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

Conectați fiecare unitate Ryzen AI Halo la switch-ul Ethernet folosind un cablu Cat 7 (sau superior). Aceasta stabilește legătura de 10Gbps folosită pentru comunicarea de mare viteză dintre noduri.

### 1. Determinarea interfețelor de rețea

Pe fiecare mașină, aflați numele interfeței sale de rețea și notați-l (va fi menționat în restul instrucțiunilor ca `IFNAME`). Rulați:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Aceasta afișează direct numele interfeței, de exemplu:

```bash
enp191s0
```

### 2. Verificarea vitezelor legăturii de rețea

Confirmați că legătura este activă și rulează la viteză maximă verificând viteza interfeței dumneavoastră:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Notă**: Înlocuiți `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea interfețelor de rețea](#1-determine-network-interfaces)

Ar trebui să vedeți o viteză de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Notă**: Dacă viteza este mai mică de `10000Mb/s` sau legătura nu se activează, verificați conexiunea cablului și confirmați că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea negocierii automate și setarea manuală a vitezei legăturii; consultați documentația switch-ului dumneavoastră.

## Extinderea alocării VRAM

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

### Configurarea memoriei pentru rularea modelelor mari

Pe Linux, ROCm utilizează un pool de memorie de sistem partajată, iar acest pool este configurat implicit la jumătate din memoria sistemului.

Această cantitate poate fi mărită modificând setarea paginii Translation Table Manager (TTM) a kernel-ului, urmând instrucțiunile de mai jos. AMD recomandă setarea VRAM dedicată minimă în BIOS (0,5 GB).

* Instalați utilitarul pipx și adăugați calea pentru wheel-urile instalate cu pipx în calea de căutare a sistemului.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalați wheel-ul amd-debug-tools din PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Rulați instrumentul amd-ttm pentru a interoga setările actuale ale memoriei partajate.
  ```bash
  amd-ttm
  ```

* Reconfigurați setările memoriei partajate la **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reporniți sistemul pentru ca modificările să intre în vigoare.

## Inițializarea containerului vLLM

> **Notă**: Finalizați acest pas atât pe Mașina 1, cât și pe Mașina 2.

Sistemul dumneavoastră Ryzen AI Halo vine cu vLLM inclus într-o imagine de container prealcătuită, pe care o rulați folosind Podman, un instrument de containerizare gratuit și open source.

### 1. Crearea directorului de descărcare a modelului

Când serviți modelul Qwen3.5-397B în acest ghid, vLLM va descărca automat ponderile modelului pe sistemul dumneavoastră. Pentru a vă asigura că aceste ponderi sunt accesibile din interiorul containerului, creați mai întâi un director de modele pe care containerul îl poate monta:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lansarea containerului vLLM

Comanda de mai jos lansează containerul și vă plasează într-un shell interactiv. Aceasta montează directorul de modele pe care tocmai l-ați creat și transmite `IFNAME`-ul dumneavoastră către `NCCL_SOCKET_IFNAME` și `GLOO_SOCKET_IFNAME`, indicând RCCL (biblioteca folosită de vLLM pentru a coordona GPU-urile pe tot clusterul) ce interfață să utilizeze.

Porniți containerul cu:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Notă**: Înlocuiți `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea interfețelor de rețea](#1-determine-network-interfaces)

## Rularea modelului pe cluster

vLLM folosește Ray pentru a orchestra clusterul și RCCL pentru a gestiona comunicarea GPU-la-GPU între noduri. O mașină acționează ca **nod principal** (Mașina 1), coordonând inferența. Cealaltă se alătură ca **nod de lucru** (Mașina 2), contribuind cu memoria sa GPU și puterea de calcul.

> **Notă**: Ray este o dependență opțională pentru vLLM și este disponibilă doar din interiorul containerului Podman preconfigurat. 

La lansare, vLLM fragmentează modelul pe ambele noduri folosind paralelismul tensorial. Odată încărcat, inferența continuă ca și cum ar rula pe un singur accelerator.

#### Prevenirea erorilor OOM ale Ray

Implicit, Ray monitorizează memoria gazdei pe fiecare nod și oprește cel mai mare proces atunci când utilizarea memoriei depășește 95%. Pe sistemul dumneavoastră Ryzen™ AI Halo, GPU-ul și gazda partajează un singur pool de memorie, astfel încât încărcarea unui model poate declanșa o eroare `ray.exceptions.OutOfMemoryError` și poate opri procesul de lucru.

Pentru a preveni acest lucru, vom exporta `RAY_memory_monitor_refresh_ms=0` pe fiecare mașină înainte de a porni și alătura clusterul.
### Pasul 1: Porniți nodul principal Ray (Mașina 1)

Pe Mașina 1, porniți nodul principal Ray pentru a inițializa clusterul:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Găsirea `<MACHINE_1_IP>`**: Pe Mașina 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.

### Pasul 2: Alăturați-vă clusterului (Mașina 2)

Pe Mașina 2, conectați-vă la nodul principal pentru a forma clusterul:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Găsirea `<MACHINE_2_IP>`**: Pe Mașina 2, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.

### Pasul 3: Serviți modelul (Mașina 1)

Pe Mașina 1, lansați serverul vLLM. Acesta va descărca automat modelul și va începe să-l servească pe ambele noduri:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Referință parametri

| Flag | Scop |
|------|------|
| `--port` | Portul pe care este servit API-ul HTTP |
| `--host` | Adresa IP la care este legat serverul (`0.0.0.0` pentru toate interfețele) |
| `--max-model-len` | Lungimea maximă a contextului în tokeni |
| `--gpu-memory-utilization` | Fracțiunea de memorie GPU care va fi alocată (0.0–1.0) |
| `--dtype` | Tipul de date pentru ponderile modelului |
| `--tensor-parallel-size` | Numărul de GPU-uri pe care este fragmentat modelul (setați la numărul total de GPU-uri din cluster) |
| `--distributed-executor-backend` | Backend-ul pentru execuția multi-nod (`ray` pentru implementări în cluster) |
| `--enforce-eager` | Dezactivează compilarea graficelor CUDA pentru compatibilitate |
| `--language-model-only` | Omite încărcarea componentelor auxiliare ale modelului (de ex., encoder-ul de viziune) |
| `--reasoning-parser` | Activează analiza structurată a rezultatelor de raționament pentru model |

Pentru utilizarea completă a parametrilor, consultați [documentația vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accesarea modelului

vLLM expune un API compatibil cu OpenAI, astfel încât puteți conecta orice client sau interfață compatibilă la clusterul dvs. O opțiune populară este [Open WebUI](https://github.com/open-webui/open-webui), care oferă o interfață de chat bazată pe browser.

Pentru a conecta Open WebUI la endpoint-ul dvs. vLLM:

1. Deschideți **Settings** > **Admin Panel** > **Connections**
2. Faceți clic pe **+** de la **Manage OpenAI API Connections**
3. Setați **Connection Type** la **External**
4. Setați **URL** la `http://<MACHINE_1_IP>:7000/v1`
5. Sub **Auth**, selectați **None** din meniul derulant
6. Lăsați **Model IDs** gol pentru a descoperi automat toate modelele de la endpoint

> **Găsirea `<MACHINE_1_IP>`**: Pe Mașina 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală. Dacă accesați Open WebUI chiar de pe Mașina 1, puteți folosi `http://localhost:7000/v1`.

![Setările de conexiune Open WebUI pentru endpoint-ul vLLM](assets/openwebui-connection.png)

Odată conectat, selectați modelul din meniul derulant de modele din Open WebUI și începeți să conversați. Modelul rulează acum pe ambele noduri Ryzen AI Halo:

![Conversație cu Qwen3.5-397B în Open WebUI](assets/openwebui-chat.png)

## Pași următori

- **Explorați alte modele**: Descoperiți modele noi pe [Hugging Face](https://huggingface.co/models?&sort=trending) care se încadrează în memoria GPU combinată a clusterului dvs.
- **Extindeți la patru noduri**: Adăugați încă două sisteme Ryzen AI Halo ca lucrători Ray suplimentari pentru a fragmenta modelele pe și mai multe GPU-uri. Acest lucru necesită un switch Ethernet cu cel puțin patru porturi, câte unul pentru fiecare nod. Urmați [Pasul 2: Alăturați-vă clusterului](#step-2-join-the-cluster-machine-2) pe fiecare lucrător suplimentar și creșteți `--tensor-parallel-size` în consecință
- **Încercați alte strategii de paralelism**: vLLM suportă [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pentru modelele mixture-of-experts și [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pentru un randament mai mare. Experimentați cu `--enable-expert-parallel` și `--data-parallel-size` pentru a găsi cea mai bună configurație pentru sarcina dvs. de lucru
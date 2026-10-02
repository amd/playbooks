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

# Clusterizarea a patru sisteme Ryzen™ AI Halo cu RCCL

## Prezentare generală

Sistemul tău Ryzen™ AI Halo este deja capabil să ruleze modele de limbaj mari la nivel local. Clusterizarea duce acest lucru mai departe, combinând memoria GPU a mai multor sisteme printr-o rețea locală, oferindu-ți acces la modele și mai mari, cu raționament mai puternic, generare de cod mai bună și o înțelegere multilingvă mai profundă, totul în întregime pe propriul tău hardware.

Acest playbook te învață cum să clusterizezi patru sisteme Ryzen AI Halo folosind RCCL (ROCm Communication Collectives Library) împreună cu vLLM și cum să rulezi Qwen3.5-397B, un model cu 397 de miliarde de parametri, pe toate cele patru mașini, cu accelerare ROCm.

## Ce vei învăța

- Cum să extinzi alocarea VRAM pe sistemele Ryzen AI Halo
- Lansarea vLLM cu suport ROCm
- Configurarea RCCL pentru inferență paralelă tensorială multi-nod pe patru sisteme Ryzen AI Halo
- Rularea unui model cu 397 de miliarde de parametri pe patru sisteme Ryzen AI Halo conectate în rețea

## Cerințe preliminare

### Hardware

Acest playbook necesită patru unități Ryzen AI Halo și un switch Ethernet, conectate într-o topologie stea, fiecare unitate fiind cablată direct la switch.

| Componentă | Cantitate | Descriere |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Noduri de calcul care formează clusterul |
| Switch Ethernet 10Gbps | 1 | Switch central care permite comunicarea multi-nod a sistemelor Ryzen AI Halo (minimum 4 porturi) |
| Cablu Ethernet | 4 | Conectează fiecare unitate Halo la switch (se recomandă Cat 7 sau superior) |

> **Notă**: Sunt necesare patru porturi de switch Ethernet pentru a conecta cele patru unități Ryzen AI Halo. Este necesar un al cincilea port dacă accesezi modelul de pe o mașină client separată, în loc de pe una dintre unitățile Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configurarea hardware fizic

> **Notă**: Finalizează acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

Conectează fiecare unitate Ryzen AI Halo la switch-ul Ethernet folosind un cablu Cat 7 (sau superior). Acest lucru stabilește legătura de 10Gbps folosită pentru comunicarea de mare viteză dintre noduri.

### 1. Determinarea interfețelor de rețea

Pe fiecare mașină, află numele interfeței sale de rețea și notează-l (va fi menționat în restul instrucțiunilor ca `IFNAME`). Rulează:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Acest lucru afișează direct numele interfeței, de exemplu:

```bash
enp191s0
```

### 2. Verificarea vitezelor legăturilor de rețea

Confirmă că legătura este activă și rulează la viteză maximă verificând viteza interfeței tale:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Notă**: Înlocuiește `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea interfețelor de rețea](#1-determine-network-interfaces)

Ar trebui să vezi o viteză de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Notă**: Dacă viteza este mai mică de `10000Mb/s` sau legătura nu se activează, verifică conexiunea cablului și confirmă că portul switch-ului este setat la 10Gbps. Unele switch-uri necesită dezactivarea auto-negocierii și setarea manuală a vitezei legăturii; consultă documentația switch-ului tău.

## Extinderea alocării VRAM

> **Notă**: Finalizează acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

### Configurarea memoriei pentru rularea modelelor mari

Pe Linux, ROCm utilizează un pool de memorie partajată a sistemului, iar acest pool este configurat implicit la jumătate din memoria sistemului.

Această cantitate poate fi mărită prin modificarea setării de pagini Translation Table Manager (TTM) a kernelului, folosind instrucțiunile de mai jos. AMD recomandă setarea VRAM-ului dedicat minim din BIOS (0,5 GB).

* Instalează utilitarul pipx și adaugă calea pentru pachetele (wheels) instalate de pipx în calea de căutare a sistemului.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instalează pachetul amd-debug-tools din PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Rulează instrumentul amd-ttm pentru a interoga setările curente pentru memoria partajată.
  ```bash
  amd-ttm
  ```

* Reconfigurează setările memoriei partajate la **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Repornește sistemul pentru ca modificările să intre în vigoare.

## Inițializarea containerului vLLM

> **Notă**: Finalizează acest pas pe toate cele patru mașini (Mașina 1 până la Mașina 4).

Sistemul tău Ryzen AI Halo vine cu vLLM preambalat într-o imagine de container precompilată, pe care o rulezi folosind Podman, un instrument de containere gratuit și open source.

### 1. Crearea directorului de descărcare a modelului

Când rulezi modelul Qwen3.5-397B în acest playbook, vLLM va descărca automat ponderile modelului pe sistemul tău. Pentru a te asigura că aceste ponderi sunt accesibile din interiorul containerului, creează mai întâi un director models pe care containerul îl poate monta:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lansarea containerului vLLM

Comanda de mai jos lansează containerul și te plasează într-un shell interactiv. Aceasta montează directorul models pe care tocmai l-ai creat și transmite `IFNAME`-ul tău către `NCCL_SOCKET_IFNAME` și `GLOO_SOCKET_IFNAME`, indicând RCCL (biblioteca pe care vLLM o folosește pentru a coordona GPU-urile în tot clusterul) ce interfață să folosească.

Pornește containerul cu:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Notă**: Înlocuiește `<IFNAME>` cu numele interfeței de ieșire din [1. Determinarea interfețelor de rețea](#1-determine-network-interfaces)

## Rularea modelului pe cluster

vLLM folosește Ray pentru a orchestra clusterul și RCCL pentru a gestiona comunicarea GPU-la-GPU între noduri. O mașină acționează ca nod principal (Mașina 1), coordonând inferența. Celelalte trei se alătură ca noduri lucrătoare (Mașinile 2, 3 și 4), contribuind cu memoria GPU și puterea lor de calcul.

> **Notă**: Ray este o dependență opțională pentru vLLM și este disponibilă doar din interiorul containerului Podman preconfigurat.

La lansare, vLLM împarte modelul pe toate cele patru noduri folosind paralelism tensorial. Odată încărcat, inferența se desfășoară ca și cum ar rula pe un singur accelerator.

#### Prevenirea erorilor Ray OOM

În mod implicit, Ray monitorizează memoria gazdă pe fiecare nod și oprește cel mai mare proces atunci când utilizarea memoriei depășește 95%. Pe sistemul tău Ryzen™ AI Halo, GPU-ul și gazda împart un singur pool de memorie, astfel încât încărcarea unui model poate declanșa o eroare `ray.exceptions.OutOfMemoryError` și poate opri procesul lucrător.

Pentru a preveni acest lucru, vom exporta `RAY_memory_monitor_refresh_ms=0` pe fiecare mașină înainte de a porni și alătura clusterul.
### Pasul 1: Porniți nodul principal Ray (Machine 1)

Pe Machine 1, porniți nodul principal Ray pentru a inițializa clusterul:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Găsirea `<MACHINE_1_IP>`**: Pe Machine 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.

### Pasul 2: Alăturați-vă clusterului (Machines 2, 3 și 4)

Pe fiecare dintre Machines 2, 3 și 4, conectați-vă la nodul principal pentru a forma clusterul:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Găsirea `<MACHINE_N_IP>`**: Pe fiecare mașină worker, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală.

### Pasul 3: Serviți modelul (Machine 1)

Pe Machine 1, lansați serverul vLLM. Acesta va descărca automat modelul și va începe să-l servească pe toate cele patru noduri:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### Referință parametri

| Flag | Scop |
|------|------|
| `--port` | Portul pe care este servit API-ul HTTP |
| `--host` | Adresa IP la care este asociat serverul (`0.0.0.0` pentru toate interfețele) |
| `--max-model-len` | Lungimea maximă a contextului în tokeni |
| `--gpu-memory-utilization` | Fracțiunea de memorie GPU alocată (0.0–1.0) |
| `--dtype` | Tipul de date pentru ponderile modelului |
| `--tensor-parallel-size` | Numărul de GPU-uri pe care este fragmentat modelul (se setează la numărul total de GPU-uri din cluster) |
| `--distributed-executor-backend` | Backend-ul pentru execuția multi-nod (`ray` pentru implementări de cluster) |
| `--enforce-eager` | Dezactivează compilarea graficelor CUDA pentru compatibilitate |
| `--language-model-only` | Omite încărcarea componentelor auxiliare ale modelului (de ex. encoderul vizual) |
| `--reasoning-parser` | Activează analiza structurată a rezultatelor de raționament pentru model |

Pentru utilizarea completă a parametrilor, consultați [documentația vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Accesarea modelului

vLLM expune un API compatibil cu OpenAI, astfel încât puteți conecta orice client sau interfață compatibilă la clusterul dumneavoastră. O opțiune populară este [Open WebUI](https://github.com/open-webui/open-webui), care oferă o interfață de chat bazată pe browser.

Pentru a conecta Open WebUI la endpoint-ul dumneavoastră vLLM:

1. Deschideți **Settings** > **Admin Panel** > **Connections**
2. Faceți clic pe **+** din **Manage OpenAI API Connections**
3. Setați **Connection Type** la **External**
4. Setați **URL** la `http://<MACHINE_1_IP>:7000/v1`
5. Sub **Auth**, selectați **None** din meniul derulant
6. Lăsați **Model IDs** gol pentru a descoperi automat toate modelele de la endpoint

> **Găsirea `<MACHINE_1_IP>`**: Pe Machine 1, rulați `hostname -I | awk '{print $1}'` pentru a găsi adresa sa IP locală. Dacă accesați Open WebUI chiar de pe Machine 1, puteți utiliza `http://localhost:7000/v1`.

![Setările de conexiune Open WebUI pentru endpoint-ul vLLM](assets/openwebui-connection.png)

Odată conectat, selectați modelul din meniul derulant de modele din Open WebUI și începeți conversația. Modelul rulează acum pe toate cele patru noduri Ryzen AI Halo:

![Conversație cu Qwen3.5-397B în Open WebUI](assets/openwebui-chat.png)

## Pașii următori

- **Explorați alte modele**: Descoperiți modele noi pe [Hugging Face](https://huggingface.co/models?&sort=trending) care se încadrează în memoria GPU combinată a clusterului dumneavoastră
- **Extindeți dincolo de patru noduri**: Adăugați sisteme suplimentare Ryzen AI Halo ca workeri Ray suplimentari pentru a fragmenta modelele pe și mai multe GPU-uri. Urmați [Pasul 2: Alăturați-vă clusterului](#step-2-join-the-cluster-machines-2-3-and-4) pe fiecare worker suplimentar și creșteți corespunzător `--tensor-parallel-size`
- **Încercați alte strategii de paralelism**: vLLM suportă [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) pentru modele de tip mixture-of-experts și [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) pentru un randament mai mare. Experimentați cu `--enable-expert-parallel` și `--data-parallel-size` pentru a găsi cea mai bună configurație pentru sarcina dumneavoastră de lucru
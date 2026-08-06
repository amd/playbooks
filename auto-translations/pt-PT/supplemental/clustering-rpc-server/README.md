<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Agrupar em Cluster Dois Ryzen™ AI Halo com RPC

## Visão Geral

O seu Ryzen™ AI Halo já é capaz de executar modelos de linguagem de grandes dimensões localmente. Agrupar em cluster leva isto ainda mais longe, combinando a memória GPU de vários sistemas através de uma rede local, dando-lhe acesso a modelos ainda maiores com um raciocínio mais forte, melhor geração de código e uma compreensão multilingue mais profunda, tudo inteiramente no seu próprio hardware.

Este manual ensina-o a agrupar em cluster dois sistemas Ryzen AI Halo utilizando o motor RPC do llama.cpp e a executar o GLM 4.7, um modelo com 358 mil milhões de parâmetros, em ambas as máquinas com aceleração AMD ROCm™.

## O que Vai Aprender

- Como estender a atribuição de VRAM em sistemas Ryzen AI Halo
- Instalar o llama.cpp com suporte para ROCm e RPC
- Configurar um worker RPC e iniciar inferência distribuída entre dois nós
- Executar um modelo com 358 mil milhões de parâmetros em dois sistemas Ryzen AI Halo ligados em rede

## Definir a Configuração de Memória

> **Nota**: Conclua este passo tanto na Máquina 1 como na Máquina 2.

<!-- @os:windows -->
No Windows, para executar modelos maiores que requerem mais memória, é necessário utilizar a atribuição AMD Variable Graphics Memory (VRAM do iGPU).

Isto pode ser feito abrindo o painel de controlo AMD Software: Adrenalin Edition e navegando até: `Performance > Tuning > AMD Variable Graphics Memory`. Defina o valor para **96 GB**. Reinicie o sistema para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
No Linux, o ROCm utiliza um conjunto de memória de sistema partilhado, e este conjunto está configurado por predefinição para metade da memória do sistema.

Esta quantidade pode ser aumentada alterando a definição de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB).

* Instale o utilitário pipx e adicione o caminho para as wheels instaladas pelo pipx ao caminho de pesquisa do sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instale a wheel amd-debug-tools a partir do PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Execute a ferramenta amd-ttm para consultar as definições atuais de memória partilhada.
  ```bash
  amd-ttm
  ```

* Reconfigure as definições de memória partilhada para **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reinicie o sistema para que as alterações tenham efeito.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->
## Pré-requisitos

### Hardware

Este manual requer duas unidades Ryzen AI Halo e um switch Ethernet, ligados numa topologia em estrela, com cada unidade ligada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nós de computação que formam o cluster |
| Switch Ethernet 10Gbps | 1 | Switch central para permitir a comunicação multi-nó entre unidades Ryzen AI Halo (pelo menos 2 portas) |
| Cabo Ethernet | 2 | Liga cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Nota**: São necessárias duas portas do switch Ethernet para ligar as duas unidades Ryzen AI Halo. É necessária uma terceira porta se aceder ao modelo a partir de uma máquina cliente separada, em vez de a partir de uma das unidades Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Instale:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe) com a carga de trabalho **Desktop Development with C++**
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## Configuração Física do Hardware

> **Nota**: Conclua este passo tanto na Máquina 1 como na Máquina 2.

Ligue cada unidade Ryzen AI Halo ao switch Ethernet utilizando um cabo Cat 7 (ou superior). Isto estabelece a ligação de 10Gbps utilizada para comunicação de alta velocidade entre os nós.
<!-- @os:linux -->
### 1. Determinar Interfaces de Rede

Em cada máquina, determine o nome da respetiva interface de rede e anote-o (será referido abaixo como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isto mostra o nome da interface diretamente, por exemplo:

```bash
enp191s0
```

### 2. Verificar as Velocidades de Ligação de Rede

Confirme que a ligação está ativa e a funcionar à velocidade máxima verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Substitua `<IFNAME>` pelo nome da interface de saída de [1. Determinar Interfaces de Rede](#1-determine-network-interfaces)

Deverá ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se a velocidade for inferior a `10000Mb/s` ou a ligação não ficar ativa, verifique a ligação do cabo e confirme se a porta do switch está definida para 10Gbps. Alguns switches requerem que a negociação automática seja desativada e a velocidade da ligação definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verificar a Velocidade da Ligação de Rede

Em cada máquina, verifique a velocidade de ligação das suas interfaces de rede:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

A sua interface Ethernet deverá estar `Up` e a funcionar a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Nota**: Se a velocidade for inferior a `10 Gbps` ou a ligação não ficar ativa, verifique a ligação do cabo e confirme se a porta do switch está definida para 10Gbps. Alguns switches requerem que a negociação automática seja desativada e a velocidade da ligação definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

## Instalar o llama.cpp

> **Nota**: Conclua este passo tanto na Máquina 1 como na Máquina 2.

Estão disponíveis duas opções de instalação:

- [Opção 1: Lemonade SDK (Recomendado)](#option-1-lemonade-sdk-recommended) - binários pré-compilados, configuração mais rápida
- [Opção 2: Compilação Manual a Partir do Código-Fonte](#option-2-manual-source-build) - compile a partir do código-fonte com controlo total sobre as flags de compilação

### Opção 1: Lemonade SDK (Recomendado)

O Lemonade SDK disponibiliza builds noturnas do llama.cpp com aceleração AMD ROCm 7, destinadas a GPUs como a gfx1151 (Strix Halo / Ryzen AI Max+ 395) e outras arquiteturas Radeon mais recentes.

<!-- @os:windows -->
#### Passo 1: Transferir os Binários Pré-Criados

Navegue até à página do lançamento mais recente e transfira o arquivo correspondente à sua plataforma e alvo de GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Transfira o ficheiro com o nome `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (onde `xxxx` é o número da compilação).

#### Passo 2: Extrair os Binários

Descompacte o arquivo transferido:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Este diretório contém agora compilações com suporte a ROCm do `llama-cli.exe`, `llama-server.exe` e `rpc-server.exe`, pré-compiladas para o seu sistema Ryzen AI Halo.

#### Passo 3: Verificar a Deteção da GPU

```bash
.\llama-cli.exe --list-devices
```

Resultado esperado:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Passo 1: Transferir os Binários Pré-Criados

Navegue até à página do lançamento mais recente e transfira o arquivo correspondente à sua plataforma e alvo de GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Transfira o ficheiro com o nome `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (onde `xxxx` é o número da compilação).

#### Passo 2: Extrair e Preparar os Binários

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Este diretório contém agora compilações com suporte a ROCm do `llama-cli`, `llama-server` e `rpc-server`, pré-compiladas para o seu sistema Ryzen AI Halo.

#### Passo 3: Verificar a Deteção da GPU

```bash
./llama-cli --list-devices
```

Resultado esperado:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Com o llama.cpp preparado em cada nó, prossiga para [Transferir o Modelo](#downloading-the-model).

### Opção 2: Compilação Manual a Partir do Código-Fonte

<!-- @os:windows -->
#### Passo 1: Compilar o llama.cpp

Abra o **x64 Native Tools Command Prompt** (instalado com o Visual Studio Build Tools) e clone o repositório:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adicione o HIP ao seu caminho e compile com suporte a ROCm e RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flag de Compilação | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Ativa a pilha de software ROCm/HIP |
| `-DGGML_RPC=ON` | Ativa o RPC para inferência distribuída |
| `-DGPU_TARGETS=gfx1151` | Tem como alvo a GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Utiliza o sistema de compilação Ninja |

#### Passo 2: Verificar a Deteção da GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Resultado esperado:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Passo 3: Adicionar o HIP ao Seu Caminho de Utilizador

O passo de compilação acima definiu `%HIP_PATH%\bin` apenas para a sessão atual. Para disponibilizar as bibliotecas HIP em qualquer terminal (não apenas no x64 Native Tools Command Prompt), adicione-o permanentemente ao seu `PATH` de utilizador:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Com o llama.cpp preparado em cada nó, prossiga para [Transferir o Modelo](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Passo 1: Compilar o llama.cpp

Clone o repositório:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Compile com suporte a ROCm e RPC:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| Flag de Compilação | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Ativa a pilha de software ROCm |
| `-DGGML_RPC=ON` | Ativa o RPC para inferência distribuída |
| `-DAMDGPU_TARGETS="gfx1151"` | Tem como alvo a GPU Ryzen AI Halo (Radeon 8060s) |

Para mais opções de compilação, consulte a [documentação de compilação do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Passo 2: Verificar a Deteção da GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Resultado esperado:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Com o llama.cpp preparado em cada nó, prossiga para [Transferir o Modelo](#downloading-the-model).
<!-- @os:end -->

## Transferir o Modelo

Este guia utiliza o [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), um modelo com 358 mil milhões de parâmetros na quantização `Q4_K_XL` da [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Nesta quantização, o modelo requer aproximadamente 205 GB de armazenamento e cabe na memória combinada das GPU de dois nós Ryzen AI Halo.

Transfira os ficheiros GGUF utilizando o CLI do Hugging Face:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **Nota**: A transferência do modelo deve ser concluída na Máquina 1 (o controlador). Os nós de trabalho RPC não precisam de uma cópia local dos ficheiros do modelo.

## Iniciar o Modelo no Cluster

O motor RPC (Remote Procedure Call) do llama.cpp permite que uma única instância do llama.cpp transfira camadas do modelo para nós de trabalho remotos através da rede. Uma máquina atua como **controlador** (Máquina 1), tratando da tokenização, agendamento e orquestração. A outra máquina executa um **servidor RPC** leve (Máquina 2) que expõe a sua memória e capacidade de computação da GPU ao controlador.

No momento do carregamento, o llama.cpp divide o modelo entre ambos os nós. Após o carregamento, a inferência decorre como se estivesse a ser executada num único acelerador. O RPC trata as transferências de tensores e a sincronização nos bastidores.

### Passo 1: Iniciar o Servidor RPC (Máquina 2)

Na Máquina 2, inicie o servidor RPC para expor os seus recursos de GPU ao controlador:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| Flag | Finalidade |
|------|---------|
| `-p` | Porta na qual difundir o servidor RPC |
| `-c` | Ativa uma cache local para tensores de grande dimensão, evitando transferências de rede repetidas durante o carregamento do modelo |
| `--host` | Endereço IP ao qual associar o servidor RPC (`0.0.0.0` para todas as interfaces) |

Para mais opções, consulte a [documentação de RPC do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Passo 2: Iniciar o Modelo (Máquina 1)

Com o servidor RPC em execução na Máquina 2, inicie a inferência a partir da Máquina 1 utilizando `llama-cli` ou `llama-server`.

#### llama-cli

O `llama-cli` fornece uma interface baseada em terminal para interagir diretamente com o modelo. É ideal para benchmarking, depuração e experimentação de baixo nível.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrar `<RPC_WORKER_IP>`**: Na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Execute este comando no Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrar `<RPC_WORKER_IP>`**: Na Máquina 2, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar o seu endereço IP local.

<!-- @os:end -->

Após a execução, o `llama-cli` apresenta o progresso do carregamento do modelo e entra num pedido interativo onde pode conversar diretamente com o modelo:

![llama-cli a executar o GLM 4.7 em dois nós](assets/llama-cli-example.png)
#### llama-server

O `llama-server` expõe o mesmo motor de inferência através de um processo de servidor persistente com uma interface web integrada e uma API HTTP compatível com OpenAI. Esta é a interface preferida para implementações de longa duração, acesso multiutilizador e integração com ferramentas externas.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrar `<RPC_WORKER_IP>`**: Na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Nota**: Execute este comando no Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrar `<RPC_WORKER_IP>`**: Na Máquina 2, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar o seu endereço IP local.
<!-- @os:end -->

Depois de iniciado, abra `http://<HOST_IP>:8081` no seu navegador para aceder à interface web integrada. Esta disponibiliza uma interface de chat baseada em navegador para interagir com o modelo:

![Interface web do llama-server a executar GLM 4.7 em dois nós](assets/llama-server-example.png)

<!-- @os:linux -->
> **Encontrar `<HOST_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Encontrar `<HOST_IP>`**: Na Máquina 1, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar o seu endereço IP local.
<!-- @os:end -->

#### Referência de Parâmetros

| Flag | Finalidade |
|------|---------|
| `-m` | Caminho para o ficheiro de modelo GGUF (utilize o primeiro fragmento, `00001-of-00005`) |
| `-c` | Tamanho do contexto em tokens. Valores maiores utilizam mais memória |
| `-fa on` | Ativa o rocWMMA Flash Attention para melhor desempenho em GPUs AMD |
| `-ngl 999` | Transfere todas as camadas do modelo para a GPU |
| `--no-mmap` | Desativa o mapeamento de memória, reduzindo os tempos de carregamento quando o tamanho do modelo excede a RAM do sistema mas cabe na VRAM |
| `--host` | IP ao qual associar o `llama-server` (apenas `llama-server`) |
| `--port` | Porta na qual disponibilizar a API HTTP (apenas `llama-server`) |
| `--rpc` | Lista separada por vírgulas de endpoints de workers RPC (`IP:port`) |

Para a utilização completa dos parâmetros, consulte a [documentação do llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e a [documentação do llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Próximos Passos

- **Ligar aplicações de terceiros**: O `llama-server` expõe uma API compatível com OpenAI. Aponte qualquer aplicação compatível com OpenAI (como o Open WebUI) para `http://<HOST_IP>:8081` com qualquer chave de API de substituição (por exemplo, `none`) para se ligar ao seu cluster
- **Explorar outros modelos**: Navegue pelos GGUFs quantizados no [Hugging Face](https://huggingface.co/models?search=gguf) para encontrar modelos que cabem dentro da memória GPU combinada do seu cluster
- **Escalar para quatro nós**: Adicione mais dois sistemas Ryzen AI Halo como workers RPC adicionais para aceder a modelos à escala de 1 bilião de parâmetros. Passe endpoints adicionais para `--rpc` como uma lista separada por vírgulas (por exemplo, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
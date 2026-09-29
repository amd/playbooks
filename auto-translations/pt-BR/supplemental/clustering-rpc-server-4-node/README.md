<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Clusterizando Quatro Ryzen™ AI Halos com RPC

## Visão Geral

Seu Ryzen™ AI Halo já é capaz de executar modelos de linguagem grandes localmente. A clusterização leva isso um passo além, combinando a memória de GPU de vários sistemas em uma rede local, dando a você acesso a modelos ainda maiores, com raciocínio mais forte, melhor geração de código e compreensão multilíngue mais profunda, tudo inteiramente em seu próprio hardware.

Este guia ensina como clusterizar quatro sistemas Ryzen AI Halo usando o mecanismo RPC do llama.cpp e executar o Kimi K2.6, um grande modelo de mistura de especialistas (mixture-of-experts), nas quatro máquinas com aceleração AMD ROCm™.

## O Que Você Vai Aprender

- Como estender a alocação de VRAM em sistemas Ryzen AI Halo
- Instalação do llama.cpp com suporte a ROCm e RPC
- Configuração de workers RPC e inicialização de inferência distribuída em quatro nós
- Execução de um modelo com 1T de parâmetros em quatro sistemas Ryzen AI Halo conectados em rede

## Configurando a Memória

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

<!-- @os:windows -->
No Windows, para executar modelos maiores que exigem mais memória, precisamos usar a alocação AMD Variable Graphics Memory (VRAM da iGPU).

Isso pode ser feito abrindo o painel de controle AMD Software: Adrenalin Edition e navegando até: `Performance > Tuning > AMD Variable Graphics Memory`. Defina o valor para **96 GB**. Por favor, reinicie o sistema para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
No Linux, o ROCm utiliza um pool de memória de sistema compartilhado, e esse pool é configurado por padrão para metade da memória do sistema.

Essa quantidade pode ser aumentada alterando a configuração de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir o mínimo de VRAM dedicada na BIOS (0,5 GB).

* Instale o utilitário pipx e adicione o caminho para os wheels instalados pelo pipx ao caminho de busca do sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instale o wheel amd-debug-tools a partir do PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Execute a ferramenta amd-ttm para consultar as configurações atuais de memória compartilhada.
  ```bash
  amd-ttm
  ```

* Reconfigure as configurações de memória compartilhada para **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reinicie o sistema para que as alterações tenham efeito.


<!-- @os:end -->
<!-- @device:halo_box -->
## Verifique Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->
## Pré-requisitos

### Hardware

Este guia requer quatro unidades Ryzen AI Halo e um switch Ethernet, conectados em uma topologia estrela, com cada unidade conectada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nós de computação que formam o cluster |
| Switch Ethernet 10Gbps | 1 | Switch central para permitir a comunicação multi-nó entre os Ryzen AI Halo (pelo menos 4 portas) |
| Cabo Ethernet | 4 | Conecta cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Observação**: São necessárias quatro portas do switch Ethernet para conectar as quatro unidades Ryzen AI Halo. Uma quinta porta é necessária caso você acesse o modelo a partir de uma máquina cliente separada, em vez de a partir de uma das unidades Halo.

### Software
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
Por favor, instale:
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

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

Conecte cada unidade Ryzen AI Halo ao switch Ethernet usando um cabo Cat 7 (ou superior). Isso estabelece o link de 10Gbps usado para comunicação de alta velocidade entre os nós.
<!-- @os:linux -->
### 1. Determine as Interfaces de Rede

Em cada máquina, encontre o nome de sua interface de rede e anote-o (ele será referenciado abaixo como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isso imprime o nome da interface diretamente, por exemplo:

```bash
enp191s0
```

### 2. Verifique as Velocidades de Link de Rede

Confirme que o link está ativo e funcionando na velocidade máxima verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Observação**: Substitua `<IFNAME>` pelo nome da interface de saída de [1. Determine as Interfaces de Rede](#1-determine-network-interfaces)

Você deve ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Observação**: Se a velocidade for menor que `10000Mb/s` ou o link não subir, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10Gbps. Alguns switches exigem que a negociação automática seja desativada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifique a Velocidade do Link de Rede

Em cada máquina, verifique a velocidade de link de suas interfaces de rede:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Sua interface Ethernet deve estar `Up` e funcionando a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Observação**: Se a velocidade for menor que `10 Gbps` ou o link não subir, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10Gbps. Alguns switches exigem que a negociação automática seja desativada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

## Instalando o llama.cpp

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

Duas opções de instalação estão disponíveis:

- [Opção 1: Lemonade SDK (Recomendado)](#option-1-lemonade-sdk-recommended) - binários pré-compilados, configuração mais rápida
- [Opção 2: Compilação Manual a partir do Código-fonte](#option-2-manual-source-build) - compile a partir do código-fonte com controle total sobre as flags de compilação

### Opção 1: Lemonade SDK (Recomendado)

O Lemonade SDK fornece builds noturnos do llama.cpp com aceleração AMD ROCm 7, direcionados a GPUs como a gfx1151 (Strix Halo / Ryzen AI Max+ 395) e outras arquiteturas Radeon recentes.

<!-- @os:windows -->
#### Step 1: Baixe os binários pré-compilados

Navegue até a página do release mais recente e baixe o arquivo compatível com sua plataforma e destino de GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Baixe o arquivo chamado `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (em que `xxxx` é o número do build).

#### Step 2: Extraia os binários

Descompacte o arquivo baixado:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Este diretório agora contém builds habilitados para ROCm de `llama-cli.exe`, `llama-server.exe` e `ggml-rpc-server.exe`, pré-compilados para o seu sistema Ryzen AI Halo.

#### Step 3: Verifique a detecção da GPU

```bash
.\llama-cli.exe --list-devices
```

Saída esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Baixe os binários pré-compilados

Navegue até a página do release mais recente e baixe o arquivo compatível com sua plataforma e destino de GPU:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Baixe o arquivo chamado `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (em que `xxxx` é o número do build).

#### Step 2: Extraia e prepare os binários

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Este diretório agora contém builds habilitados para ROCm de `llama-cli`, `llama-server` e `rpc-server`, pré-compilados para o seu sistema Ryzen AI Halo.

#### Step 3: Verifique a detecção da GPU

```bash
./llama-cli --list-devices
```

Saída esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
Com o llama.cpp preparado em cada nó, prossiga para [Baixando o Modelo](#downloading-the-model).

### Opção 2: Build manual a partir do código-fonte

<!-- @os:windows -->
#### Step 1: Compile o llama.cpp

Abra o **x64 Native Tools Command Prompt** (instalado com o Visual Studio Build Tools) e clone o repositório:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

Adicione o HIP ao seu path e compile com suporte a ROCm e RPC:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| Flag de Build | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita a stack de software ROCm/HIP |
| `-DGGML_RPC=ON` | Habilita o RPC para inferência distribuída |
| `-DGPU_TARGETS=gfx1151` | Define como destino a GPU do Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Usa o sistema de build Ninja |

#### Step 2: Verifique a detecção da GPU

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

Saída esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### Step 3: Adicione o HIP ao seu path de usuário

A etapa de build acima definiu `%HIP_PATH%\bin` apenas para a sessão atual. Para tornar as bibliotecas HIP disponíveis em qualquer terminal (não apenas no x64 Native Tools Command Prompt), adicione-o permanentemente ao seu `PATH` de usuário:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Com o llama.cpp preparado em cada nó, prossiga para [Baixando o Modelo](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Compile o llama.cpp

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

| Flag de Build | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita a stack de software ROCm |
| `-DGGML_RPC=ON` | Habilita o RPC para inferência distribuída |
| `-DAMDGPU_TARGETS="gfx1151"` | Define como destino a GPU do Ryzen AI Halo (Radeon 8060s) |

Para mais opções de build, consulte a [documentação de build do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Verifique a detecção da GPU

```bash
cd rocm/bin
./llama-cli --list-devices
```

Saída esperada:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

Com o llama.cpp preparado em cada nó, prossiga para [Baixando o Modelo](#downloading-the-model).
<!-- @os:end -->

## Baixando o Modelo

Este playbook usa o [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6) na quantização `UD-Q2_K_XL` da [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL). Esta quantização cabe dentro da memória combinada de GPU de quatro nós Ryzen AI Halo.

Baixe os arquivos GGUF usando o Hugging Face CLI:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **Nota**: O download do modelo deve ser concluído na Máquina 1 (o controlador). Os nós de trabalho RPC (Máquinas 2, 3 e 4) não precisam ter uma cópia local dos arquivos do modelo.

## Iniciando o modelo no cluster

O mecanismo RPC (Remote Procedure Call) do llama.cpp permite que uma única instância do llama.cpp transfira camadas do modelo para workers remotos pela rede. Uma máquina atua como **controladora** (Máquina 1), cuidando da tokenização, do agendamento e da orquestração. As outras três máquinas executam cada uma um **servidor RPC** leve (Máquinas 2, 3 e 4) que expõe sua memória e capacidade de processamento de GPU para a controladora.

No momento do carregamento, o llama.cpp fragmenta o modelo entre os quatro nós. Uma vez carregado, a inferência prossegue como se estivesse sendo executada em um único acelerador. O RPC cuida das transferências de tensores e da sincronização nos bastidores.

### Step 1: Inicie os servidores RPC (Máquinas 2, 3 e 4)

Em cada uma das Máquinas 2, 3 e 4, inicie o servidor RPC para expor seus recursos de GPU à controladora:
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
| `-p` | Porta na qual o servidor RPC será transmitido |
| `-c` | Habilita um cache local para tensores grandes, evitando transferências de rede repetidas durante o carregamento do modelo |
| `--host` | Endereço IP ao qual o servidor RPC será vinculado (`0.0.0.0` para todas as interfaces) |

Para mais opções, consulte a [documentação de RPC do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Inicie o modelo (Máquina 1)

Com os servidores RPC em execução nas Máquinas 2, 3 e 4, inicie a inferência a partir da Máquina 1 usando `llama-cli` ou `llama-server`.
#### llama-cli

`llama-cli` fornece uma interface baseada em terminal para interagir diretamente com o modelo. É ideal para benchmarking, depuração e experimentação de baixo nível.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Encontrando `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Em cada uma das Máquinas 2, 3 e 4, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: Execute este comando no Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Encontrando `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Em cada uma das Máquinas 2, 3 e 4, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.

<!-- @os:end -->

Uma vez em execução, `llama-cli` exibe o progresso de carregamento do modelo e entra em um prompt interativo onde você pode conversar diretamente com o modelo:

![llama-cli executando Kimi K2.6 em quatro nós](assets/llama-cli-example.png)

#### llama-server

`llama-server` expõe o mesmo mecanismo de inferência através de um processo de servidor persistente com uma interface web integrada e uma API HTTP compatível com OpenAI. Esta é a interface preferida para implantações de longa duração, acesso multiusuário e integração com ferramentas externas.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Encontrando `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Em cada uma das Máquinas 2, 3 e 4, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: Execute este comando no Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **Encontrando `<RPC_WORKER_2_IP>`, `<RPC_WORKER_3_IP>`, `<RPC_WORKER_4_IP>`**: Em cada uma das Máquinas 2, 3 e 4, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.
<!-- @os:end -->

Uma vez iniciado, abra `http://<HOST_IP>:8081` no seu navegador para acessar a interface web integrada. Isso fornece uma interface de chat baseada em navegador para interagir com o modelo:

![interface web do llama-server executando Kimi K2.6 em quatro nós](assets/llama-server-example.png)

<!-- @os:linux -->
> **Encontrando `<HOST_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Encontrando `<HOST_IP>`**: Na Máquina 1, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.
<!-- @os:end -->

#### Referência de Parâmetros

| Flag | Finalidade |
|------|---------|
| `-m` | Caminho para o arquivo de modelo GGUF (use o primeiro fragmento, `00001-of-00008`) |
| `-c` | Tamanho do contexto em tokens. Valores maiores usam mais memória |
| `-fa on` | Habilita o rocWMMA Flash Attention para melhor desempenho em GPUs AMD |
| `-ngl 999` | Descarrega todas as camadas do modelo para a GPU |
| `-lm none` | Define o modo de carregamento do modelo como `none`, desabilitando o mapeamento de memória para reduzir os tempos de carregamento quando o tamanho do modelo excede a RAM do sistema, mas cabe na VRAM |
| `-b` | Tamanho do lote lógico em tokens. Definir como 4096 equilibra a taxa de transferência e o uso de memória entre os nós |
| `-ub` | Tamanho do lote físico (micro) para processamento de prompts. Corresponder a `-b` evita sobrecarga desnecessária de fragmentação |
| `--host` | IP ao qual vincular o `llama-server` (`llama-server` somente) |
| `--port` | Porta na qual servir a API HTTP (`llama-server` somente) |
| `--rpc` | Lista separada por vírgulas de endpoints de workers RPC (`IP:port`) |

Para o uso completo dos parâmetros, consulte a [documentação do llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e a [documentação do llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Próximos Passos

- **Conectar aplicativos de terceiros**: `llama-server` expõe uma API compatível com OpenAI. Aponte qualquer aplicativo compatível com OpenAI (como o Open WebUI) para `http://<HOST_IP>:8081` com qualquer chave de API de espaço reservado (por exemplo, `none`) para se conectar ao seu cluster
- **Explorar outros modelos**: Navegue por GGUFs quantizados no [Hugging Face](https://huggingface.co/models?search=gguf) para encontrar modelos que caibam dentro da memória de GPU combinada do seu cluster
- **Escalar além de quatro nós**: Adicione mais sistemas Ryzen AI Halo como workers RPC adicionais para acessar modelos além da escala de 1 trilhão de parâmetros. Passe endpoints adicionais para `--rpc` como uma lista separada por vírgulas (por exemplo, `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`)
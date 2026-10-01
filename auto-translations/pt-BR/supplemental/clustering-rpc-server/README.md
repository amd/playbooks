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

# Clusterização de Dois Ryzen™ AI Halo com RPC

## Visão Geral

Seu Ryzen™ AI Halo já é capaz de executar modelos de linguagem grandes localmente. A clusterização leva isso ainda mais longe ao combinar a memória de GPU de múltiplos sistemas em uma rede local, dando acesso a modelos ainda maiores, com raciocínio mais forte, melhor geração de código e compreensão multilíngue mais profunda, tudo isso inteiramente em seu próprio hardware.

Este guia ensina como agrupar dois sistemas Ryzen AI Halo usando o motor RPC do llama.cpp e executar o GLM 4.7, um modelo de 358 bilhões de parâmetros, em ambas as máquinas com aceleração AMD ROCm™.

## O Que Você Vai Aprender

- Como estender a alocação de VRAM em sistemas Ryzen AI Halo
- Instalação do llama.cpp com suporte a ROCm e RPC
- Configuração de um worker RPC e execução de inferência distribuída em dois nós
- Execução de um modelo de 358 bilhões de parâmetros em dois sistemas Ryzen AI Halo conectados em rede

## Configurando a Memória

> **Observação**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

<!-- @os:windows -->
No Windows, para executar modelos maiores que exigem mais memória, precisamos usar a alocação de Memória Gráfica Variável da AMD (VRAM da iGPU).

Isso pode ser feito abrindo o painel de controle AMD Software: Adrenalin Edition e navegando até: `Performance > Tuning > AMD Variable Graphics Memory`. Defina o valor como **96 GB**. Reinicie o sistema para que as alterações tenham efeito.

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
No Linux, o ROCm utiliza um pool de memória compartilhada do sistema, e esse pool é configurado por padrão para metade da memória do sistema.

Essa quantidade pode ser aumentada alterando a configuração de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB).

* Instale o utilitário pipx e adicione o caminho dos wheels instalados pelo pipx ao caminho de busca do sistema.

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
## Verifique se Há Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->
## Pré-requisitos

### Hardware

Este guia requer duas unidades Ryzen AI Halo e um switch Ethernet, conectados em uma topologia estrela, com cada unidade ligada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nós de computação que formam o cluster |
| Switch Ethernet de 10 Gbps | 1 | Switch central para permitir a comunicação multinó entre os Ryzen AI Halo (pelo menos 2 portas) |
| Cabo Ethernet | 2 | Conecta cada unidade Halo ao switch (recomendado Cat 7 ou superior) |

> **Observação**: São necessárias duas portas de switch Ethernet para conectar as duas unidades Ryzen AI Halo. Uma terceira porta é necessária se você acessar o modelo a partir de uma máquina cliente separada, em vez de a partir de uma das unidades Halo.

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

> **Observação**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

Conecte cada unidade Ryzen AI Halo ao switch Ethernet usando um cabo Cat 7 (ou superior). Isso estabelece o link de 10 Gbps usado para comunicação de alta velocidade entre os nós.
<!-- @os:linux -->
### 1. Determine as Interfaces de Rede

Em cada máquina, encontre o nome da sua interface de rede e anote-o (ele será referido abaixo como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isso exibe diretamente o nome da interface, por exemplo:

```bash
enp191s0
```

### 2. Verifique as Velocidades do Link de Rede

Confirme se o link está ativo e funcionando na velocidade máxima verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Observação**: Substitua `<IFNAME>` pelo nome da interface de saída obtido em [1. Determine as Interfaces de Rede](#1-determine-network-interfaces)

Você deve ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Observação**: Se a velocidade for menor que `10000Mb/s` ou o link não subir, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10 Gbps. Alguns switches exigem que a auto-negociação seja desativada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

<!-- @os:windows -->
### Verifique a Velocidade do Link de Rede

Em cada máquina, verifique a velocidade do link das suas interfaces de rede:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

Sua interface Ethernet deve estar `Up` e funcionando a `10 Gbps`:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **Observação**: Se a velocidade for menor que `10 Gbps` ou o link não subir, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10 Gbps. Alguns switches exigem que a auto-negociação seja desativada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

<!-- @os:end -->

## Instalando o llama.cpp

> **Observação**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

Duas opções de instalação estão disponíveis:

- [Opção 1: Lemonade SDK (Recomendado)](#option-1-lemonade-sdk-recommended) - binários pré-compilados, configuração mais rápida
- [Opção 2: Compilação Manual a partir do Código-Fonte](#option-2-manual-source-build) - compile a partir do código-fonte com controle total sobre as flags de build

### Opção 1: Lemonade SDK (Recomendado)

O Lemonade SDK fornece builds noturnos do llama.cpp com aceleração AMD ROCm 7, direcionados a GPUs como gfx1151 (Strix Halo / Ryzen AI Max+ 395) e outras arquiteturas Radeon recentes.

<!-- @os:windows -->
#### Step 1: Baixar os binários pré-compilados

Navegue até a página do lançamento mais recente e baixe o pacote correspondente à sua plataforma e ao GPU de destino:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Baixe o arquivo chamado `llama-bxxxx-windows-rocm-gfx1151-x64.zip` (em que `xxxx` é o número da build).

#### Step 2: Extrair os binários

Descompacte o arquivo baixado:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

Esse diretório agora contém builds do `llama-cli.exe`, `llama-server.exe` e `rpc-server.exe` habilitadas para ROCm, pré-compiladas para o seu sistema Ryzen AI Halo.

#### Step 3: Verificar a detecção da GPU

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
#### Step 1: Baixar os binários pré-compilados

Navegue até a página do lançamento mais recente e baixe o pacote correspondente à sua plataforma e ao GPU de destino:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

Baixe o arquivo chamado `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` (em que `xxxx` é o número da build).

#### Step 2: Extrair e preparar os binários

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

Esse diretório agora contém builds do `llama-cli`, `llama-server` e `rpc-server` habilitadas para ROCm, pré-compiladas para o seu sistema Ryzen AI Halo.

#### Step 3: Verificar a detecção da GPU

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
Com o llama.cpp preparado em cada nó, prossiga para [Baixando o modelo](#downloading-the-model).

### Opção 2: Build manual a partir do código-fonte

<!-- @os:windows -->
#### Step 1: Compilar o llama.cpp

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

| Build Flag | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita o stack de software ROCm/HIP |
| `-DGGML_RPC=ON` | Habilita o RPC para inferência distribuída |
| `-DGPU_TARGETS=gfx1151` | Direciona para a GPU Ryzen AI Halo (Radeon 8060s) |
| `-G Ninja` | Usa o sistema de build Ninja |

#### Step 2: Verificar a detecção da GPU

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

#### Step 3: Adicionar o HIP ao seu path de usuário

A etapa de compilação acima definiu `%HIP_PATH%\bin` apenas para a sessão atual. Para disponibilizar as bibliotecas HIP em qualquer terminal (não apenas no x64 Native Tools Command Prompt), adicione-o permanentemente ao `PATH` do seu usuário:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

Com o llama.cpp preparado em cada nó, prossiga para [Baixando o modelo](#downloading-the-model).
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: Compilar o llama.cpp

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

| Build Flag | Finalidade |
|-----------|---------|
| `-DGGML_HIP=ON` | Habilita o stack de software ROCm |
| `-DGGML_RPC=ON` | Habilita o RPC para inferência distribuída |
| `-DAMDGPU_TARGETS="gfx1151"` | Direciona para a GPU Ryzen AI Halo (Radeon 8060s) |

Para mais opções de build, consulte a [documentação de build do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md).

#### Step 2: Verificar a detecção da GPU

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

Com o llama.cpp preparado em cada nó, prossiga para [Baixando o modelo](#downloading-the-model).
<!-- @os:end -->

## Baixando o modelo

Este playbook usa o [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7), um modelo de 358B parâmetros na quantização `Q4_K_XL` fornecida pela [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL). Nessa quantização, o modelo requer aproximadamente 205GB de armazenamento e cabe na memória combinada das GPUs de dois nós Ryzen AI Halo.

Baixe os arquivos GGUF usando a CLI do Hugging Face:
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

> **Observação**: o download do modelo deve ser concluído na Máquina 1 (o controlador). Os nós worker de RPC não precisam de uma cópia local dos arquivos do modelo.

## Iniciando o modelo no cluster

O mecanismo RPC (Remote Procedure Call) do llama.cpp permite que uma única instância do llama.cpp transfira camadas do modelo para workers remotos pela rede. Uma máquina atua como **controlador** (Máquina 1), cuidando de tokenização, agendamento e orquestração. A outra máquina executa um **servidor RPC** leve (Máquina 2) que expõe sua memória de GPU e capacidade de computação ao controlador.

No momento do carregamento, o llama.cpp fragmenta o modelo entre os dois nós. Depois de carregado, a inferência prossegue como se estivesse rodando em um único acelerador. O RPC cuida das transferências de tensores e da sincronização nos bastidores.

### Step 1: Iniciar o servidor RPC (Máquina 2)

Na Máquina 2, inicie o servidor RPC para expor seus recursos de GPU ao controlador:
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
| `-p` | Porta em que o servidor RPC será transmitido |
| `-c` | Habilita um cache local para tensores grandes, evitando transferências de rede repetidas durante o carregamento do modelo |
| `--host` | Endereço IP ao qual o servidor RPC será vinculado (`0.0.0.0` para todas as interfaces) |

Para mais opções, consulte a [documentação de RPC do llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md).

### Step 2: Iniciar o modelo (Máquina 1)

Com o servidor RPC em execução na Máquina 2, inicie a inferência a partir da Máquina 1 usando `llama-cli` ou `llama-server`.

#### llama-cli

O `llama-cli` fornece uma interface baseada em terminal para interagir diretamente com o modelo. É ideal para benchmarking, depuração e experimentação de baixo nível.

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrando o `<RPC_WORKER_IP>`**: na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: execute esse comando no Terminal (Powershell).

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **Encontrando o `<RPC_WORKER_IP>`**: na Máquina 2, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.

<!-- @os:end -->

Uma vez em execução, o `llama-cli` exibe o progresso do carregamento do modelo e entra em um prompt interativo onde você pode conversar diretamente com o modelo:

![llama-cli executando o GLM 4.7 em dois nós](assets/llama-cli-example.png)
#### llama-server

`llama-server` expõe o mesmo mecanismo de inferência por meio de um processo de servidor persistente com uma UI web integrada e uma API HTTP compatível com OpenAI. Essa é a interface preferida para implantações de execução mais longa, acesso multiusuário e integração com ferramentas externas.

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **Localizando o `<RPC_WORKER_IP>`**: Na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Observação**: Execute este comando no Terminal (Powershell).

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **Localizando o `<RPC_WORKER_IP>`**: Na Máquina 2, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.
<!-- @os:end -->

Após a inicialização, abra `http://<HOST_IP>:8081` no seu navegador para acessar a UI web integrada. Isso fornece uma interface de chat baseada em navegador para interagir com o modelo:

![UI web do llama-server executando o GLM 4.7 em dois nós](assets/llama-server-example.png)

<!-- @os:linux -->
> **Localizando o `<HOST_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
<!-- @os:end -->

<!-- @os:windows -->
> **Localizando o `<HOST_IP>`**: Na Máquina 1, execute `ipconfig | findstr /C:"IPv4"` no Terminal (Powershell) para encontrar seu endereço IP local.
<!-- @os:end -->

#### Referência de Parâmetros

| Flag | Finalidade |
|------|---------|
| `-m` | Caminho para o arquivo de modelo GGUF (use o primeiro fragmento, `00001-of-00005`) |
| `-c` | Tamanho do contexto em tokens. Valores maiores usam mais memória |
| `-fa on` | Ativa o rocWMMA Flash Attention para melhor desempenho em GPUs AMD |
| `-ngl 999` | Descarrega todas as camadas do modelo para a GPU |
| `-lm none` | Define o modo de carregamento do modelo como `none`, desativando o mapeamento de memória para reduzir os tempos de carregamento quando o tamanho do modelo excede a RAM do sistema, mas cabe na VRAM |
| `--host` | IP ao qual o `llama-server` será vinculado (apenas `llama-server`) |
| `--port` | Porta na qual a API HTTP será disponibilizada (apenas `llama-server`) |
| `--rpc` | Lista de endpoints de workers RPC separados por vírgula (`IP:port`) |

Para o uso completo dos parâmetros, consulte a [documentação do llama-cli](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) e a [documentação do llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## Próximos Passos

- **Conectar aplicativos de terceiros**: o `llama-server` expõe uma API compatível com OpenAI. Aponte qualquer aplicativo compatível com OpenAI (como o Open WebUI) para `http://<HOST_IP>:8081` com qualquer chave de API de espaço reservado (por exemplo, `none`) para se conectar ao seu cluster
- **Explorar outros modelos**: Navegue pelos GGUFs quantizados no [Hugging Face](https://huggingface.co/models?search=gguf) para encontrar modelos que caibam na memória GPU combinada do seu cluster
- **Escalar para quatro nós**: Adicione mais dois sistemas Ryzen AI Halo como workers RPC adicionais para acessar modelos na escala de 1 trilhão de parâmetros. Passe endpoints adicionais para `--rpc` como uma lista separada por vírgula (por exemplo, `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)
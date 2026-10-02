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

# Agrupamento de Quatro Ryzen™ AI Halos com RCCL

## Visão Geral

O seu Ryzen™ AI Halo já é capaz de executar grandes modelos de linguagem localmente. O agrupamento leva isto mais além, combinando a memória GPU de vários sistemas numa rede local, dando-lhe acesso a modelos ainda maiores com raciocínio mais forte, melhor geração de código e uma compreensão multilingue mais profunda, tudo inteiramente no seu próprio hardware.

Este manual ensina-o a agrupar quatro sistemas Ryzen AI Halo utilizando RCCL (ROCm Communication Collectives Library) com vLLM e a executar o Qwen3.5-397B, um modelo de 397 mil milhões de parâmetros, em todas as quatro máquinas com aceleração ROCm.

## O Que Vai Aprender

- Como alargar a alocação de VRAM em sistemas Ryzen AI Halo
- Lançar o vLLM com suporte ROCm
- Configurar o RCCL para inferência tensor-paralela multi-nó em quatro sistemas Ryzen AI Halo
- Executar um modelo de 397 mil milhões de parâmetros em quatro sistemas Ryzen AI Halo ligados em rede

## Pré-requisitos

### Hardware

Este manual requer quatro unidades Ryzen AI Halo e um switch Ethernet, ligados numa topologia em estrela com cada unidade ligada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nós de computação que formam o cluster |
| Switch Ethernet de 10Gbps | 1 | Switch central para permitir a comunicação multi-nó entre unidades Ryzen AI Halo (pelo menos 4 portas) |
| Cabo Ethernet | 4 | Liga cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Nota**: São necessárias quatro portas de switch Ethernet para ligar as quatro unidades Ryzen AI Halo. É necessária uma quinta porta se aceder ao modelo a partir de uma máquina cliente separada em vez de a partir de uma das unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuração Física do Hardware

> **Nota**: Complete este passo em todas as quatro máquinas (Máquina 1 a Máquina 4).

Ligue cada unidade Ryzen AI Halo ao switch Ethernet utilizando um cabo Cat 7 (ou superior). Isto estabelece a ligação de 10Gbps utilizada para comunicação de alta velocidade entre os nós.

### 1. Determinar as Interfaces de Rede

Em cada máquina, encontre o nome da sua interface de rede e anote-o (será referido no resto das instruções como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isto apresenta o nome da interface diretamente, por exemplo:

```bash
enp191s0
```

### 2. Verificar as Velocidades de Ligação de Rede

Confirme que a ligação está ativa e a funcionar à velocidade total verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Substitua `<IFNAME>` pelo nome de interface de saída de [1. Determinar as Interfaces de Rede](#1-determine-network-interfaces)

Deverá ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se a velocidade for inferior a `10000Mb/s` ou a ligação não estabelecer, verifique a ligação do cabo e confirme que a porta do switch está configurada para 10Gbps. Alguns switches requerem que a negociação automática seja desativada e a velocidade de ligação definida manualmente; consulte a documentação do seu switch.

## Alargar a Alocação de VRAM

> **Nota**: Complete este passo em todas as quatro máquinas (Máquina 1 a Máquina 4).

### Configuração de Memória para Executar Modelos Grandes

No Linux, o ROCm utiliza um conjunto de memória do sistema partilhado, e este conjunto está configurado por predefinição para metade da memória do sistema.

Esta quantidade pode ser aumentada alterando a definição de página do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir o mínimo de VRAM dedicada na BIOS (0,5 GB).

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

## Inicialização do Contentor vLLM

> **Nota**: Complete este passo em todas as quatro máquinas (Máquina 1 a Máquina 4).

O seu Ryzen AI Halo é fornecido com o vLLM empacotado dentro de uma imagem de contentor pré-construída, que executa utilizando o Podman, uma ferramenta de contentores gratuita e de código aberto.

### 1. Criar o Diretório de Transferência do Modelo

Quando servir o modelo Qwen3.5-397B neste manual, o vLLM transferirá automaticamente os pesos do modelo para o seu sistema. Para garantir que esses pesos são acessíveis a partir de dentro do contentor, crie primeiro um diretório de modelos que o contentor possa montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lançar o Contentor vLLM

O comando abaixo lança o contentor e coloca-o numa shell interativa. Monta o diretório de modelos que acabou de criar e passa o seu `IFNAME` para `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, informando o RCCL (a biblioteca que o vLLM utiliza para coordenar GPUs em todo o cluster) sobre qual interface utilizar.

Inicie o contentor com:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Substitua `<IFNAME>` pelo nome de interface de saída de [1. Determinar as Interfaces de Rede](#1-determine-network-interfaces)

## Executar o Modelo no Cluster

O vLLM utiliza o Ray para orquestrar o cluster e o RCCL para lidar com a comunicação GPU-a-GPU entre nós. Uma máquina atua como nó principal (Máquina 1), coordenando a inferência. As outras três juntam-se como nós de trabalho (Máquinas 2, 3 e 4), contribuindo com a sua memória GPU e capacidade de processamento.

> **Nota**: O Ray é uma dependência opcional para o vLLM e só está disponível a partir do contentor Podman pré-configurado.

No arranque, o vLLM divide o modelo entre os quatro nós utilizando paralelismo tensor. Uma vez carregado, a inferência prossegue como se estivesse a ser executada num único acelerador.

#### Prevenir Erros OOM do Ray

Por predefinição, o Ray monitoriza a memória do anfitrião em cada nó e termina o maior processo quando a utilização de memória ultrapassa os 95%. No seu Ryzen™ AI Halo, a GPU e o anfitrião partilham um conjunto de memória, pelo que carregar um modelo pode desencadear um `ray.exceptions.OutOfMemoryError` e terminar o processo de trabalho.

Para prevenir isto, iremos exportar `RAY_memory_monitor_refresh_ms=0` em cada máquina antes de iniciar e juntar-se ao cluster.
### Passo 1: Iniciar o Nó Principal do Ray (Máquina 1)

Na Máquina 1, inicie o nó principal do Ray para inicializar o cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **A encontrar `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.

### Passo 2: Juntar-se ao Cluster (Máquinas 2, 3 e 4)

Em cada uma das Máquinas 2, 3 e 4, ligue-se ao nó principal para formar o cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **A encontrar `<MACHINE_N_IP>`**: Em cada máquina de trabalho, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.

### Passo 3: Servir o Modelo (Máquina 1)

Na Máquina 1, inicie o servidor vLLM. Isto irá descarregar automaticamente o modelo e começar a servi-lo em todos os quatro nós:

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

#### Referência de Parâmetros

| Flag | Finalidade |
|------|---------|
| `--port` | Porta para servir a API HTTP |
| `--host` | Endereço IP ao qual associar o servidor (`0.0.0.0` para todas as interfaces) |
| `--max-model-len` | Comprimento máximo do contexto em tokens |
| `--gpu-memory-utilization` | Fração da memória da GPU a alocar (0.0–1.0) |
| `--dtype` | Tipo de dados para os pesos do modelo |
| `--tensor-parallel-size` | Número de GPUs pelas quais fragmentar o modelo (definir para o total de GPUs no cluster) |
| `--distributed-executor-backend` | Backend para execução multi-nó (`ray` para implementações em cluster) |
| `--enforce-eager` | Desativa a compilação de CUDA graph para compatibilidade |
| `--language-model-only` | Ignora o carregamento de componentes auxiliares do modelo (por exemplo, o codificador de visão) |
| `--reasoning-parser` | Ativa a análise estruturada da saída de raciocínio para o modelo |

Para a utilização completa dos parâmetros, consulte a [documentação do vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Aceder ao Modelo

O vLLM expõe uma API compatível com OpenAI, pelo que pode ligar qualquer cliente ou interface compatível ao seu cluster. Uma opção popular é o [Open WebUI](https://github.com/open-webui/open-webui), que fornece uma interface de chat baseada no browser.

Para ligar o Open WebUI ao seu endpoint vLLM:

1. Abra **Settings** > **Admin Panel** > **Connections**
2. Clique no **+** em **Manage OpenAI API Connections**
3. Defina o **Connection Type** como **External**
4. Defina o **URL** como `http://<MACHINE_1_IP>:7000/v1`
5. Em **Auth**, selecione **None** no menu pendente
6. Deixe **Model IDs** vazio para descobrir automaticamente todos os modelos a partir do endpoint

> **A encontrar `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local. Se aceder ao Open WebUI a partir da própria Máquina 1, pode utilizar `http://localhost:7000/v1`.

![Definições de ligação do Open WebUI para o endpoint vLLM](assets/openwebui-connection.png)

Depois de estabelecida a ligação, selecione o modelo no menu pendente de modelos no Open WebUI e comece a conversar. O modelo está agora em execução em todos os quatro nós do seu Ryzen AI Halo:

![A conversar com o Qwen3.5-397B no Open WebUI](assets/openwebui-chat.png)

## Próximos Passos

- **Explore outros modelos**: Descubra novos modelos no [Hugging Face](https://huggingface.co/models?&sort=trending) que caibam na memória de GPU combinada do seu cluster
- **Expanda para além de quatro nós**: Adicione mais sistemas Ryzen AI Halo como trabalhadores Ray adicionais para fragmentar modelos entre ainda mais GPUs. Siga o [Passo 2: Juntar-se ao Cluster](#step-2-join-the-cluster-machines-2-3-and-4) em cada trabalhador adicional e aumente `--tensor-parallel-size` em conformidade
- **Experimente outras estratégias de paralelismo**: O vLLM suporta [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos de mistura de especialistas (mixture-of-experts) e [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para maior débito. Experimente `--enable-expert-parallel` e `--data-parallel-size` para encontrar a melhor configuração para a sua carga de trabalho
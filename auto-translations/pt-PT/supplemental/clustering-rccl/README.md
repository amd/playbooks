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

# Configurar um cluster com dois Ryzen™ AI Halo com RCCL

## Visão geral

O seu Ryzen™ AI Halo já é capaz de executar modelos de linguagem de grande dimensão localmente. A configuração em cluster leva isto ainda mais longe, combinando a memória GPU de vários sistemas através de uma rede local, dando-lhe acesso a modelos ainda maiores, com raciocínio mais sólido, melhor geração de código e uma compreensão multilingue mais profunda, tudo inteiramente no seu próprio hardware.

Este manual ensina-o a configurar um cluster com dois sistemas Ryzen AI Halo utilizando RCCL (ROCm Communication Collectives Library) com vLLM e a executar o Qwen3.5-397B, um modelo com 397 mil milhões de parâmetros, em ambas as máquinas com aceleração ROCm.

## O que vai aprender

- Como aumentar a alocação de VRAM em sistemas Ryzen AI Halo
- Iniciar o vLLM com suporte para ROCm
- Configurar o RCCL para inferência com paralelismo de tensores em múltiplos nós, em dois sistemas Ryzen AI Halo
- Executar um modelo com 397 mil milhões de parâmetros em dois sistemas Ryzen AI Halo ligados em rede

## Pré-requisitos

### Hardware

Este manual requer duas unidades Ryzen AI Halo e um switch Ethernet, ligados numa topologia em estrela, com cada unidade ligada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nós de computação que formam o cluster |
| Switch Ethernet de 10 Gbps | 1 | Switch central que permite a comunicação entre múltiplos nós Ryzen AI Halo (pelo menos 2 portas) |
| Cabo Ethernet | 2 | Liga cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Nota**: São necessárias duas portas do switch Ethernet para ligar as duas unidades Ryzen AI Halo. É necessária uma terceira porta caso aceda ao modelo a partir de uma máquina cliente separada, em vez de a partir de uma das unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuração física do hardware

> **Nota**: Complete este passo tanto na Máquina 1 como na Máquina 2.

Ligue cada unidade Ryzen AI Halo ao switch Ethernet utilizando um cabo Cat 7 (ou superior). Isto estabelece a ligação de 10 Gbps utilizada para a comunicação de alta velocidade entre os nós.

### 1. Determinar as interfaces de rede

Em cada máquina, encontre o nome da respetiva interface de rede e anote-o (será referido no resto das instruções como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isto apresenta diretamente o nome da interface, por exemplo:

```bash
enp191s0
```

### 2. Verificar as velocidades da ligação de rede

Confirme que a ligação está ativa e a funcionar à velocidade máxima, verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Substitua `<IFNAME>` pelo nome da interface de saída obtido em [1. Determinar as interfaces de rede](#1-determinar-as-interfaces-de-rede)

Deverá ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se a velocidade for inferior a `10000Mb/s` ou a ligação não ficar ativa, verifique a ligação do cabo e confirme que a porta do switch está definida para 10 Gbps. Alguns switches exigem que a negociação automática seja desativada e a velocidade da ligação definida manualmente; consulte a documentação do seu switch.

## Aumentar a alocação de VRAM

> **Nota**: Complete este passo tanto na Máquina 1 como na Máquina 2.

### Configuração de memória para executar modelos de grande dimensão

No Linux, o ROCm utiliza um conjunto de memória partilhada do sistema, e este conjunto está configurado por predefinição para metade da memória do sistema.

Esta quantidade pode ser aumentada alterando a definição de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB).

* Instale o utilitário pipx e adicione o caminho para os wheels instalados pelo pipx ao caminho de pesquisa do sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instale o wheel amd-debug-tools a partir do PyPI.
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

## Inicialização do contentor vLLM

> **Nota**: Complete este passo tanto na Máquina 1 como na Máquina 2.

O seu Ryzen AI Halo é fornecido com o vLLM já incluído numa imagem de contentor pré-criada, que executa utilizando o Podman, uma ferramenta de contentores gratuita e de código aberto.

### 1. Criar o diretório de transferência do modelo

Ao servir o modelo Qwen3.5-397B neste manual, o vLLM transferirá automaticamente os pesos do modelo para o seu sistema. Para garantir que esses pesos estão acessíveis a partir de dentro do contentor, comece por criar um diretório de modelos que o contentor possa montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Iniciar o contentor vLLM

O comando abaixo inicia o contentor e coloca-o numa shell interativa. Este monta o diretório de modelos que acabou de criar e passa o seu `IFNAME` para `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, indicando ao RCCL (a biblioteca que o vLLM utiliza para coordenar as GPUs em todo o cluster) qual a interface a utilizar.

Inicie o contentor com:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Substitua `<IFNAME>` pelo nome da interface de saída obtido em [1. Determinar as interfaces de rede](#1-determinar-as-interfaces-de-rede)

## Executar o modelo no cluster

O vLLM utiliza o Ray para orquestrar o cluster e o RCCL para gerir a comunicação de GPU para GPU entre nós. Uma máquina atua como **nó principal** (Máquina 1), coordenando a inferência. A outra junta-se como **nó de trabalho** (Máquina 2), contribuindo com a sua memória de GPU e capacidade de computação.

> **Nota**: O Ray é uma dependência opcional para o vLLM e apenas está disponível a partir do contentor Podman pré-configurado.

No arranque, o vLLM divide o modelo entre ambos os nós utilizando paralelismo de tensores. Depois de carregado, a inferência prossegue como se estivesse a ser executada num único acelerador.

### Passo 1: Iniciar o nó principal do Ray (Máquina 1)

Na Máquina 1, inicie o nó principal do Ray para inicializar o cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Encontrar `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.
### Passo 2: Juntar-se ao Cluster (Máquina 2)

Na Máquina 2, ligue-se ao nó principal para formar o cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Encontrar o `<MACHINE_2_IP>`**: Na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local.

### Passo 3: Servir o Modelo (Máquina 1)

Na Máquina 1, inicie o servidor vLLM. Isto irá transferir automaticamente o modelo e começar a servi-lo em ambos os nós:

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

#### Referência de Parâmetros

| Flag | Finalidade |
|------|---------|
| `--port` | Porta na qual servir a API HTTP |
| `--host` | Endereço IP ao qual associar o servidor (`0.0.0.0` para todas as interfaces) |
| `--max-model-len` | Comprimento máximo de contexto em tokens |
| `--gpu-memory-utilization` | Fração da memória da GPU a alocar (0.0–1.0) |
| `--dtype` | Tipo de dados para os pesos do modelo |
| `--tensor-parallel-size` | Número de GPUs pelas quais fragmentar o modelo (definir para o total de GPUs no cluster) |
| `--distributed-executor-backend` | Backend para execução multi-nó (`ray` para implementações em cluster) |
| `--enforce-eager` | Desativa a compilação de gráficos CUDA para compatibilidade |
| `--language-model-only` | Ignora o carregamento de componentes auxiliares do modelo (por exemplo, codificador de visão) |
| `--reasoning-parser` | Ativa a análise estruturada de saída de raciocínio para o modelo |

Para a utilização completa dos parâmetros, consulte a [documentação do vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Aceder ao Modelo

O vLLM expõe uma API compatível com OpenAI, pelo que pode ligar qualquer cliente ou interface compatível ao seu cluster. Uma opção popular é o [Open WebUI](https://github.com/open-webui/open-webui), que fornece uma interface de chat baseada no navegador.

Para ligar o Open WebUI ao seu endpoint vLLM:

1. Abra **Settings** > **Admin Panel** > **Connections**
2. Clique no **+** em **Manage OpenAI API Connections**
3. Defina o **Connection Type** para **External**
4. Defina o **URL** para `http://<MACHINE_1_IP>:7000/v1`
5. Em **Auth**, selecione **None** na lista pendente
6. Deixe **Model IDs** vazio para descobrir automaticamente todos os modelos a partir do endpoint

> **Encontrar o `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar o seu endereço IP local. Se aceder ao Open WebUI a partir da própria Máquina 1, pode utilizar `http://localhost:7000/v1`.

![Definições de ligação do Open WebUI para o endpoint vLLM](assets/openwebui-connection.png)

Depois de ligado, selecione o modelo na lista pendente de modelos no Open WebUI e comece a conversar. O modelo está agora a funcionar em ambos os seus nós Ryzen AI Halo:

![A conversar com o Qwen3.5-397B no Open WebUI](assets/openwebui-chat.png)

## Passos Seguintes

- **Explore outros modelos**: Descubra novos modelos no [Hugging Face](https://huggingface.co/models?&sort=trending) que caibam dentro da memória de GPU combinada do seu cluster
- **Escale para quatro nós**: Adicione mais dois sistemas Ryzen AI Halo como workers Ray adicionais para fragmentar modelos entre ainda mais GPUs. Isto requer um switch Ethernet com pelo menos quatro portas, uma para cada nó. Siga o [Passo 2: Juntar-se ao Cluster](#step-2-join-the-cluster-machine-2) em cada worker adicional e aumente o `--tensor-parallel-size` em conformidade
- **Experimente outras estratégias de paralelismo**: O vLLM suporta [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos mixture-of-experts e [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para maior taxa de transferência. Experimente `--enable-expert-parallel` e `--data-parallel-size` para encontrar a melhor configuração para a sua carga de trabalho
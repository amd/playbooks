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

# Clusterizando dois Ryzen™ AI Halo com RCCL

## Visão Geral

Seu Ryzen™ AI Halo já é capaz de executar modelos de linguagem de grande porte localmente. A clusterização leva isso ainda mais longe, combinando a memória de GPU de múltiplos sistemas em uma rede local, dando a você acesso a modelos ainda maiores, com raciocínio mais forte, melhor geração de código e compreensão multilíngue mais profunda, tudo inteiramente em seu próprio hardware.

Este playbook ensina como clusterizar dois sistemas Ryzen AI Halo usando RCCL (ROCm Communication Collectives Library) com vLLM e executar o Qwen3.5-397B, um modelo com 397B de parâmetros, em ambas as máquinas com aceleração ROCm.

## O Que Você Vai Aprender

- Como estender a alocação de VRAM em sistemas Ryzen AI Halo
- Como iniciar o vLLM com suporte a ROCm
- Como configurar o RCCL para inferência tensor-paralela multi-nó em dois sistemas Ryzen AI Halo
- Como executar um modelo de 397B de parâmetros em dois sistemas Ryzen AI Halo conectados em rede

## Pré-requisitos

### Hardware

Este playbook requer duas unidades Ryzen AI Halo e um switch Ethernet, conectados em uma topologia estrela, com cada unidade conectada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nós de computação que formam o cluster |
| Switch Ethernet de 10Gbps | 1 | Switch central para permitir a comunicação multi-nó do Ryzen AI Halo (pelo menos 2 portas) |
| Cabo Ethernet | 2 | Conecta cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Nota**: São necessárias duas portas do switch Ethernet para conectar as duas unidades Ryzen AI Halo. Uma terceira porta é necessária se você acessar o modelo a partir de uma máquina cliente separada, em vez de uma das unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuração Física do Hardware

> **Nota**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

Conecte cada unidade Ryzen AI Halo ao switch Ethernet usando um cabo Cat 7 (ou superior). Isso estabelece o link de 10Gbps usado para comunicação de alta velocidade entre os nós.

### 1. Determinar as Interfaces de Rede

Em cada máquina, encontre o nome de sua interface de rede e anote-o (ele será referido no restante das instruções como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isso exibe o nome da interface diretamente, por exemplo:

```bash
enp191s0
```

### 2. Verificar as Velocidades do Link de Rede

Confirme que o link está ativo e operando na velocidade máxima verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Substitua `<IFNAME>` pelo nome da interface obtido em [1. Determinar as Interfaces de Rede](#1-determinar-as-interfaces-de-rede)

Você deve ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Se a velocidade for inferior a `10000Mb/s` ou o link não subir, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10Gbps. Alguns switches exigem que a auto-negociação seja desabilitada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

## Estendendo a Alocação de VRAM

> **Nota**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

### Configuração de Memória para Execução de Modelos Grandes

No Linux, o ROCm utiliza um pool de memória compartilhada do sistema, e esse pool é configurado por padrão para metade da memória do sistema.

Essa quantidade pode ser aumentada alterando a configuração de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB).

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

## Inicialização do Contêiner vLLM

> **Nota**: Realize esta etapa tanto na Máquina 1 quanto na Máquina 2.

Seu Ryzen AI Halo é fornecido com o vLLM empacotado dentro de uma imagem de contêiner pré-construída, que você executa usando o Podman, uma ferramenta de contêiner gratuita e de código aberto.

### 1. Criar o Diretório de Download do Modelo

Quando você servir o modelo Qwen3.5-397B neste playbook, o vLLM baixará automaticamente os pesos do modelo para o seu sistema. Para garantir que esses pesos sejam acessíveis de dentro do contêiner, primeiro crie um diretório de modelos que o contêiner possa montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Iniciar o Contêiner vLLM

O comando abaixo inicia o contêiner e o coloca em um shell interativo. Ele monta o diretório de modelos que você acabou de criar e passa seu `IFNAME` para `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, informando ao RCCL (a biblioteca que o vLLM usa para coordenar GPUs em todo o cluster) qual interface usar.

Inicie o contêiner com:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Substitua `<IFNAME>` pelo nome da interface obtido em [1. Determinar as Interfaces de Rede](#1-determinar-as-interfaces-de-rede)

## Executando o Modelo no Cluster

O vLLM usa o Ray para orquestrar o cluster e o RCCL para gerenciar a comunicação GPU a GPU entre os nós. Uma máquina atua como o **nó principal (head node)** (Máquina 1), coordenando a inferência. A outra se junta como um **nó de trabalho (worker node)** (Máquina 2), contribuindo com sua memória de GPU e capacidade de processamento.

> **Nota**: O Ray é uma dependência opcional do vLLM e só está disponível a partir do contêiner Podman pré-configurado.

Na inicialização, o vLLM particiona o modelo entre os dois nós usando paralelismo de tensor. Uma vez carregado, a inferência prossegue como se estivesse sendo executada em um único acelerador.

### Etapa 1: Iniciar o Nó Principal do Ray (Máquina 1)

Na Máquina 1, inicie o nó principal do Ray para inicializar o cluster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Encontrando `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.
### Etapa 2: Junte-se ao Cluster (Máquina 2)

Na Máquina 2, conecte-se ao nó principal para formar o cluster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Encontrando `<MACHINE_2_IP>`**: Na Máquina 2, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.

### Etapa 3: Sirva o Modelo (Máquina 1)

Na Máquina 1, inicie o servidor vLLM. Isso fará o download automático do modelo e começará a servi-lo em ambos os nós:

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
|------|-----------|
| `--port` | Porta na qual servir a API HTTP |
| `--host` | Endereço IP ao qual vincular o servidor (`0.0.0.0` para todas as interfaces) |
| `--max-model-len` | Comprimento máximo de contexto em tokens |
| `--gpu-memory-utilization` | Fração da memória da GPU a ser alocada (0.0–1.0) |
| `--dtype` | Tipo de dado para os pesos do modelo |
| `--tensor-parallel-size` | Número de GPUs para fragmentar o modelo (defina como o total de GPUs no cluster) |
| `--distributed-executor-backend` | Backend para execução multi-nó (`ray` para implantações em cluster) |
| `--enforce-eager` | Desabilita a compilação de CUDA graph para compatibilidade |
| `--language-model-only` | Ignora o carregamento de componentes auxiliares do modelo (por exemplo, codificador de visão) |
| `--reasoning-parser` | Habilita o parsing estruturado de saída de raciocínio para o modelo |

Para o uso completo dos parâmetros, consulte a [documentação do vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Acessando o Modelo

O vLLM expõe uma API compatível com OpenAI, então você pode conectar qualquer cliente ou interface compatível ao seu cluster. Uma opção popular é o [Open WebUI](https://github.com/open-webui/open-webui), que fornece uma interface de chat baseada em navegador.

Para conectar o Open WebUI ao seu endpoint vLLM:

1. Abra **Settings** > **Admin Panel** > **Connections**
2. Clique no **+** em **Manage OpenAI API Connections**
3. Defina o **Connection Type** como **External**
4. Defina a **URL** como `http://<MACHINE_1_IP>:7000/v1`
5. Em **Auth**, selecione **None** no menu suspenso
6. Deixe **Model IDs** vazio para descobrir automaticamente todos os modelos do endpoint

> **Encontrando `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local. Se estiver acessando o Open WebUI a partir da própria Máquina 1, você pode usar `http://localhost:7000/v1`.

![Configurações de conexão do Open WebUI para o endpoint vLLM](assets/openwebui-connection.png)

Uma vez conectado, selecione o modelo no menu suspenso de modelos do Open WebUI e comece a conversar. O modelo agora está sendo executado em ambos os seus nós Ryzen AI Halo:

![Conversando com o Qwen3.5-397B no Open WebUI](assets/openwebui-chat.png)

## Próximos Passos

- **Explore outros modelos**: Descubra novos modelos no [Hugging Face](https://huggingface.co/models?&sort=trending) que se encaixem na memória de GPU combinada do seu cluster
- **Escale para quatro nós**: Adicione mais dois sistemas Ryzen AI Halo como workers Ray adicionais para fragmentar modelos entre ainda mais GPUs. Isso requer um switch Ethernet com pelo menos quatro portas, uma para cada nó. Siga a [Etapa 2: Junte-se ao Cluster](#step-2-join-the-cluster-machine-2) em cada worker adicional e aumente `--tensor-parallel-size` de acordo
- **Experimente outras estratégias de paralelismo**: O vLLM suporta [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos mixture-of-experts e [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para maior throughput. Experimente `--enable-expert-parallel` e `--data-parallel-size` para encontrar a melhor configuração para sua carga de trabalho
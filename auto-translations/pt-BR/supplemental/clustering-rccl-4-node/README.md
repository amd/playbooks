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

# Clusterização de Quatro Ryzen™ AI Halo com RCCL

## Visão Geral

Seu Ryzen™ AI Halo já é capaz de executar grandes modelos de linguagem localmente. A clusterização leva isso ainda mais longe, combinando a memória de GPU de múltiplos sistemas por meio de uma rede local, oferecendo acesso a modelos ainda maiores, com raciocínio mais forte, melhor geração de código e compreensão multilíngue mais profunda, tudo inteiramente em seu próprio hardware.

Este guia ensina como clusterizar quatro sistemas Ryzen AI Halo usando RCCL (ROCm Communication Collectives Library) com vLLM e executar o Qwen3.5-397B, um modelo com 397 bilhões de parâmetros, em todas as quatro máquinas com aceleração ROCm.

## O Que Você Vai Aprender

- Como estender a alocação de VRAM em sistemas Ryzen AI Halo
- Como iniciar o vLLM com suporte a ROCm
- Como configurar o RCCL para inferência tensor-paralela multi-nó em quatro sistemas Ryzen AI Halo
- Como executar um modelo com 397 bilhões de parâmetros em quatro sistemas Ryzen AI Halo em rede

## Pré-requisitos

### Hardware

Este guia requer quatro unidades Ryzen AI Halo e um switch Ethernet, conectados em uma topologia estrela, com cada unidade ligada diretamente ao switch.

| Componente | Quantidade | Descrição |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | Nós de computação que formam o cluster |
| Switch Ethernet 10Gbps | 1 | Switch central para permitir a comunicação multi-nó entre os Ryzen AI Halo (com pelo menos 4 portas) |
| Cabo Ethernet | 4 | Conecta cada unidade Halo ao switch (recomenda-se Cat 7 ou superior) |

> **Observação**: São necessárias quatro portas do switch Ethernet para conectar as quatro unidades Ryzen AI Halo. Uma quinta porta é necessária caso você acesse o modelo a partir de uma máquina cliente separada, em vez de uma das unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuração Física do Hardware

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

Conecte cada unidade Ryzen AI Halo ao switch Ethernet usando um cabo Cat 7 (ou superior). Isso estabelece o link de 10Gbps usado para comunicação de alta velocidade entre os nós.

### 1. Determinar as Interfaces de Rede

Em cada máquina, descubra o nome da sua interface de rede e anote-o (ele será referido no restante das instruções como `IFNAME`). Execute:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Isso exibe o nome da interface diretamente, por exemplo:

```bash
enp191s0
```

### 2. Verificar as Velocidades do Link de Rede

Confirme se o link está ativo e operando na velocidade máxima verificando a velocidade da sua interface:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Observação**: Substitua `<IFNAME>` pelo nome da interface de saída obtido em [1. Determinar as Interfaces de Rede](#1-determine-network-interfaces)

Você deve ver uma velocidade de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Observação**: Se a velocidade for inferior a `10000Mb/s` ou o link não ficar ativo, verifique a conexão do cabo e confirme se a porta do switch está configurada para 10Gbps. Alguns switches exigem que a auto-negociação seja desativada e a velocidade do link definida manualmente; consulte a documentação do seu switch.

## Estendendo a Alocação de VRAM

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

### Configuração de Memória para Executar Modelos Grandes

No Linux, o ROCm utiliza um pool de memória do sistema compartilhado, e esse pool é configurado por padrão para metade da memória do sistema.

Essa quantidade pode ser aumentada alterando a configuração de páginas do Translation Table Manager (TTM) do kernel, seguindo as instruções abaixo. A AMD recomenda definir a VRAM dedicada mínima na BIOS (0,5 GB).

* Instale o utilitário pipx e adicione o caminho das wheels instaladas pelo pipx ao caminho de busca do sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instale a wheel amd-debug-tools do PyPI.
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

> **Observação**: Conclua esta etapa em todas as quatro máquinas (Máquina 1 a Máquina 4).

Seu Ryzen AI Halo vem com o vLLM empacotado dentro de uma imagem de contêiner pré-construída, que você executa usando o Podman, uma ferramenta de contêiner gratuita e de código aberto.

### 1. Criar o Diretório de Download do Modelo

Ao servir o modelo Qwen3.5-397B neste guia, o vLLM fará automaticamente o download dos pesos do modelo para o seu sistema. Para garantir que esses pesos fiquem acessíveis de dentro do contêiner, primeiro crie um diretório de modelos que o contêiner possa montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Iniciar o Contêiner vLLM

O comando abaixo inicia o contêiner e abre um shell interativo. Ele monta o diretório de modelos que você acabou de criar e passa seu `IFNAME` para `NCCL_SOCKET_IFNAME` e `GLOO_SOCKET_IFNAME`, informando ao RCCL (a biblioteca que o vLLM usa para coordenar GPUs em todo o cluster) qual interface usar.

Inicie o contêiner com:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Observação**: Substitua `<IFNAME>` pelo nome da interface de saída obtido em [1. Determinar as Interfaces de Rede](#1-determine-network-interfaces)

## Executando o Modelo no Cluster

O vLLM usa o Ray para orquestrar o cluster e o RCCL para lidar com a comunicação GPU a GPU entre os nós. Uma máquina atua como o nó principal (Máquina 1), coordenando a inferência. As outras três se juntam como nós de trabalho (Máquinas 2, 3 e 4), contribuindo com sua memória de GPU e capacidade de processamento.

> **Observação**: O Ray é uma dependência opcional do vLLM e está disponível apenas dentro do contêiner Podman pré-configurado.

No momento da inicialização, o vLLM fragmenta o modelo entre todos os quatro nós usando paralelismo de tensores. Depois de carregado, a inferência ocorre como se estivesse sendo executada em um único acelerador.

#### Prevenindo Erros de OOM do Ray

Por padrão, o Ray monitora a memória do host em cada nó e encerra o maior processo quando o uso de memória ultrapassa 95%. No seu Ryzen™ AI Halo, a GPU e o host compartilham um único pool de memória, então carregar um modelo pode disparar um `ray.exceptions.OutOfMemoryError` e encerrar o processo de trabalho.

Para evitar isso, vamos exportar `RAY_memory_monitor_refresh_ms=0` em cada máquina antes de iniciar e se juntar ao cluster.
### Etapa 1: Iniciar o Ray Head Node (Máquina 1)

Na Máquina 1, inicie o Ray head node para inicializar o cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Encontrando `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.

### Etapa 2: Entrar no Cluster (Máquinas 2, 3 e 4)

Em cada uma das Máquinas 2, 3 e 4, conecte-se ao head node para formar o cluster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **Encontrando `<MACHINE_N_IP>`**: Em cada máquina worker, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local.

### Etapa 3: Servir o Modelo (Máquina 1)

Na Máquina 1, inicie o servidor vLLM. Isso fará o download do modelo automaticamente e começará a servi-lo em todos os quatro nós:

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
| `--port` | Porta na qual a API HTTP será servida |
| `--host` | Endereço IP ao qual o servidor será vinculado (`0.0.0.0` para todas as interfaces) |
| `--max-model-len` | Comprimento máximo de contexto em tokens |
| `--gpu-memory-utilization` | Fração da memória da GPU a ser alocada (0.0–1.0) |
| `--dtype` | Tipo de dado para os pesos do modelo |
| `--tensor-parallel-size` | Número de GPUs nas quais o modelo será fragmentado (defina como o total de GPUs no cluster) |
| `--distributed-executor-backend` | Backend para execução multi-nó (`ray` para implantações em cluster) |
| `--enforce-eager` | Desabilita a compilação de CUDA graph para compatibilidade |
| `--language-model-only` | Ignora o carregamento de componentes auxiliares do modelo (por exemplo, o codificador de visão) |
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
6. Deixe **Model IDs** em branco para descobrir automaticamente todos os modelos do endpoint

> **Encontrando `<MACHINE_1_IP>`**: Na Máquina 1, execute `hostname -I | awk '{print $1}'` para encontrar seu endereço IP local. Se estiver acessando o Open WebUI a partir da própria Máquina 1, você pode usar `http://localhost:7000/v1`.

![Configurações de conexão do Open WebUI para o endpoint vLLM](assets/openwebui-connection.png)

Após a conexão, selecione o modelo no menu suspenso de modelos no Open WebUI e comece a conversar. O modelo agora está sendo executado em todos os quatro nós Ryzen AI Halo:

![Conversando com Qwen3.5-397B no Open WebUI](assets/openwebui-chat.png)

## Próximos Passos

- **Explore outros modelos**: Descubra novos modelos no [Hugging Face](https://huggingface.co/models?&sort=trending) que caibam na memória de GPU combinada do seu cluster
- **Escale além de quatro nós**: Adicione mais sistemas Ryzen AI Halo como workers adicionais do Ray para fragmentar modelos em ainda mais GPUs. Siga a [Etapa 2: Entrar no Cluster](#step-2-join-the-cluster-machines-2-3-and-4) em cada worker adicional e aumente o `--tensor-parallel-size` de acordo
- **Experimente outras estratégias de paralelismo**: O vLLM oferece suporte a [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos mixture-of-experts e [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para maior throughput. Experimente `--enable-expert-parallel` e `--data-parallel-size` para encontrar a melhor configuração para sua carga de trabalho
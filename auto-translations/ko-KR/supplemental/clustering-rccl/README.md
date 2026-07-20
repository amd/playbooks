<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

# RCCL을 사용하여 두 개의 Ryzen™ AI Halo 클러스터링하기

## 개요

Ryzen™ AI Halo는 이미 로컬에서 대규모 언어 모델을 실행할 수 있는 성능을 갖추고 있습니다. 클러스터링을 통해 로컬 네트워크상에서 여러 시스템의 GPU 메모리를 결합하여 이를 한 단계 더 발전시킬 수 있으며, 이를 통해 더욱 향상된 추론 능력, 더 나은 코드 생성, 더 깊이 있는 다국어 이해 능력을 갖춘 훨씬 더 큰 모델을 완전히 자체 하드웨어에서 사용할 수 있습니다.

이 플레이북에서는 vLLM과 함께 RCCL(ROCm Communication Collectives Library)을 사용하여 두 개의 Ryzen AI Halo 시스템을 클러스터링하고, 397B 파라미터 모델인 Qwen3.5-397B를 두 시스템 모두에서 ROCm 가속을 통해 실행하는 방법을 알아봅니다.

## 학습 내용

- Ryzen AI Halo 시스템에서 VRAM 할당을 확장하는 방법
- ROCm 지원으로 vLLM을 실행하는 방법
- 두 개의 Ryzen AI Halo 시스템 간 멀티 노드 텐서 병렬 추론을 위한 RCCL 구성 방법
- 네트워크로 연결된 두 개의 Ryzen AI Halo 시스템에서 397B 파라미터 모델을 실행하는 방법

## 사전 요구 사항

### 하드웨어

이 플레이북에는 두 개의 Ryzen AI Halo 유닛과 하나의 이더넷 스위치가 필요하며, 각 유닛이 스위치에 직접 연결되는 스타 토폴로지로 구성됩니다.

| 구성 요소 | 수량 | 설명 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 클러스터를 구성하는 컴퓨팅 노드 |
| 10Gbps 이더넷 스위치 | 1 | 멀티 노드 Ryzen AI Halo 통신을 지원하는 중앙 스위치(최소 2개 포트 필요) |
| 이더넷 케이블 | 2 | 각 Halo 유닛을 스위치에 연결(Cat 7 이상 권장) |

> **참고**: 두 개의 Ryzen AI Halo 유닛을 연결하려면 이더넷 스위치 포트 2개가 필요합니다. Halo 유닛 중 하나가 아닌 별도의 클라이언트 머신에서 모델에 액세스하려면 세 번째 포트가 필요합니다.

### 소프트웨어
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 물리적 하드웨어 설정

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

Cat 7(또는 그 이상) 케이블을 사용하여 각 Ryzen AI Halo 유닛을 이더넷 스위치에 연결합니다. 이렇게 하면 노드 간 고속 통신에 사용되는 10Gbps 링크가 구성됩니다.

### 1. 네트워크 인터페이스 확인

각 머신에서 네트워크 인터페이스의 이름을 확인하고 기록해 둡니다(이후 지침에서는 이를 `IFNAME`이라고 표기합니다). 다음 명령을 실행합니다:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

이 명령은 인터페이스 이름을 다음과 같이 직접 출력합니다:

```bash
enp191s0
```

### 2. 네트워크 링크 속도 확인

인터페이스의 속도를 확인하여 링크가 활성화되어 있고 최대 속도로 작동하는지 확인합니다:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **참고**: `<IFNAME>`을 [1. 네트워크 인터페이스 확인](#1-네트워크-인터페이스-확인)에서 확인한 출력 인터페이스 이름으로 바꾸세요.

`10000Mb/s`의 속도가 표시되어야 합니다:

```bash
	Speed: 10000Mb/s
```

> **참고**: 속도가 `10000Mb/s`보다 낮거나 링크가 활성화되지 않는 경우, 케이블 연결을 확인하고 스위치 포트가 10Gbps로 설정되어 있는지 확인하세요. 일부 스위치의 경우 자동 협상(auto-negotiation)을 비활성화하고 링크 속도를 수동으로 설정해야 할 수 있습니다. 자세한 내용은 스위치 설명서를 참조하세요.

## VRAM 할당 확장

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

### 대규모 모델 실행을 위한 메모리 구성

Linux에서 ROCm은 공유 시스템 메모리 풀을 사용하며, 이 풀은 기본적으로 시스템 메모리의 절반으로 구성됩니다.

이 값은 다음 지침에 따라 커널의 Translation Table Manager(TTM) 페이지 설정을 변경하여 늘릴 수 있습니다. AMD는 BIOS에서 최소 전용 VRAM을 0.5GB로 설정할 것을 권장합니다.

* pipx 유틸리티를 설치하고 pipx로 설치된 wheel의 경로를 시스템 검색 경로에 추가합니다.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI에서 amd-debug-tools wheel을 설치합니다.
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttm 도구를 실행하여 공유 메모리의 현재 설정을 조회합니다.
  ```bash
  amd-ttm
  ```

* 공유 메모리 설정을 **120GB**로 재구성합니다:
  ```bash
  amd-ttm --set 120
  ```

* 변경 사항을 적용하려면 시스템을 재부팅합니다.

## vLLM 컨테이너 초기화

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료해야 합니다.

Ryzen AI Halo에는 미리 빌드된 컨테이너 이미지 안에 패키징된 vLLM이 포함되어 있으며, 이는 무료 오픈소스 컨테이너 도구인 Podman을 사용하여 실행합니다.

### 1. 모델 다운로드 디렉터리 생성

이 플레이북에서 Qwen3.5-397B 모델을 서빙하면 vLLM이 모델 가중치를 시스템에 자동으로 다운로드합니다. 해당 가중치를 컨테이너 내부에서 액세스할 수 있도록 하려면, 먼저 컨테이너가 마운트할 수 있는 모델 디렉터리를 생성하세요:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM 컨테이너 실행

아래 명령은 컨테이너를 실행하고 대화형 셸로 진입시킵니다. 이 명령은 방금 생성한 모델 디렉터리를 마운트하고, `IFNAME`을 `NCCL_SOCKET_IFNAME` 및 `GLOO_SOCKET_IFNAME`에 전달하여 vLLM이 클러스터 전체에서 GPU를 조율하는 데 사용하는 라이브러리인 RCCL에 어떤 인터페이스를 사용할지 알려줍니다.

다음 명령으로 컨테이너를 시작합니다:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **참고**: `<IFNAME>`을 [1. 네트워크 인터페이스 확인](#1-네트워크-인터페이스-확인)에서 확인한 출력 인터페이스 이름으로 바꾸세요.

## 클러스터에서 모델 실행

vLLM은 Ray를 사용하여 클러스터를 오케스트레이션하고, RCCL을 사용하여 노드 간 GPU-to-GPU 통신을 처리합니다. 한 머신은 **헤드 노드**(머신 1) 역할을 하며 추론을 조율하고, 다른 머신은 **워커 노드**(머신 2)로 참여하여 자신의 GPU 메모리와 연산 능력을 제공합니다.

> **참고**: Ray는 vLLM의 선택적 의존성이며, 사전 구성된 Podman 컨테이너 내부에서만 사용할 수 있습니다.

시작 시 vLLM은 텐서 병렬 처리를 사용하여 두 노드에 모델을 분할합니다. 로딩이 완료되면 추론은 마치 단일 가속기에서 실행되는 것처럼 진행됩니다.

### 1단계: Ray 헤드 노드 시작(머신 1)

머신 1에서 Ray 헤드 노드를 시작하여 클러스터를 초기화합니다:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` 확인 방법**: 머신 1에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인하세요.
### 2단계: 클러스터에 참여하기 (Machine 2)

Machine 2에서 헤드 노드에 연결하여 클러스터를 구성합니다:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` 찾기**: Machine 2에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다.

### 3단계: 모델 서빙하기 (Machine 1)

Machine 1에서 vLLM 서버를 실행합니다. 이렇게 하면 모델이 자동으로 다운로드되고 두 노드 전체에서 서빙이 시작됩니다:

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

#### 매개변수 참조

| 플래그 | 용도 |
|------|---------|
| `--port` | HTTP API를 서빙할 포트 |
| `--host` | 서버를 바인딩할 IP 주소 (모든 인터페이스는 `0.0.0.0`) |
| `--max-model-len` | 토큰 단위의 최대 컨텍스트 길이 |
| `--gpu-memory-utilization` | 할당할 GPU 메모리 비율 (0.0–1.0) |
| `--dtype` | 모델 가중치의 데이터 타입 |
| `--tensor-parallel-size` | 모델을 분할할 GPU 개수 (클러스터 내 전체 GPU 수로 설정) |
| `--distributed-executor-backend` | 다중 노드 실행을 위한 백엔드 (클러스터 배포 시 `ray`) |
| `--enforce-eager` | 호환성을 위해 CUDA 그래프 컴파일을 비활성화 |
| `--language-model-only` | 보조 모델 구성 요소(예: 비전 인코더) 로드를 건너뜀 |
| `--reasoning-parser` | 모델에 대한 구조화된 추론 출력 파싱을 활성화 |

전체 매개변수 사용법은 [vLLM 문서](https://docs.vllm.ai/en/latest/configuration/engine_args/)를 참고하세요.

## 모델에 접근하기

vLLM은 OpenAI 호환 API를 제공하므로 호환되는 클라이언트나 인터페이스를 클러스터에 연결할 수 있습니다. 인기 있는 옵션 중 하나는 브라우저 기반 채팅 인터페이스를 제공하는 [Open WebUI](https://github.com/open-webui/open-webui)입니다.

Open WebUI를 vLLM 엔드포인트에 연결하려면:

1. **Settings** > **Admin Panel** > **Connections**를 엽니다
2. **Manage OpenAI API Connections**에서 **+**를 클릭합니다
3. **Connection Type**을 **External**로 설정합니다
4. **URL**을 `http://<MACHINE_1_IP>:7000/v1`로 설정합니다
5. **Auth** 아래에서 드롭다운 메뉴에서 **None**을 선택합니다
6. 엔드포인트에서 모든 모델을 자동으로 검색하려면 **Model IDs**를 비워둡니다

> **`<MACHINE_1_IP>` 찾기**: Machine 1에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다. Machine 1 자체에서 Open WebUI에 접근하는 경우 `http://localhost:7000/v1`을 사용할 수 있습니다.

![vLLM 엔드포인트에 대한 Open WebUI 연결 설정](assets/openwebui-connection.png)

연결되면 Open WebUI의 모델 드롭다운에서 모델을 선택하고 채팅을 시작하세요. 이제 모델이 두 개의 Ryzen AI Halo 노드 전체에서 실행됩니다:

![Open WebUI에서 Qwen3.5-397B와 채팅하기](assets/openwebui-chat.png)

## 다음 단계

- **다른 모델 살펴보기**: 클러스터의 결합된 GPU 메모리에 맞는 새로운 모델을 [Hugging Face](https://huggingface.co/models?&sort=trending)에서 찾아보세요
- **4개 노드로 확장하기**: Ryzen AI Halo 시스템 두 대를 추가 Ray 워커로 더해 더 많은 GPU에 걸쳐 모델을 분할합니다. 이를 위해서는 각 노드당 하나씩, 최소 4개의 포트를 가진 이더넷 스위치가 필요합니다. 추가하는 각 워커에서 [2단계: 클러스터에 참여하기](#step-2-join-the-cluster-machine-2)를 따르고 그에 맞게 `--tensor-parallel-size`를 늘리세요
- **다른 병렬화 전략 시도해보기**: vLLM은 전문가 혼합(mixture-of-experts) 모델을 위한 [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)과 더 높은 처리량을 위한 [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)을 지원합니다. `--enable-expert-parallel`과 `--data-parallel-size`를 실험하여 작업 부하에 가장 적합한 구성을 찾아보세요
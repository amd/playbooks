<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> 이 플레이북은 GitHub에서 렌더링할 수 없는 특수 태그를 사용합니다. 이 콘텐츠를 올바르게 미리 보려면 [amd.com/playbooks](https://amd.com/playbooks)를 방문하세요.
<!-- @github-only:end -->

# RCCL을 사용한 두 Ryzen™ AI Halo 클러스터링

## 개요

Ryzen™ AI Halo는 이미 로컬에서 대규모 언어 모델을 실행할 수 있습니다. 클러스터링은 로컬 네트워크를 통해 여러 시스템의 GPU 메모리를 결합함으로써 이를 한 단계 더 발전시켜, 더 강력한 추론 능력, 향상된 코드 생성, 더 깊은 다국어 이해를 갖춘 훨씬 더 큰 모델에 접근할 수 있게 해줍니다. 이 모든 것이 완전히 자신의 하드웨어에서 이루어집니다.

이 플레이북은 RCCL(ROCm Communication Collectives Library)을 사용하여 두 Ryzen AI Halo 시스템을 클러스터링하고, vLLM과 함께 ROCm 가속을 통해 두 머신에서 3,970억 파라미터 모델인 Qwen3.5-397B를 실행하는 방법을 알려줍니다.

## 학습 내용

- Ryzen AI Halo 시스템에서 VRAM 할당을 확장하는 방법
- ROCm 지원으로 vLLM 실행하기
- 두 Ryzen AI Halo 시스템에서 멀티 노드 텐서 병렬 추론을 위한 RCCL 구성
- 네트워크로 연결된 두 Ryzen AI Halo 시스템에서 3,970억 파라미터 모델 실행하기

## 사전 요구 사항

### 하드웨어

이 플레이북에는 두 대의 Ryzen AI Halo 유닛과 하나의 이더넷 스위치가 필요하며, 각 유닛이 스위치에 직접 연결되는 스타 토폴로지로 구성됩니다.

| 구성 요소 | 수량 | 설명 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 클러스터를 구성하는 컴퓨트 노드 |
| 10Gbps 이더넷 스위치 | 1 | 멀티 노드 Ryzen AI Halo 통신을 위한 중앙 스위치 (최소 2개 포트) |
| 이더넷 케이블 | 2 | 각 Halo 유닛을 스위치에 연결 (Cat 7 이상 권장) |

> **참고**: 두 Ryzen AI Halo 유닛을 연결하려면 이더넷 스위치 포트 두 개가 필요합니다. Halo 유닛 중 하나가 아닌 별도의 클라이언트 머신에서 모델에 접근하는 경우 세 번째 포트가 필요합니다.

### 소프트웨어
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 물리적 하드웨어 설정

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료하세요.

Cat 7(이상) 케이블을 사용하여 각 Ryzen AI Halo 유닛을 이더넷 스위치에 연결합니다. 이를 통해 노드 간 고속 통신에 사용되는 10Gbps 링크가 구성됩니다.

### 1. 네트워크 인터페이스 확인

각 머신에서 네트워크 인터페이스 이름을 찾아 기록해 두세요(이후 지침에서 `IFNAME`으로 참조됩니다). 다음을 실행하세요:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

이 명령은 인터페이스 이름을 직접 출력합니다. 예를 들면:

```bash
enp191s0
```

### 2. 네트워크 링크 속도 확인

인터페이스 속도를 확인하여 링크가 활성화되어 있고 최대 속도로 실행 중인지 확인합니다:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **참고**: `<IFNAME>`을 [1. 네트워크 인터페이스 확인](#1-determine-network-interfaces)에서 출력된 인터페이스 이름으로 교체하세요.

속도가 `10000Mb/s`로 표시되어야 합니다:

```bash
	Speed: 10000Mb/s
```

> **참고**: 속도가 `10000Mb/s`보다 낮거나 링크가 연결되지 않는 경우, 케이블 연결을 확인하고 스위치 포트가 10Gbps로 설정되어 있는지 확인하세요. 일부 스위치는 자동 협상을 비활성화하고 링크 속도를 수동으로 설정해야 할 수 있습니다. 스위치 설명서를 참조하세요.

## VRAM 할당 확장

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료하세요.

### 대규모 모델 실행을 위한 메모리 구성

Linux에서 ROCm은 공유 시스템 메모리 풀을 활용하며, 이 풀은 기본적으로 시스템 메모리의 절반으로 구성됩니다.

다음 지침에 따라 커널의 TTM(Translation Table Manager) 페이지 설정을 변경하여 이 양을 늘릴 수 있습니다. AMD는 BIOS에서 최소 전용 VRAM을 0.5 GB로 설정할 것을 권장합니다.

* pipx 유틸리티를 설치하고 pipx로 설치된 휠의 경로를 시스템 검색 경로에 추가합니다.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* PyPI에서 amd-debug-tools 휠을 설치합니다.
  ```bash
  pipx install amd-debug-tools
  ```

* amd-ttm 도구를 실행하여 공유 메모리의 현재 설정을 조회합니다.
  ```bash
  amd-ttm
  ```

* 공유 메모리 설정을 **120 GB**로 재구성합니다:
  ```bash
  amd-ttm --set 120
  ```

* 변경 사항을 적용하려면 시스템을 재부팅합니다.

## vLLM 컨테이너 초기화

> **참고**: 이 단계는 머신 1과 머신 2 모두에서 완료하세요.

Ryzen AI Halo에는 사전 빌드된 컨테이너 이미지 안에 vLLM이 패키징되어 제공되며, 무료 오픈 소스 컨테이너 도구인 Podman을 사용하여 실행합니다.

### 1. 모델 다운로드 디렉터리 생성

이 플레이북에서 Qwen3.5-397B 모델을 서빙할 때 vLLM이 자동으로 모델 가중치를 시스템에 다운로드합니다. 해당 가중치가 컨테이너 내부에서 접근 가능하도록 컨테이너가 마운트할 수 있는 models 디렉터리를 먼저 생성합니다:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. vLLM 컨테이너 실행

아래 명령은 컨테이너를 실행하고 대화형 셸로 진입합니다. 방금 생성한 models 디렉터리를 마운트하고 `IFNAME`을 `NCCL_SOCKET_IFNAME` 및 `GLOO_SOCKET_IFNAME`에 전달하여, 클러스터 전반의 GPU를 조율하는 데 vLLM이 사용하는 라이브러리인 RCCL에 사용할 인터페이스를 알려줍니다.

다음 명령으로 컨테이너를 시작합니다:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **참고**: `<IFNAME>`을 [1. 네트워크 인터페이스 확인](#1-determine-network-interfaces)에서 출력된 인터페이스 이름으로 교체하세요.

## 클러스터에서 모델 실행

vLLM은 Ray를 사용하여 클러스터를 오케스트레이션하고 RCCL을 사용하여 노드 간 GPU-to-GPU 통신을 처리합니다. 한 머신이 **헤드 노드**(머신 1)로서 추론을 조율하고, 다른 머신은 **워커 노드**(머신 2)로 참여하여 GPU 메모리와 컴퓨팅 자원을 제공합니다.

> **참고**: Ray는 vLLM의 선택적 의존성이며 사전 구성된 Podman 컨테이너 내부에서만 사용할 수 있습니다.

실행 시 vLLM은 텐서 병렬 처리를 사용하여 두 노드에 모델을 분산합니다. 로드가 완료되면 단일 가속기에서 실행하는 것처럼 추론이 진행됩니다.

### 1단계: Ray 헤드 노드 시작 (머신 1)

머신 1에서 Ray 헤드 노드를 시작하여 클러스터를 초기화합니다:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **`<MACHINE_1_IP>` 확인**: 머신 1에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다.

### 2단계: 클러스터 참여 (머신 2)

머신 2에서 헤드 노드에 연결하여 클러스터를 구성합니다:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **`<MACHINE_2_IP>` 확인**: 머신 2에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다.

### 3단계: 모델 서빙 (머신 1)

머신 1에서 vLLM 서버를 실행합니다. 모델이 자동으로 다운로드되고 두 노드에 걸쳐 서빙이 시작됩니다:

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

#### 파라미터 참조

| 플래그 | 목적 |
|------|---------|
| `--port` | HTTP API를 서빙할 포트 |
| `--host` | 서버를 바인딩할 IP 주소 (모든 인터페이스의 경우 `0.0.0.0`) |
| `--max-model-len` | 토큰 단위의 최대 컨텍스트 길이 |
| `--gpu-memory-utilization` | 할당할 GPU 메모리 비율 (0.0–1.0) |
| `--dtype` | 모델 가중치의 데이터 타입 |
| `--tensor-parallel-size` | 모델을 분산할 GPU 수 (클러스터의 총 GPU 수로 설정) |
| `--distributed-executor-backend` | 멀티 노드 실행 백엔드 (클러스터 배포의 경우 `ray`) |
| `--enforce-eager` | 호환성을 위해 CUDA 그래프 컴파일 비활성화 |
| `--language-model-only` | 보조 모델 구성 요소(예: 비전 인코더) 로딩 건너뜀 |
| `--reasoning-parser` | 모델의 구조화된 추론 출력 파싱 활성화 |

전체 파라미터 사용법은 [vLLM 문서](https://docs.vllm.ai/en/latest/configuration/engine_args/)를 참조하세요.

## 모델 접근

vLLM은 OpenAI 호환 API를 제공하므로 호환되는 모든 클라이언트나 인터페이스를 클러스터에 연결할 수 있습니다. 인기 있는 옵션 중 하나는 브라우저 기반 채팅 인터페이스를 제공하는 [Open WebUI](https://github.com/open-webui/open-webui)입니다.

Open WebUI를 vLLM 엔드포인트에 연결하려면:

1. **설정** > **관리자 패널** > **연결**을 엽니다.
2. **OpenAI API 연결 관리**에서 **+**를 클릭합니다.
3. **연결 유형**을 **외부**로 설정합니다.
4. **URL**을 `http://<MACHINE_1_IP>:7000/v1`로 설정합니다.
5. **인증** 아래에서 드롭다운에서 **없음**을 선택합니다.
6. **모델 ID**는 비워 두어 엔드포인트에서 모든 모델을 자동으로 검색합니다.

> **`<MACHINE_1_IP>` 확인**: 머신 1에서 `hostname -I | awk '{print $1}'`을 실행하여 로컬 IP 주소를 확인합니다. 머신 1에서 직접 Open WebUI에 접근하는 경우 `http://localhost:7000/v1`을 사용할 수 있습니다.

![vLLM 엔드포인트에 대한 Open WebUI 연결 설정](assets/openwebui-connection.png)

연결되면 Open WebUI의 모델 드롭다운에서 모델을 선택하고 채팅을 시작합니다. 이제 모델이 두 Ryzen AI Halo 노드에 걸쳐 실행됩니다:

![Open WebUI에서 Qwen3.5-397B와 채팅하기](assets/openwebui-chat.png)

## 다음 단계

- **다른 모델 탐색**: [Hugging Face](https://huggingface.co/models?&sort=trending)에서 클러스터의 결합된 GPU 메모리에 맞는 새로운 모델을 찾아보세요.
- **4개 노드로 확장**: Ryzen AI Halo 시스템 두 대를 추가 Ray 워커로 추가하여 더 많은 GPU에 모델을 분산합니다. 이를 위해서는 각 노드당 하나씩 최소 4개의 포트가 있는 이더넷 스위치가 필요합니다. 각 추가 워커에서 [2단계: 클러스터 참여](#step-2-join-the-cluster-machine-2)를 따르고 `--tensor-parallel-size`를 그에 맞게 늘리세요.
- **다른 병렬 처리 전략 시도**: vLLM은 혼합 전문가 모델을 위한 [전문가 병렬 처리](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)와 더 높은 처리량을 위한 [데이터 병렬 처리](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)를 지원합니다. `--enable-expert-parallel` 및 `--data-parallel-size`를 실험하여 워크로드에 가장 적합한 구성을 찾아보세요.
<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4 툴박스 컨테이너 이미지 받아오기

`ds4-cockpit`은 컨테이너 툴박스 내부에서 ds4 추론 엔진을 실행합니다. **Interactive Toolboxes** 탭에서 사용 가능한 최신 툴박스(예: `ds4-rocm-7.2.4`)를 선택한 다음 **Create/Update**를 클릭하여 이미지를 받아옵니다.

대신 이미지를 직접 받아오려면:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

툴박스 버전은 시간이 지나면서 변경되므로, 아래의 확인 작업은 고정된 태그가 아닌 이미지 패밀리를 기준으로 일치시킵니다.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->
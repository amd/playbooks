<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Traducción automática.** Esta página fue traducida automáticamente del inglés y no ha sido revisada por un humano. Puede contener errores, y ciertas instrucciones, comandos, descargas, disponibilidad de productos u otro contenido pueden variar según el idioma o la región. En caso de cualquier incoherencia o discrepancia, la versión original en inglés del playbook prevalecerá y será la que rija.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Cómo agrupar dos Ryzen™ AI Halo con RCCL

## Descripción general

Tu Ryzen™ AI Halo ya es capaz de ejecutar modelos de lenguaje grandes de forma local. La agrupación en clúster lleva esto un paso más allá, combinando la memoria GPU de múltiples sistemas a través de una red local, dándote acceso a modelos aún más grandes con razonamiento más sólido, mejor generación de código y una comprensión multilingüe más profunda, todo completamente en tu propio hardware.

Este playbook te enseña cómo agrupar en clúster dos sistemas Ryzen AI Halo usando RCCL (ROCm Communication Collectives Library) con vLLM y ejecutar Qwen3.5-397B, un modelo de 397B parámetros, en ambas máquinas con aceleración ROCm.

## Qué aprenderás

- Cómo extender la asignación de VRAM en sistemas Ryzen AI Halo
- Cómo lanzar vLLM con soporte ROCm
- Cómo configurar RCCL para inferencia con paralelismo tensorial multi-nodo entre dos sistemas Ryzen AI Halo
- Cómo ejecutar un modelo de 397B parámetros en dos sistemas Ryzen AI Halo conectados en red

## Requisitos previos

### Hardware

Este playbook requiere dos unidades Ryzen AI Halo y un switch Ethernet, conectados en una topología en estrella con cada unidad conectada directamente al switch.

| Componente | Cantidad | Descripción |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodos de cómputo que forman el clúster |
| Switch Ethernet de 10Gbps | 1 | Switch central que permite la comunicación multi-nodo de Ryzen AI Halo (al menos 2 puertos) |
| Cable Ethernet | 2 | Conecta cada unidad Halo al switch (se recomienda Cat 7 o superior) |

> **Nota**: Se requieren dos puertos del switch Ethernet para conectar las dos unidades Ryzen AI Halo. Se requiere un tercer puerto si accedes al modelo desde una máquina cliente separada en lugar de hacerlo desde una de las unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuración física del hardware

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Conecta cada unidad Ryzen AI Halo al switch Ethernet usando un cable Cat 7 (o superior). Esto establece el enlace de 10Gbps utilizado para la comunicación de alta velocidad entre los nodos.

### 1. Determinar las interfaces de red

En cada máquina, encuentra el nombre de su interfaz de red y anótalo (se hará referencia a él en el resto de las instrucciones como `IFNAME`). Ejecuta:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Esto imprime el nombre de la interfaz directamente, por ejemplo:

```bash
enp191s0
```

### 2. Verificar las velocidades del enlace de red

Confirma que el enlace esté activo y funcionando a velocidad máxima verificando la velocidad de tu interfaz:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz de salida obtenido en [1. Determinar las interfaces de red](#1-determinar-las-interfaces-de-red)

Deberías ver una velocidad de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Si la velocidad es menor que `10000Mb/s` o el enlace no se activa, revisa la conexión del cable y confirma que el puerto del switch esté configurado a 10Gbps. Algunos switches requieren que se desactive la auto-negociación y se establezca la velocidad del enlace manualmente; consulta la documentación de tu switch.

## Extensión de la asignación de VRAM

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

### Configuración de memoria para ejecutar modelos grandes

En Linux, ROCm utiliza un grupo de memoria del sistema compartido, y este grupo está configurado de forma predeterminada a la mitad de la memoria del sistema.

Esta cantidad se puede aumentar cambiando la configuración de páginas del Translation Table Manager (TTM) del kernel, con las siguientes instrucciones. AMD recomienda establecer el mínimo de VRAM dedicada en el BIOS (0.5 GB).

* Instala la utilidad pipx y agrega la ruta para los wheels instalados por pipx a la ruta de búsqueda del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instala el wheel amd-debug-tools desde PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Ejecuta la herramienta amd-ttm para consultar la configuración actual de la memoria compartida.
  ```bash
  amd-ttm
  ```

* Reconfigura la configuración de memoria compartida a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reinicia el sistema para que los cambios surtan efecto.

## Inicialización del contenedor vLLM

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Tu Ryzen AI Halo viene con vLLM empaquetado dentro de una imagen de contenedor prediseñada, que ejecutas usando Podman, una herramienta de contenedores gratuita y de código abierto.

### 1. Crear el directorio de descarga del modelo

Cuando sirvas el modelo Qwen3.5-397B en este playbook, vLLM descargará automáticamente los pesos del modelo a tu sistema. Para asegurarte de que esos pesos sean accesibles desde dentro del contenedor, primero crea un directorio de modelos que el contenedor pueda montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lanzar el contenedor vLLM

El siguiente comando lanza el contenedor y te coloca en un shell interactivo. Monta el directorio de modelos que acabas de crear y pasa tu `IFNAME` a `NCCL_SOCKET_IFNAME` y `GLOO_SOCKET_IFNAME`, indicándole a RCCL (la biblioteca que usa vLLM para coordinar las GPU en todo el clúster) qué interfaz utilizar.

Inicia el contenedor con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz de salida obtenido en [1. Determinar las interfaces de red](#1-determinar-las-interfaces-de-red)

## Ejecución del modelo en el clúster

vLLM usa Ray para orquestar el clúster y RCCL para manejar la comunicación GPU a GPU entre nodos. Una máquina actúa como el **nodo principal** (Máquina 1), coordinando la inferencia. La otra se une como **nodo trabajador** (Máquina 2), aportando su memoria GPU y capacidad de cómputo.

> **Nota**: Ray es una dependencia opcional para vLLM y solo está disponible desde dentro del contenedor Podman preconfigurado.

Al iniciar, vLLM fragmenta el modelo entre ambos nodos usando paralelismo tensorial. Una vez cargado, la inferencia procede como si se ejecutara en un solo acelerador.

### Paso 1: Iniciar el nodo principal de Ray (Máquina 1)

En la Máquina 1, inicia el nodo principal de Ray para inicializar el clúster:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Cómo encontrar `<MACHINE_1_IP>`**: En la Máquina 1, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.
### Paso 2: Unirse al clúster (Máquina 2)

En la Máquina 2, conéctate al nodo principal para formar el clúster:

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Cómo encontrar `<MACHINE_2_IP>`**: En la Máquina 2, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.

### Paso 3: Servir el modelo (Máquina 1)

En la Máquina 1, inicia el servidor vLLM. Esto descargará automáticamente el modelo y comenzará a servirlo en ambos nodos:

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

#### Referencia de parámetros

| Flag | Propósito |
|------|-----------|
| `--port` | Puerto en el que se sirve la API HTTP |
| `--host` | Dirección IP a la que se vincula el servidor (`0.0.0.0` para todas las interfaces) |
| `--max-model-len` | Longitud máxima de contexto en tokens |
| `--gpu-memory-utilization` | Fracción de memoria GPU a asignar (0.0–1.0) |
| `--dtype` | Tipo de dato para los pesos del modelo |
| `--tensor-parallel-size` | Cantidad de GPUs entre las que se fragmenta el modelo (configúralo con el total de GPUs en el clúster) |
| `--distributed-executor-backend` | Backend para la ejecución multinodo (`ray` para implementaciones en clúster) |
| `--enforce-eager` | Deshabilita la compilación de CUDA graph para compatibilidad |
| `--language-model-only` | Omite la carga de componentes auxiliares del modelo (por ejemplo, el codificador de visión) |
| `--reasoning-parser` | Habilita el análisis estructurado de salida de razonamiento para el modelo |

Para conocer el uso completo de los parámetros, consulta la [documentación de vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Acceso al modelo

vLLM expone una API compatible con OpenAI, por lo que puedes conectar cualquier cliente o interfaz compatible a tu clúster. Una opción popular es [Open WebUI](https://github.com/open-webui/open-webui), que ofrece una interfaz de chat basada en el navegador.

Para conectar Open WebUI a tu endpoint de vLLM:

1. Abre **Settings** > **Admin Panel** > **Connections**
2. Haz clic en el **+** en **Manage OpenAI API Connections**
3. Configura el **Connection Type** como **External**
4. Configura la **URL** como `http://<MACHINE_1_IP>:7000/v1`
5. En **Auth**, selecciona **None** en el menú desplegable
6. Deja **Model IDs** vacío para descubrir automáticamente todos los modelos del endpoint

> **Cómo encontrar `<MACHINE_1_IP>`**: En la Máquina 1, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local. Si accedes a Open WebUI desde la propia Máquina 1, puedes usar `http://localhost:7000/v1`.

![Configuración de conexión de Open WebUI para el endpoint de vLLM](assets/openwebui-connection.png)

Una vez conectado, selecciona el modelo en el menú desplegable de modelos de Open WebUI y comienza a chatear. El modelo ahora se está ejecutando en ambos nodos Ryzen AI Halo:

![Chateando con Qwen3.5-397B en Open WebUI](assets/openwebui-chat.png)

## Próximos pasos

- **Explora otros modelos**: Descubre nuevos modelos en [Hugging Face](https://huggingface.co/models?&sort=trending) que se ajusten a la memoria GPU combinada de tu clúster
- **Escala a cuatro nodos**: Agrega dos sistemas Ryzen AI Halo más como workers de Ray adicionales para fragmentar modelos entre incluso más GPUs. Esto requiere un switch Ethernet con al menos cuatro puertos, uno para cada nodo. Sigue el [Paso 2: Unirse al clúster](#step-2-join-the-cluster-machine-2) en cada worker adicional y aumenta `--tensor-parallel-size` en consecuencia
- **Prueba otras estrategias de paralelismo**: vLLM admite [paralelismo de expertos](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos de mezcla de expertos (mixture-of-experts) y [paralelismo de datos](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para mayor rendimiento. Experimenta con `--enable-expert-parallel` y `--data-parallel-size` para encontrar la mejor configuración para tu carga de trabajo
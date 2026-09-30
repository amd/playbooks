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

# Clustering de Dos Ryzen™ AI Halo con RCCL

## Descripción General

Tu Ryzen™ AI Halo ya es capaz de ejecutar modelos de lenguaje grandes de forma local. El clustering lleva esto más allá al combinar la memoria de la GPU de múltiples sistemas a través de una red local, brindándote acceso a modelos aún más grandes con razonamiento más sólido, mejor generación de código y una comprensión multilingüe más profunda, todo completamente en tu propio hardware.

Este playbook te enseña cómo agrupar dos sistemas Ryzen AI Halo utilizando RCCL (ROCm Communication Collectives Library) con vLLM y ejecutar Qwen3.5-397B, un modelo de 397 mil millones de parámetros, en ambas máquinas con aceleración de ROCm.

## Qué Aprenderás

- Cómo extender la asignación de VRAM en sistemas Ryzen AI Halo
- Cómo iniciar vLLM con soporte de ROCm
- Cómo configurar RCCL para inferencia con paralelismo tensorial multi-nodo en dos sistemas Ryzen AI Halo
- Cómo ejecutar un modelo de 397 mil millones de parámetros en dos sistemas Ryzen AI Halo conectados en red

## Requisitos Previos

### Hardware

Este playbook requiere dos unidades Ryzen AI Halo y un switch Ethernet, conectados en una topología en estrella con cada unidad cableada directamente al switch.

| Componente | Cantidad | Descripción |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodos de cómputo que conforman el clúster |
| Switch Ethernet de 10Gbps | 1 | Switch central que permite la comunicación multi-nodo entre unidades Ryzen AI Halo (al menos 2 puertos) |
| Cable Ethernet | 2 | Conecta cada unidad Halo al switch (se recomienda Cat 7 o superior) |

> **Nota**: Se requieren dos puertos del switch Ethernet para conectar las dos unidades Ryzen AI Halo. Se requiere un tercer puerto si accedes al modelo desde una máquina cliente separada en lugar de hacerlo desde una de las unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuración Física del Hardware

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Conecta cada unidad Ryzen AI Halo al switch Ethernet utilizando un cable Cat 7 (o superior). Esto establece el enlace de 10Gbps utilizado para la comunicación de alta velocidad entre los nodos.

### 1. Determinar las Interfaces de Red

En cada máquina, encuentra el nombre de su interfaz de red y anótalo (se hará referencia a él en el resto de las instrucciones como `IFNAME`). Ejecuta:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

Esto imprime el nombre de la interfaz directamente, por ejemplo:

```bash
enp191s0
```

### 2. Verificar las Velocidades del Enlace de Red

Confirma que el enlace esté activo y funcionando a máxima velocidad revisando la velocidad de tu interfaz:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz obtenido en [1. Determinar las Interfaces de Red](#1-determine-network-interfaces)

Deberías ver una velocidad de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Si la velocidad es menor que `10000Mb/s` o el enlace no se activa, verifica la conexión del cable y confirma que el puerto del switch esté configurado en 10Gbps. Algunos switches requieren que la negociación automática esté deshabilitada y que la velocidad del enlace se configure manualmente; consulta la documentación de tu switch.

## Extendiendo la Asignación de VRAM

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

### Configuración de Memoria para Ejecutar Modelos Grandes

En Linux, ROCm utiliza un pool de memoria compartida del sistema, y este pool está configurado por defecto a la mitad de la memoria del sistema.

Esta cantidad puede aumentarse cambiando la configuración de páginas del Translation Table Manager (TTM) del kernel, siguiendo las siguientes instrucciones. AMD recomienda establecer la VRAM dedicada mínima en el BIOS (0.5 GB).

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

## Inicialización del Contenedor vLLM

> **Nota**: Completa este paso tanto en la Máquina 1 como en la Máquina 2.

Tu Ryzen AI Halo viene con vLLM empaquetado dentro de una imagen de contenedor preconstruida, que ejecutas usando Podman, una herramienta de contenedores gratuita y de código abierto.

### 1. Crear el Directorio de Descarga del Modelo

Cuando sirvas el modelo Qwen3.5-397B en este playbook, vLLM descargará automáticamente los pesos del modelo a tu sistema. Para asegurarte de que esos pesos sean accesibles desde dentro del contenedor, primero crea un directorio de modelos que el contenedor pueda montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Iniciar el Contenedor vLLM

El siguiente comando inicia el contenedor y te coloca en una shell interactiva. Monta el directorio de modelos que acabas de crear y pasa tu `IFNAME` a `NCCL_SOCKET_IFNAME` y `GLOO_SOCKET_IFNAME`, indicándole a RCCL (la biblioteca que vLLM utiliza para coordinar las GPU a través del clúster) qué interfaz usar.

Inicia el contenedor con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz obtenido en [1. Determinar las Interfaces de Red](#1-determine-network-interfaces)

## Ejecutando el Modelo en el Clúster

vLLM utiliza Ray para orquestar el clúster y RCCL para manejar la comunicación GPU a GPU entre nodos. Una máquina actúa como el **nodo principal** (Máquina 1), coordinando la inferencia. La otra se une como un **nodo trabajador** (Máquina 2), contribuyendo con su memoria de GPU y capacidad de cómputo.

> **Nota**: Ray es una dependencia opcional para vLLM y solo está disponible desde dentro del contenedor Podman preconfigurado.

Al iniciar, vLLM fragmenta el modelo entre ambos nodos utilizando paralelismo tensorial. Una vez cargado, la inferencia procede como si se ejecutara en un solo acelerador.

#### Previniendo Errores de OOM en Ray

Por defecto, Ray monitorea la memoria del host en cada nodo y termina el proceso más grande cuando el uso de memoria supera el 95%. En tu Ryzen™ AI Halo, la GPU y el host comparten un mismo pool de memoria, por lo que cargar un modelo puede desencadenar un `ray.exceptions.OutOfMemoryError` y terminar el proceso trabajador.

Para evitar esto, exportaremos `RAY_memory_monitor_refresh_ms=0` en cada máquina antes de iniciar y unirse al clúster.
### Paso 1: Iniciar el nodo principal de Ray (Máquina 1)

En la Máquina 1, inicie el nodo principal de Ray para inicializar el clúster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **Cómo encontrar `<MACHINE_1_IP>`**: En la Máquina 1, ejecute `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.

### Paso 2: Unirse al clúster (Máquina 2)

En la Máquina 2, conéctese al nodo principal para formar el clúster:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **Cómo encontrar `<MACHINE_2_IP>`**: En la Máquina 2, ejecute `hostname -I | awk '{print $1}'` para encontrar su dirección IP local.

### Paso 3: Servir el modelo (Máquina 1)

En la Máquina 1, inicie el servidor vLLM. Esto descargará automáticamente el modelo y comenzará a servirlo en ambos nodos:

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

| Indicador | Propósito |
|------|---------|
| `--port` | Puerto en el que se sirve la API HTTP |
| `--host` | Dirección IP a la que se vincula el servidor (`0.0.0.0` para todas las interfaces) |
| `--max-model-len` | Longitud máxima de contexto en tokens |
| `--gpu-memory-utilization` | Fracción de memoria de GPU a asignar (0.0–1.0) |
| `--dtype` | Tipo de datos para los pesos del modelo |
| `--tensor-parallel-size` | Número de GPU entre las cuales fragmentar el modelo (configúrelo con el total de GPU en el clúster) |
| `--distributed-executor-backend` | Backend para ejecución multinodo (`ray` para implementaciones en clúster) |
| `--enforce-eager` | Deshabilita la compilación de gráficos CUDA por compatibilidad |
| `--language-model-only` | Omite la carga de componentes auxiliares del modelo (por ejemplo, el codificador de visión) |
| `--reasoning-parser` | Habilita el análisis estructurado de la salida de razonamiento para el modelo |

Para conocer el uso completo de los parámetros, consulte la [documentación de vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Acceso al modelo

vLLM expone una API compatible con OpenAI, por lo que puede conectar cualquier cliente o interfaz compatible a su clúster. Una opción popular es [Open WebUI](https://github.com/open-webui/open-webui), que ofrece una interfaz de chat basada en navegador.

Para conectar Open WebUI a su endpoint de vLLM:

1. Abra **Settings** > **Admin Panel** > **Connections**
2. Haga clic en el **+** en **Manage OpenAI API Connections**
3. Configure el **Connection Type** como **External**
4. Configure la **URL** como `http://<MACHINE_1_IP>:7000/v1`
5. En **Auth**, seleccione **None** en el menú desplegable
6. Deje **Model IDs** vacío para descubrir automáticamente todos los modelos del endpoint

> **Cómo encontrar `<MACHINE_1_IP>`**: En la Máquina 1, ejecute `hostname -I | awk '{print $1}'` para encontrar su dirección IP local. Si accede a Open WebUI desde la propia Máquina 1, puede usar `http://localhost:7000/v1`.

![Configuración de conexión de Open WebUI para el endpoint de vLLM](assets/openwebui-connection.png)

Una vez conectado, seleccione el modelo en el menú desplegable de modelos en Open WebUI y comience a chatear. Ahora el modelo se ejecuta en ambos nodos Ryzen AI Halo:

![Chateando con Qwen3.5-397B en Open WebUI](assets/openwebui-chat.png)

## Próximos pasos

- **Explore otros modelos**: Descubra nuevos modelos en [Hugging Face](https://huggingface.co/models?&sort=trending) que se ajusten a la memoria de GPU combinada de su clúster
- **Escale a cuatro nodos**: Agregue dos sistemas Ryzen AI Halo adicionales como workers de Ray adicionales para fragmentar modelos entre aún más GPU. Esto requiere un switch Ethernet con al menos cuatro puertos, uno por cada nodo. Siga el [Paso 2: Unirse al clúster](#step-2-join-the-cluster-machine-2) en cada worker adicional y aumente `--tensor-parallel-size` en consecuencia
- **Pruebe otras estrategias de paralelismo**: vLLM admite [expert parallel](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos de mezcla de expertos y [data parallel](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para un mayor rendimiento. Experimente con `--enable-expert-parallel` y `--data-parallel-size` para encontrar la mejor configuración para su carga de trabajo
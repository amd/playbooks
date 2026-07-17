<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# Agrupando dos Ryzen™ AI Halos con RCCL

## Descripción general

Tu Ryzen™ AI Halo ya es capaz de ejecutar modelos de lenguaje grandes de forma local. La agrupación va más allá al combinar la memoria GPU de múltiples sistemas a través de una red local, dándote acceso a modelos aún más grandes con razonamiento más sólido, mejor generación de código y comprensión multilingüe más profunda, todo completamente en tu propio hardware.

Este playbook te enseña cómo agrupar dos sistemas Ryzen AI Halo usando RCCL (ROCm Communication Collectives Library) con vLLM y ejecutar Qwen3.5-397B, un modelo de 397B parámetros, en ambas máquinas con aceleración ROCm.

## Lo que aprenderás

- Cómo extender la asignación de VRAM en sistemas Ryzen AI Halo
- Cómo lanzar vLLM con soporte ROCm
- Cómo configurar RCCL para inferencia tensor-paralela multinodo en dos sistemas Ryzen AI Halo
- Cómo ejecutar un modelo de 397B parámetros en dos sistemas Ryzen AI Halo conectados en red

## Requisitos previos

### Hardware

Este playbook requiere dos unidades Ryzen AI Halo y un switch Ethernet, conectados en topología estrella con cada unidad cableada directamente al switch.

| Componente | Cantidad | Descripción |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | Nodos de cómputo que forman el clúster |
| Switch Ethernet 10Gbps | 1 | Switch central para permitir la comunicación multinodo entre Ryzen AI Halo (al menos 2 puertos) |
| Cable Ethernet | 2 | Conecta cada unidad Halo al switch (se recomienda Cat 7 o superior) |

> **Nota**: Se requieren dos puertos del switch Ethernet para conectar las dos unidades Ryzen AI Halo. Se necesita un tercer puerto si accedes al modelo desde una máquina cliente separada en lugar de hacerlo desde una de las unidades Halo.

### Software
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## Configuración física del hardware

> **Nota**: Completa este paso en la Máquina 1 y en la Máquina 2.

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

Confirma que el enlace está activo y funcionando a plena velocidad verificando la velocidad de tu interfaz:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz obtenido en [1. Determinar las interfaces de red](#1-determine-network-interfaces)

Deberías ver una velocidad de `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **Nota**: Si la velocidad es inferior a `10000Mb/s` o el enlace no se establece, verifica la conexión del cable y confirma que el puerto del switch esté configurado a 10Gbps. Algunos switches requieren deshabilitar la autonegociación y configurar la velocidad del enlace manualmente; consulta la documentación de tu switch.

## Extender la asignación de VRAM

> **Nota**: Completa este paso en la Máquina 1 y en la Máquina 2.

### Configuración de memoria para ejecutar modelos grandes

En Linux, ROCm utiliza un grupo de memoria del sistema compartido, y este grupo está configurado por defecto a la mitad de la memoria del sistema.

Esta cantidad puede aumentarse cambiando la configuración de páginas del Translation Table Manager (TTM) del kernel, siguiendo las instrucciones a continuación. AMD recomienda establecer la VRAM dedicada mínima en el BIOS (0.5 GB).

* Instala la utilidad pipx y agrega la ruta de las ruedas instaladas por pipx al path de búsqueda del sistema.

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* Instala la rueda amd-debug-tools desde PyPI.
  ```bash
  pipx install amd-debug-tools
  ```

* Ejecuta la herramienta amd-ttm para consultar la configuración actual de la memoria compartida.
  ```bash
  amd-ttm
  ```

* Reconfigura los ajustes de memoria compartida a **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* Reinicia el sistema para que los cambios surtan efecto.

## Inicialización del contenedor vLLM

> **Nota**: Completa este paso en la Máquina 1 y en la Máquina 2.

Tu Ryzen AI Halo incluye vLLM empaquetado dentro de una imagen de contenedor precompilada, que ejecutas usando Podman, una herramienta de contenedores gratuita y de código abierto.

### 1. Crear el directorio de descarga de modelos

Cuando sirvas el modelo Qwen3.5-397B en este playbook, vLLM descargará automáticamente los pesos del modelo en tu sistema. Para asegurarte de que esos pesos sean accesibles desde dentro del contenedor, primero crea un directorio de modelos que el contenedor pueda montar:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. Lanzar el contenedor vLLM

El comando a continuación lanza el contenedor y te lleva a un shell interactivo. Monta el directorio de modelos que acabas de crear y pasa tu `IFNAME` a `NCCL_SOCKET_IFNAME` y `GLOO_SOCKET_IFNAME`, indicándole a RCCL (la biblioteca que vLLM usa para coordinar los GPU del clúster) qué interfaz utilizar.

Inicia el contenedor con:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **Nota**: Reemplaza `<IFNAME>` con el nombre de la interfaz obtenido en [1. Determinar las interfaces de red](#1-determine-network-interfaces)

## Ejecutar el modelo en el clúster

vLLM usa Ray para orquestar el clúster y RCCL para gestionar la comunicación GPU a GPU entre nodos. Una máquina actúa como **nodo principal** (Máquina 1), coordinando la inferencia. La otra se une como **nodo trabajador** (Máquina 2), aportando su memoria GPU y capacidad de cómputo.

> **Nota**: Ray es una dependencia opcional de vLLM y solo está disponible desde dentro del contenedor Podman preconfigurado.

Al iniciarse, vLLM fragmenta el modelo en ambos nodos usando paralelismo tensorial. Una vez cargado, la inferencia procede como si se ejecutara en un único acelerador.

### Paso 1: Iniciar el nodo principal Ray (Máquina 1)

En la Máquina 1, inicia el nodo principal Ray para inicializar el clúster:

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

En la Máquina 1, lanza el servidor vLLM. Esto descargará automáticamente el modelo y comenzará a servirlo en ambos nodos:

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
|------|---------|
| `--port` | Puerto en el que se sirve la API HTTP |
| `--host` | Dirección IP a la que se vincula el servidor (`0.0.0.0` para todas las interfaces) |
| `--max-model-len` | Longitud máxima de contexto en tokens |
| `--gpu-memory-utilization` | Fracción de memoria GPU a asignar (0.0–1.0) |
| `--dtype` | Tipo de dato para los pesos del modelo |
| `--tensor-parallel-size` | Número de GPU entre los que se fragmenta el modelo (establecer al total de GPU en el clúster) |
| `--distributed-executor-backend` | Backend para la ejecución multinodo (`ray` para despliegues en clúster) |
| `--enforce-eager` | Deshabilita la compilación de grafos CUDA para compatibilidad |
| `--language-model-only` | Omite la carga de componentes auxiliares del modelo (p. ej., codificador de visión) |
| `--reasoning-parser` | Habilita el análisis estructurado de salida de razonamiento para el modelo |

Para el uso completo de parámetros, consulta la [documentación de vLLM](https://docs.vllm.ai/en/latest/configuration/engine_args/).

## Acceder al modelo

vLLM expone una API compatible con OpenAI, por lo que puedes conectar cualquier cliente o interfaz compatible a tu clúster. Una opción popular es [Open WebUI](https://github.com/open-webui/open-webui), que proporciona una interfaz de chat basada en navegador.

Para conectar Open WebUI a tu endpoint de vLLM:

1. Abre **Configuración** > **Panel de administración** > **Conexiones**
2. Haz clic en **+** en **Administrar conexiones de API de OpenAI**
3. Establece el **Tipo de conexión** en **Externo**
4. Establece la **URL** en `http://<MACHINE_1_IP>:7000/v1`
5. En **Autenticación**, selecciona **Ninguna** del menú desplegable
6. Deja **IDs de modelo** vacío para descubrir automáticamente todos los modelos del endpoint

> **Cómo encontrar `<MACHINE_1_IP>`**: En la Máquina 1, ejecuta `hostname -I | awk '{print $1}'` para encontrar su dirección IP local. Si accedes a Open WebUI desde la propia Máquina 1, puedes usar `http://localhost:7000/v1`.

![Configuración de conexión de Open WebUI para el endpoint de vLLM](assets/openwebui-connection.png)

Una vez conectado, selecciona el modelo en el menú desplegable de modelos de Open WebUI y comienza a chatear. El modelo ahora se ejecuta en ambos nodos Ryzen AI Halo:

![Chateando con Qwen3.5-397B en Open WebUI](assets/openwebui-chat.png)

## Próximos pasos

- **Explorar otros modelos**: Descubre nuevos modelos en [Hugging Face](https://huggingface.co/models?&sort=trending) que quepan dentro de la memoria GPU combinada de tu clúster
- **Escalar a cuatro nodos**: Agrega dos sistemas Ryzen AI Halo adicionales como trabajadores Ray adicionales para fragmentar los modelos en aún más GPU. Esto requiere un switch Ethernet con al menos cuatro puertos, uno por cada nodo. Sigue el [Paso 2: Unirse al clúster](#step-2-join-the-cluster-machine-2) en cada trabajador adicional y aumenta `--tensor-parallel-size` en consecuencia
- **Probar otras estrategias de paralelismo**: vLLM admite [paralelismo de expertos](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/) para modelos de mezcla de expertos y [paralelismo de datos](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/) para mayor rendimiento. Experimenta con `--enable-expert-parallel` y `--data-parallel-size` para encontrar la mejor configuración para tu carga de trabajo
# Local Perception Capability with CVML SDK

## Overview

The [Ryzen AI CVML Library](https://ryzenai.docs.amd.com/en/latest/ryzen_ai_libraries.html#ryzen-ai-cvml-library) is AMD's C++ computer vision and machine learning toolkit that provides powerful, on-device perception capabilities — including depth estimation, face detection, and face mesh tracking. Built on top of the Ryzen AI drivers, the library automatically selects the best available hardware (GPU or NPU) for inference, letting you add AI features to C++ applications without worrying about model training or framework integration. All processing happens locally on your STX Halo™ system, making it ideal for privacy-sensitive, low-latency applications.

This playbook teaches you how to set up the Ryzen AI CVML Library, build the included sample applications, and run face detection on a sample video.

## What You'll Learn

- How to install prerequisites and set up the Ryzen AI CVML Library on your STX Halo™ system
- How the CVML C++ API works: contexts, feature objects, and image buffers
- How to build and run the included sample applications using CMake and OpenCV
- How to run face detection on an image with bounding boxes and landmarks
- How to integrate CVML features into your own C++ applications

## Prerequisites

Before starting, ensure you have the following:

- [OpenCV 4.11](https://opencv.org/) downloaded and available on your system
- CMake installed and available in your system PATH

<!-- @require:driver -->

<!-- @os:windows -->
- [AMD Ryzen AI NPU driver](https://ryzenai.docs.amd.com/en/latest/inst.html)
- [Visual Studio 2022](https://visualstudio.microsoft.com/) with the "Desktop development with C++" workload (includes MSVC compiler, Windows SDK, and C++ build tools)
<!-- @os:end -->

<!-- @os:linux -->
- Ubuntu 22.04 or 24.04 (kernel >= 6.11.0-21-generic)
- [AMD Ryzen AI NPU driver](https://ryzenai.docs.amd.com/en/latest/inst.html)
- Vulkan SDK
<!-- @os:end -->

## Setting Up the CVML Library

Clone the Ryzen AI Software repository to get the CVML Library:

```bash
git clone https://github.com/amd/RyzenAI-SW.git
cd RyzenAI-SW/Ryzen-AI-CVML-Library
```

The library package contains the following structure:

| Folder | Contents |
|--------|----------|
| `cmake/` | Packaging info for CMake's `find_package` function |
| `include/` | C++ header files (`cvml-depth-estimation.h`, `cvml-face-detector.h`, `cvml-face-mesh.h`, etc.) |
| `windows/` | Binary files for Windows (compile-time `.LIB` and runtime `.DLL`/`.GRAPHLIB`/`.AMODEL` files) |
| `linux/` | Binary files for Linux (compile and runtime `.SO` files) |
| `samples/` | Individual sample applications with source code |

<!-- @os:linux -->

### Linux-Specific Setup

Install the Vulkan SDK:

```bash
UBUNTU_CODENAME=$(. /etc/os-release; echo "$UBUNTU_CODENAME")
wget -qO- https://packages.lunarg.com/lunarg-signing-key-pub.asc | sudo tee /etc/apt/trusted.gpg.d/lunarg.asc
sudo wget -qO /etc/apt/sources.list.d/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list https://packages.lunarg.com/vulkan/1.3.296/lunarg-vulkan-1.3.296-$UBUNTU_CODENAME.list
sudo apt update
sudo apt install vulkan-sdk
```

If you are running Ubuntu 22.04, also update the MESA Vulkan drivers:

```bash
sudo add-apt-repository ppa:kisak/kisak-mesa -y
sudo apt update && sudo apt upgrade
```

<!-- @os:end -->

## Core Concepts

The CVML Library provides a simple C++ API where each perception feature (depth estimation, face detection, face mesh) has its own header file and feature object. You don't work with raw models — the library handles model loading, preprocessing, and inference automatically.

### Available Features

| Feature | Header File | Description |
|---------|------------|-------------|
| **Depth Estimation** | `cvml-depth-estimation.h` | Generates per-pixel depth maps from RGB images |
| **Face Detection** | `cvml-face-detector.h` | Detects faces with bounding boxes, landmarks (eyes, nose, mouth), and confidence scores |
| **Face Mesh** | `cvml-face-mesh.h` | Tracks detailed facial geometry with dense mesh points |

### Programming Model

Every CVML application follows the same four-step pattern:

1. **Create a Context** — The `amd::cvml::Context` manages shared resources like logging and inference backend selection.
2. **Create a Feature Object** — Instantiate the specific feature (e.g., `amd::cvml::DepthEstimation`) against the context.
3. **Wrap Input Data** — Use `amd::cvml::Image` to encapsulate your RGB image buffer without copying data.
4. **Execute** — Call the feature's processing method and read the results.

```cpp
// Step 1: Create context
auto context = amd::cvml::CreateContext();

// Step 2: Create feature object
amd::cvml::DepthEstimation depth_estimation(context);

// Step 3: Wrap input image (RGB, uint8, no copy)
amd::cvml::Image input(amd::cvml::Image::Format::kRGB,
                       amd::cvml::Image::DataType::kUint8,
                       width, height, data_pointer);

// Step 4: Execute
amd::cvml::Image output(amd::cvml::Image::Format::kGrayScale,
                        amd::cvml::Image::DataType::kFloat32,
                        width, height, nullptr);
depth_estimation.GenerateDepthMap(input, &output);

// Cleanup
context->Release();
```

### Inference Backend

The library automatically selects the best hardware (GPU or NPU) for each operation. You can also set the backend explicitly:

```cpp
// Let the library choose the best hardware (default)
context->SetInferenceBackend(amd::cvml::Context::InferenceBackend::AUTO);
```

> **Note:** Features that use the ONNX backend for NPU operations may experience longer startup latency on the first run. Subsequent runs will be faster.

## Building the Sample Applications

The CVML Library includes ready-to-build sample applications for each feature. Let's build them all at once.

1. Set the `OPENCV_INSTALL_ROOT` environment variable to point to your OpenCV installation:

   <!-- @os:windows -->
   ```cmd
   set OPENCV_INSTALL_ROOT=C:\path\to\opencv
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   export OPENCV_INSTALL_ROOT=/path/to/opencv
   ```
   <!-- @os:end -->

2. Build the samples with CMake:

   <!-- @os:windows -->
   ```cmd
   cd samples
   mkdir build
   cmake -S %CD% -B %CD%\build -DOPENCV_INSTALL_ROOT=%OPENCV_INSTALL_ROOT%
   cmake --build %CD%\build --config Release
   ```
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   cd samples
   mkdir build
   cmake -S $PWD -B $PWD/build -DOPENCV_INSTALL_ROOT=$OPENCV_INSTALL_ROOT
   cmake --build $PWD/build --config Release
   ```
   <!-- @os:end -->

3. Before running any sample, ensure the CVML runtime files are accessible:

   <!-- @os:windows -->
   Either copy the `.DLL` and `.GRAPHLIB` files from the `windows/` folder into the same directory as the built executables, or add the `windows/` folder to your `PATH` environment variable.
   <!-- @os:end -->

   <!-- @os:linux -->
   ```bash
   export LD_LIBRARY_PATH=/path/to/Ryzen-AI-CVML-Library/linux:$LD_LIBRARY_PATH
   export LD_LIBRARY_PATH=/opt/xilinx/xrt/lib:$LD_LIBRARY_PATH
   ```
   <!-- @os:end -->

## Running Face Detection

The face detection sample detects faces in an image, video, or live camera feed. It draws bounding boxes, confidence scores, and five facial landmarks (two eyes, nose, and two mouth edges) on each detected face.

First, download a sample image to use as input (photo by [SHVETS production](https://www.pexels.com/photo/young-woman-filming-video-in-light-apartment-7516247/), free to use via Pexels):

```bash
curl -L -o sample_face.jpg "https://images.pexels.com/photos/7516247/pexels-photo-7516247.jpeg?cs=srgb&dl=pexels-shvets-production-7516247.jpg&fm=jpg"
```

**Run face detection on the sample image:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg
```
<!-- @os:end -->

A window will appear showing the image with a green bounding box around the detected face, a yellow confidence score, and red landmark dots (eyes, nose, mouth edges).

**Save the annotated output to a file:**

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -o output_face.jpg
```
<!-- @os:end -->

**Use the precise model** for higher accuracy (at the cost of speed):

<!-- @os:windows -->
```cmd
cvml-sample-face-detection.exe -i sample_face.jpg -m precise
```
<!-- @os:end -->

<!-- @os:linux -->
```bash
./cvml-sample-face-detection -i sample_face.jpg -m precise
```
<!-- @os:end -->

The face detection feature offers two model variants:

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| `fast` (default) | Higher FPS | Good | Real-time camera applications |
| `precise` | Lower FPS | Best | Photo analysis, high-accuracy needs |

## Integrating CVML into Your Own Application

To use the CVML Library in your own C++ project, add it via CMake's `find_package`:

```cmake
# Find the Ryzen AI CVML Library
find_package(RyzenAILibrary REQUIRED PATHS ${AMD_CVML_SDK_ROOT})

# Link against the CVML libraries
target_link_libraries(${PROJECT_NAME} ${RyzenAILibrary_LIBS})
```

Where `AMD_CVML_SDK_ROOT` points to the root of the Ryzen AI CVML Library folder. Then include the appropriate header for the feature you want:

```cpp
#include <cvml-face-detector.h>   // for face detection
#include <cvml-depth-estimation.h> // for depth estimation
#include <cvml-face-mesh.h>        // for face mesh
```

## Next Steps

- **Try Depth Estimation**: Run `cvml-sample-depth-estimation -i sample_face.jpg` to generate a colorized depth map — closer objects appear in warm colors, distant ones in cool colors
- **Explore Face Mesh**: Run `cvml-sample-face-mesh -i sample_face.jpg` to see dense facial geometry tracking with detailed mesh points
- **Process video files**: Use the `-i` and `-o` flags on any sample to process videos (e.g., `cvml-sample-face-detection -i video.mp4 -o output.mp4`)
- **Compare model variants**: Try `-m precise` vs the default `-m fast` on face detection to see the accuracy/speed tradeoff firsthand
- **Build your own app**: Use the CMake integration and C++ API to add CVML features to your own C++ applications
- **Combine features**: Chain face detection with depth estimation in the same application for richer scene understanding
- **Browse the source**: Read the [Ryzen AI CVML Library on GitHub](https://github.com/amd/RyzenAI-SW/tree/main/Ryzen-AI-CVML-Library) for header documentation, additional samples, and API details

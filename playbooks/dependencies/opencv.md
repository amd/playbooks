<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenCV 4.11.0

**1. Install build dependencies** 
```bash
sudo apt update
sudo apt install -y build-essential cmake git pkg-config unzip wget
sudo apt install -y libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libjpeg-dev libpng-dev libtiff-dev
```

**2. Download OpenCV 4.11.0 source**
```bash
cd /tmp
wget -O opencv-4.11.0.zip https://github.com/opencv/opencv/archive/refs/tags/4.11.0.zip
unzip opencv-4.11.0.zip
```

**3. Configure build**
```bash
cd /tmp/opencv-4.11.0
mkdir build
cd build

cmake -S .. -B . \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_INSTALL_PREFIX=/opt/opencv-4.11.0 \
 -DBUILD_opencv_python3=OFF \
 -DBUILD_opencv_python2=OFF \
 -DBUILD_TESTS=OFF \
 -DBUILD_PERF_TESTS=OFF \
 -DBUILD_EXAMPLES=OFF
 ```

**4. Build and install**
```bash
cmake --build . --parallel "$(nproc)"
sudo cmake --install .
```

**5. Set OPENCV_INSTALL_ROOT permanently for interactive shells**
```bash
echo 'export OPENCV_INSTALL_ROOT=/opt/opencv-4.11.0' >> ~/.bashrc
source ~/.bashrc
```

Verify:
```bash
echo $OPENCV_INSTALL_ROOT
ls $OPENCV_INSTALL_ROOT
```

You should see folders like:
- bin
- include
- Lib
- share
or similar.

**6. Set OpenCV_DIR permanently for interactive shells**
`OpenCV_DIR` should point to the folder containing `OpenCVConfig.cmake`.
```bash
echo 'export OpenCV_DIR=/opt/opencv-4.11.0/lib/cmake/opencv4' >> ~/.bashrc
source ~/.bashrc
```

**7. System library path setup**
If the sample executable cannot find OpenCV shared libraries at runtime, add:
```bash
export LD_LIBRARY_PATH=/opt/opencv-4.11.0/lib:$LD_LIBRARY_PATH
```


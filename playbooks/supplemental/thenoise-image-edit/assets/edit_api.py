#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

import base64
import json
import os
import urllib.request

PORT = os.environ.get("THENOISE_PORT", "8000")

PROMPT = ("Set the scene to early evening. Light up the city's windows. Increase the "
          "contrast. Add the text 'AMD ROCm' in a monospaced font in the bottom-left corner.")

with open("city.png", "rb") as f:
    image = base64.b64encode(f.read()).decode()

body = json.dumps({"image": image, "prompt": PROMPT, "steps": 4}).encode()
request = urllib.request.Request(
    f"http://127.0.0.1:{PORT}/edit",
    data=body,
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request) as response:
    with open("city_edited_api.png", "wb") as f:
        f.write(response.read())

print("Saved city_edited_api.png")

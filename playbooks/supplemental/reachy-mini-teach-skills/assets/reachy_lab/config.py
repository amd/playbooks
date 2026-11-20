# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""Settings to try. Change a value, save, and run the script or the app again."""

OLLAMA_URL = "http://127.0.0.1:11434"

# >>> TRY ME <<<  "qwen3.5:0.8b" is faster, "qwen3.5:4b" is smarter (ollama pull it first).
CHAT_MODEL = "qwen3.5:2b"
VISION_MODEL = "qwen3.5:2b"

# >>> TRY ME <<<  Task 1: personality and cloud voice (e.g. "en-GB-RyanNeural").
PERSONA_1 = ("You are a cute desktop robot assistant. Respond with enthusiasm and warmth, "
             "in two or three short sentences. Keep it brief and conversational.")
VOICE_1 = "en-US-JennyNeural"

# >>> TRY ME <<<  Task 2: personality and local Piper voice (a file in models/).
PERSONA_2 = PERSONA_1
PIPER_VOICE = "models/en_US-joe-medium.onnx"

# >>> TRY ME <<<  Task 3: how Reachy answers about what it sees (e.g. "Answer like a pirate.").
VISION_STYLE = "You are a cheerful, curious desktop robot. Answer in one or two short, upbeat sentences."

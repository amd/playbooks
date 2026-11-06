# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""Web app for the three lab tasks.

  python -m reachy_lab.app              # then open http://127.0.0.1:7860
  python -m reachy_lab.app --selftest   # one message per task, no browser (CI)
"""

import argparse
import json
import signal
import sys
import urllib.request

from . import config

EDGE_VOICES = ["en-US-JennyNeural", "en-US-AnaNeural", "en-US-GuyNeural", "en-GB-RyanNeural", "en-AU-NatashaNeural"]
TABS = {1: "Task 1 · Cloud voice", 2: "Task 2 · 100% local", 3: "Task 3 · Eyes"}
INTRO = {
    1: "The model on the iGPU writes the reply; a Microsoft Edge voice from the internet says it.",
    2: "Same as Task 1, but the Piper voice runs on the CPU: nothing leaves this computer.",
    3: "Reachy looks at the table through its camera, and the model on the iGPU answers.",
}
EXAMPLES = {
    1: ["Tell me a joke!", "What is your favourite colour?", "Say hello to everyone in the room."],
    2: ["Tell me a joke!", "What can you do without the internet?", "Give me a fun fact about robots."],
    3: ["What do you see?", "What could I eat for breakfast here?", "Which object is on the left?"],
}


def gpu_memory() -> str:
    """Ollama's own report of where the loaded models are."""
    try:
        with urllib.request.urlopen(config.OLLAMA_URL + "/api/ps", timeout=5) as r:
            models = json.load(r)["models"]
    except Exception as e:
        return f"Ollama is not answering: {e}"
    return "\n".join(f"{m['name']}: {100 * m['size_vram'] / m['size']:.0f}% in GPU memory" for m in models) \
        or "No model loaded yet."


def build(runner, clips):
    import gradio as gr

    lab = runner.lab
    with gr.Blocks(title="Reachy Mini on AMD Ryzen AI") as demo:
        gr.Markdown("# Reachy Mini on AMD Ryzen™ AI")
        with gr.Row():
            view = gr.Image(label="Reachy", interactive=False, height=340)
            eyes = gr.Image(label="What Reachy sees", interactive=False, height=340)
        status = gr.Markdown()
        for task in (1, 2, 3):
            with gr.Tab(TABS[task]):
                gr.Markdown(INTRO[task])
                if task < 3:
                    with gr.Row():
                        persona = gr.Textbox(lab.persona[task], label="Personality", lines=2, scale=3)
                        voices = EDGE_VOICES if task == 1 else [config.PIPER_VOICE]
                        voice = gr.Dropdown(voices, value=lab.voice[task], label="Voice", allow_custom_value=True)
                    persona.change(lambda v, t=task: lab.persona.__setitem__(t, v), persona)
                    voice.change(lambda v, t=task: lab.voice.__setitem__(t, v), voice)
                else:
                    style = gr.Textbox(lab.style, label="Answer style", lines=2)
                    style.change(lambda v: setattr(lab, "style", v), style)
                box = gr.Textbox(label="Your message", placeholder="Type, then press Enter")
                box.submit(lambda text, t=task: (runner.send(t, text), "")[1], box, box)
                with gr.Row():
                    for ex in EXAMPLES[task]:
                        gr.Button(ex, size="sm").click(lambda e=ex, t=task: runner.send(t, e))
        log = gr.Textbox(label="Conversation", lines=9, max_lines=9, interactive=False)
        voice_out = gr.Audio(label="Reachy says", autoplay=True, interactive=False)
        where = gr.Button("Where is the model?", size="sm")
        where_out = gr.Markdown()
        where.click(gpu_memory, None, where_out)

        played = {"n": 0}

        def tick():
            new = gr.skip()
            if len(clips) > played["n"]:
                played["n"] = len(clips)
                new = clips[-1]
            state = "Reachy is thinking or talking ..." if runner.busy else "Ready"
            return lab.world.view, lab.world.eye, f"**{state}** · `{config.CHAT_MODEL}` on the iGPU", \
                "\n".join(list(runner.lines)[-9:]).strip(), new

        gr.Timer(0.25).tick(tick, None, [view, eyes, status, log, voice_out])
    return demo


def selftest(runner, clips) -> int:
    for task, text in ((1, "Say hello in one short sentence."), (2, "Tell me a very short joke."), (3, "What do you see?")):
        runner.send(task, text)
    runner.wait(timeout=900)
    answers = {r["task"]: r["reachy"] for r in runner.lab.history}
    ok = {f"task {t} answered": bool(answers.get(t)) for t in (1, 2, 3)}
    ok["local voice spoke"] = len(clips) >= 2  # Task 1's cloud voice needs the internet: not required
    ok["task 3 named a table object"] = any(w in answers.get(3, "").lower()
                                            for w in ("duck", "apple", "croissant", "bread", "pastry", "fruit"))
    print("\n".join(runner.lines))
    print("\nSELFTEST", " ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in ok.items()))
    return 0 if all(ok.values()) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=7860)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    from .audio import redirect
    from .lab import Runner

    clips = []
    redirect(lambda path, seconds: clips.append(path))  # Reachy's voice plays in the browser
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # stop the simulator on kill too
    runner = Runner()
    try:
        if a.selftest:
            return selftest(runner, clips)
        import gradio as gr

        build(runner, clips).queue().launch(server_name="127.0.0.1", server_port=a.port,
                                             theme=gr.themes.Soft(primary_hue="red"))
    finally:
        runner.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

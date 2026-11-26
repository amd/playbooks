#!/usr/bin/env python
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Check out the pinned MicroDuck repositories and install the training packages.

Run this inside the ROCm PyTorch container from the playbook, after check_rocm.py.
The container already provides HIP PyTorch. This script does not reinstall torch:
every pip call is constrained to the installed ROCm PyTorch stack, so pip cannot
replace that build with a CPU or CUDA wheel.
"""

import importlib
import json
import shlex
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path
from typing import Optional

import lab_paths


REQUIREMENTS = [
    "matplotlib",
    "pandas",
    "tensorboard",
    "unilab[mujoco]==1.0.0",
    "unilab-rl==1.0.0",
    "unisim-core==1.0.0",
    "tensordict==0.14.3",
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


# The ROCm PyTorch stack: torch and its companions, the ROCm runtime wheels, and
# anything else built for ROCm. pip may add packages around it, never replace it.
STACK_NAMES = ["torch", "torchvision", "torchaudio", "triton", "pytorch-triton-rocm"]
STACK_PREFIXES = ["rocm", "amd-torch-"]

# Run by the target interpreter: its ROCm stack ({name: version}) and the names
# of every distribution it can import.
INVENTORY = r"""
import importlib.metadata as md, json, re, sys
names, prefixes = json.loads(sys.argv[1]), tuple(json.loads(sys.argv[2]))
stack, seen = {}, set()
for dist in md.distributions():
    name = dist.metadata["Name"]
    if not name:
        continue
    key = re.sub(r"[-_.]+", "-", name).lower()
    seen.add(key)
    if key in names or key.startswith(prefixes) or "rocm" in dist.version.partition("+")[2]:
        stack.setdefault(key, dist.version)
json.dump({"stack": stack, "names": sorted(seen)}, sys.stdout)
"""

# Run by the target interpreter after installation: the torch the lab will
# train with, where it comes from, and one operation on the GPU.
GPU_CHECK = r"""
import sys, torch
print("Interpreter:", sys.executable)
print("PyTorch:", torch.__version__, "from", torch.__file__)
print("ROCm / HIP:", torch.version.hip)
count = torch.cuda.device_count()
print("Visible AMD GPUs:", count)
if not torch.version.hip or count < 1:
    sys.exit("ROCm PyTorch or GPU access is unavailable after package installation.")
x = torch.ones(8, device="cuda")
if float((x + x).sum()) != 16.0:
    sys.exit("A tensor operation on the GPU returned a wrong result.")
print("GPU check passed on:", torch.cuda.get_device_name(0))
"""


def inventory(python: Path) -> dict:
    output = subprocess.check_output(
        [str(python), "-c", INVENTORY, json.dumps(STACK_NAMES), json.dumps(STACK_PREFIXES)],
        text=True,
    )
    return json.loads(output)


def pip_install(python: Path, *args: str) -> None:
    """Run pip install in ``python`` without changing its ROCm PyTorch stack.

    The installed stack is written to a constraints file, so pip either keeps
    it or stops with a conflict. It cannot swap torch for a PyPI wheel that
    pulls in CUDA packages.
    """
    before = inventory(python)
    if "torch" not in before["stack"]:
        raise SystemExit(f"pip cannot see the torch that {python} imports, so it could replace it.")
    pins = sorted(before["stack"].items())
    kept = ", ".join(f"{n}=={v}" for n, v in pins)
    print("Keeping the ROCm PyTorch stack:", kept, flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        constraints = Path(tmp) / "rocm-stack.txt"
        constraints.write_text("".join(f"{n}=={v}\n" for n, v in pins), encoding="utf-8")
        result = subprocess.run(
            [str(python), "-m", "pip", "install", "--constraint", str(constraints), *args],
            check=False,
        )
    if result.returncode != 0:
        raise SystemExit(
            "pip install failed; see its output above. If pip reports a conflict with "
            "one of the kept packages, this interpreter's PyTorch does not fit UniLab "
            "1.0 (torch>=2.8,<2.12): use the ROCm PyTorch container from the playbook."
        )

    after = inventory(python)
    changed = [
        f"{name} {version} -> {after['stack'].get(name, 'removed')}"
        for name, version in pins
        if after["stack"].get(name) != version
    ]
    cuda = [
        name
        for name in sorted(set(after["names"]) - set(before["names"]))
        if name.startswith(("nvidia-", "cuda-"))
    ]
    if changed or cuda:
        raise SystemExit(
            "pip changed the ROCm PyTorch stack: " + "; ".join(changed + cuda)
        )


def is_system_python() -> bool:
    """True for the operating system's Python, whose packages belong to apt.

    The image's ``/opt/venv``, any other virtual environment and a conda
    environment are the lab's to change. Ubuntu's ``/usr/bin/python3`` is not:
    pip cannot uninstall apt's packages (no RECORD file), and changing them can
    break the system. Some hosts delete the EXTERNALLY-MANAGED marker, so the
    Debian ``dist-packages`` layout counts as well.
    """
    if sys.prefix != sys.base_prefix:
        return False
    marker = Path(sysconfig.get_path("stdlib")) / "EXTERNALLY-MANAGED"
    return marker.is_file() or "dist-packages" in sysconfig.get_path("purelib")


def checkout(repo: str, dest: Path, sha: str, sparse: Optional[list[str]] = None) -> None:
    if not dest.exists():
        command = ["git", "clone", "--filter=blob:none", "--no-checkout"]
        if sparse:
            command.append("--sparse")
        run(*command, repo, str(dest))
        run("git", "-C", str(dest), "fetch", "--depth", "1", "origin", sha)
        if sparse:
            run("git", "-C", str(dest), "sparse-checkout", "set", *sparse)
        run("git", "-C", str(dest), "checkout", "--detach", sha)
    if not (dest / ".git").exists():
        raise RuntimeError(f"Expected a Git checkout at {dest}")
    actual = subprocess.check_output(
        ["git", "-C", str(dest), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != sha:
        raise RuntimeError(f"{dest} is at {actual}; expected {sha}")


def write_env_file(python_bin: Path) -> None:
    bin_dir = python_bin.parent
    exports = {
        "LAB_ROOT": str(lab_paths.LAB_ROOT),
        "MICRODUCK_ROOT": str(lab_paths.TASK_ROOT),
        "LAB_LOG_ROOT": str(lab_paths.LOG_ROOT),
        "UNILAB_EXTRA_REGISTRY_PACKAGES": "microduck_rl_unilab.tasks",
        "MUJOCO_GL": "osmesa",
        "PYOPENGL_PLATFORM": "osmesa",
    }
    lines = [
        "# Generated by prepare_workspace.py. Source this before training or eval.",
        f"export PATH={shlex.quote(str(bin_dir))}:$PATH",
    ]
    lines += [f"export {key}={shlex.quote(value)}" for key, value in exports.items()]
    lab_paths.ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def has_hip(python: str) -> bool:
    probe = subprocess.run(
        [python, "-c", "import torch, sys; sys.exit(0 if torch.version.hip else 1)"],
        check=False,
    )
    return probe.returncode == 0


def select_python() -> Path:
    """Use the ROCm image interpreter when it already provides HIP PyTorch.

    The official image keeps that build in ``/opt/venv``. A nested virtual
    environment only sees Debian's system site-packages, so it cannot see that
    torch. Create ``microduck-venv`` only when the current interpreter has no HIP,
    or when it is the system Python: the venv then sees the system's PyTorch,
    and the lab's packages go into the venv instead of the system.
    """
    if has_hip(sys.executable) and not is_system_python():
        return Path(sys.executable)
    venv_python = lab_paths.VENV_BIN / "python"
    if not venv_python.is_file():
        run(
            sys.executable,
            "-m",
            "venv",
            str(lab_paths.ASSETS / "microduck-venv"),
            "--system-site-packages",
        )
    if has_hip(str(venv_python)):
        return venv_python
    raise SystemExit(
        "HIP PyTorch is not visible. Start the ROCm PyTorch container from this "
        "playbook and rerun there."
    )


def main() -> None:
    lab_paths.WORKSPACE.mkdir(parents=True, exist_ok=True)
    lab_paths.LOG_ROOT.mkdir(parents=True, exist_ok=True)
    python = select_python()

    pip_install(
        python,
        "--upgrade-strategy",
        "only-if-needed",
        "--no-cache-dir",
        *REQUIREMENTS,
    )

    checkout(
        "https://github.com/rocPAI-Forge/microduck_rl_unilab.git",
        lab_paths.TASK_ROOT,
        lab_paths.TASK_SHA,
    )
    checkout(
        "https://github.com/rocPAI-Forge/microduck_rl_tutorial.git",
        lab_paths.LAB_ROOT,
        lab_paths.LAB_SHA,
        sparse=["scripts", "examples/velocity_flat_demo"],
    )

    if not (lab_paths.LAB_ROOT / "scripts" / "run_train.sh").is_file():
        raise RuntimeError("Lab training script is missing from the pinned checkout")
    if not (lab_paths.DEMO / "model_950.pt").is_file():
        raise RuntimeError("Reference checkpoint is missing from the pinned checkout")

    pip_install(
        python,
        "--no-cache-dir",
        "--no-deps",
        "-e",
        str(lab_paths.TASK_ROOT),
    )
    importlib.invalidate_caches()

    if subprocess.run([str(python), "-c", GPU_CHECK], check=False).returncode != 0:
        raise SystemExit(
            "ROCm PyTorch or GPU access is unavailable after package installation."
        )

    for script in (lab_paths.LAB_ROOT / "scripts").glob("*.sh"):
        script.chmod(0o755)
    write_env_file(python)

    version = subprocess.check_output(
        [
            str(python),
            "-c",
            "import torch; print(torch.__version__, torch.version.hip)",
        ],
        text=True,
    ).strip()
    print("Workspace:", lab_paths.WORKSPACE)
    print("Task commit:", lab_paths.TASK_SHA)
    print("Lab support commit:", lab_paths.LAB_SHA)
    print("ROCm PyTorch:", version)
    print("Environment file:", lab_paths.ENV_FILE)
    print("Ready for the environment check and training commands below.")


if __name__ == "__main__":
    main()

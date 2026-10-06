#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Put a mirrored artifact where a prerequisite's own download would put it.

Adapted from the Ryzen AI documentation mirror's get.py. The internal Artifactory
mirror's base URL comes from the ARTIFACTORY_BASE secret; reads are anonymous, and
the URL is a secret only to keep the internal host out of public logs. Without the
secret (e.g. a fork PR), or when the mirror does not carry the artifact or the
transfer fails, the prerequisite's normal download still runs.

    get.py fetch <mirror path> --to <file> [--upstream]
    get.py seed <group>

fetch exits 0 iff <file> is in place afterwards, so a caller can chain a fallback;
with --upstream it falls back to the artifacts.json url itself.

seed places every file of one artifacts.json group, named after the registry
dependency that uses it, in the store of that group's tool: Lemonade's Hugging
Face cache, LM Studio's models folder or Ollama's model store. The tool's own
install then finds the files and skips the download. Exits 0 iff all are in place.

Every download is checked against the SHA-256 pinned in artifacts.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

MANIFEST = Path(__file__).with_name("artifacts.json")
CURL = "curl.exe" if os.name == "nt" else "curl"
# Resilient transfer: the corporate link can stall a single connection, so turn a
# stall into a retry and resume from the byte it stopped at.
CURL_FETCH = [CURL, "-sSfL", "--connect-timeout", "10", "--retry", "30", "--retry-all-errors",
              "--retry-delay", "2", "--speed-limit", "102400", "--speed-time", "15", "-C", "-"]
# Seed into this directory instead of the tool's own store (tests, unusual installs).
STORE_OVERRIDE = "PLAYBOOKS_MIRROR_STORE"
# Set once the mirror fails to connect, so the rest of a group skips it at once.
unreachable = False


def record(artifact: str, outcome: str) -> None:
    """Append what was asked for and what happened, so a run can prove it used the mirror."""
    path = os.environ.get("PLAYBOOKS_MIRROR_LEDGER")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"artifact": artifact, "outcome": outcome}) + "\n")


def load_manifest(path: Path) -> dict:
    return {a["dest"]: a for a in json.loads(path.read_text(encoding="utf-8"))}


def head_status(url: str) -> str:
    """HTTP status of a HEAD request ("000" if it cannot connect); settles a 404 before curl would retry it."""
    r = subprocess.run([CURL, "-sSL", "-o", os.devnull, "--head", "--connect-timeout", "10",
                        "--max-time", "60", "-w", "%{http_code}", url], capture_output=True, text=True)
    return r.stdout.strip()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, sha256: str) -> bool:
    """Fetch url to dest via a .part file; keep it only if it is whole and matches sha256."""
    part = dest.with_name(dest.name + ".part")
    part.unlink(missing_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if subprocess.run(CURL_FETCH + ["-o", str(part), url]).returncode != 0:
        part.unlink(missing_ok=True)
        return False
    if sha256 and sha256_of(part) != sha256:
        print(f"checksum mismatch for {dest.name}; discarding it")
        part.unlink(missing_ok=True)
        return False
    part.replace(dest)
    return True


def fetch(path: str, dest: Path, sha256: str, url: str = "") -> bool:
    """Put one mirrored file at dest, from the mirror or else from url. True iff it is in place."""
    global unreachable
    if dest.exists():
        record(path, "present")
        print(f"{dest} is already in place")
        return True
    base = os.environ.get("ARTIFACTORY_BASE", "").rstrip("/")
    if not base:
        record(path, "no-secret")
        print("ARTIFACTORY_BASE is not set, so the mirror is unreachable")
    elif unreachable:
        record(path, "skipped")
    else:
        status = head_status(f"{base}/{path}")
        if status == "000":
            unreachable = True
            record(path, "unreachable")
            print("the mirror cannot be reached from this machine")
        elif status != "200":
            record(path, "absent")
            print(f"{path} is not on the mirror (HTTP {status})")
        elif download(f"{base}/{path}", dest, sha256):
            record(path, "downloaded")
            print(f"{dest.name} came from the internal mirror")
            return True
        else:
            record(path, "failed")
            print(f"fetching {path} from the mirror failed")
    if url:
        print(f"falling back to upstream for {dest.name}")
        if download(url, dest, sha256):
            record(path, "upstream")
            return True
        print(f"upstream download of {dest.name} failed")
    return False


def cmd_fetch(args) -> int:
    entry = load_manifest(Path(args.manifest)).get(args.path, {})
    url = entry.get("url", "") if args.upstream else ""
    return 0 if fetch(args.path, Path(args.to), entry.get("sha256", ""), url) else 1


# ---- seed: the stores of the tools the prereqs install models into ----

def invoking_home() -> Path:
    """Home of the user who ran this, also under sudo."""
    if os.name != "nt" and os.environ.get("SUDO_USER"):
        import pwd
        return Path(pwd.getpwnam(os.environ["SUDO_USER"]).pw_dir)
    return Path.home()


def server_env(process: str, service_user: str = "", arg: str = "") -> dict:
    """Environment of the tool's server: the running process, else its service user, else ours."""
    if os.name != "nt":
        import pwd
        for comm in Path("/proc").glob("[0-9]*/comm"):
            try:
                if comm.read_text().strip() != process:
                    continue
                if arg and arg not in (comm.parent / "cmdline").read_bytes().decode(errors="replace").split("\0"):
                    continue
                env = {"HOME": pwd.getpwuid(comm.parent.stat().st_uid).pw_dir}
                try:  # readable as root or as the process's own user
                    raw = (comm.parent / "environ").read_bytes().decode(errors="replace")
                    env.update(kv.split("=", 1) for kv in raw.split("\0") if "=" in kv)
                except OSError:
                    pass
                return env
            except (OSError, KeyError):
                continue
        if service_user:
            try:
                return {"HOME": pwd.getpwnam(service_user).pw_dir}
            except KeyError:
                pass
    return dict(os.environ, HOME=str(invoking_home()))


def lemonade_store() -> Path:
    """Lemonade's Hugging Face cache, resolved the way Lemonade does it."""
    env = server_env("lemond", "lemonade")
    if env.get("HF_HUB_CACHE"):
        return Path(env["HF_HUB_CACHE"])
    if env.get("HF_HOME"):
        return Path(env["HF_HOME"]) / "hub"
    return Path(env["HOME"]) / ".cache" / "huggingface" / "hub"


def lmstudio_store() -> Path:
    """LM Studio's models folder: its downloadsFolder setting, else ~/.lmstudio/models."""
    home = invoking_home() / ".lmstudio"
    try:
        folder = json.loads((home / "settings.json").read_text(encoding="utf-8")).get("downloadsFolder")
    except (OSError, ValueError, AttributeError):
        folder = None
    return Path(folder) if folder else home / "models"


def ollama_store() -> Path:
    """Ollama's model store; the install starts `ollama serve` as us when no server runs."""
    env = server_env("ollama", arg="serve")
    return Path(env["OLLAMA_MODELS"]) if env.get("OLLAMA_MODELS") else Path(env["HOME"]) / ".ollama" / "models"


def hf_api(path: str):
    """JSON from the Hugging Face API, at HF_ENDPOINT when set (Lemonade honours it too)."""
    base = os.environ.get("HF_ENDPOINT", "https://huggingface.co").rstrip("/")
    token = os.environ.get("HF_TOKEN")
    req = urllib.request.Request(f"{base}/api/models/{path}",
                                 headers={"Authorization": f"Bearer {token}"} if token else {})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def plan_lmstudio(entries: list, store: Path) -> tuple[list, list]:
    # models/<tool>/<user>/<repo>/<file> -> <store>/<user>/<repo>/<file>
    return [(e, store.joinpath(*e["dest"].split("/")[2:])) for e in entries], []


def plan_ollama(entries: list, store: Path) -> tuple[list, list]:
    # models/Ollama/<model>/<path in the store>; manifests last, so a half-seeded model never lists.
    ordered = sorted(entries, key=lambda e: "/manifests/" in e["dest"])
    return [(e, store.joinpath(*e["dest"].split("/")[3:])) for e in ordered], []


def plan_lemonade(entries: list, store: Path) -> tuple[list, list]:
    """Into the snapshot of the repo's current commit, where `lemonade pull` downloads to and skips
    files already present. A file that changed upstream since it was mirrored is left for the pull."""
    plan, skipped, repos = [], [], {}
    for e in entries:
        repos.setdefault("/".join(e["dest"].split("/")[2:4]), []).append(e)
    for repo, group in repos.items():
        try:
            commit = hf_api(f"{repo}/revision/main")["sha"]
            listing = {}
            for folder in {e["dest"].split("/", 4)[4].rpartition("/")[0] for e in group}:
                for item in hf_api(f"{repo}/tree/{commit}" + (f"/{folder}" if folder else "")):
                    listing[item["path"]] = item
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"cannot read {repo} on Hugging Face ({exc}); lemonade pull will fetch it")
            skipped += group
            continue
        snapshot = store / f"models--{repo.replace('/', '--')}" / "snapshots" / commit
        for e in group:
            name = e["dest"].split("/", 4)[4]
            if ((listing.get(name) or {}).get("lfs") or {}).get("oid") != e["sha256"]:
                record(e["dest"], "stale")
                print(f"{name} changed upstream since it was mirrored; lemonade pull will fetch it")
                skipped.append(e)
            else:
                plan.append((e, snapshot.joinpath(*name.split("/"))))
    return plan, skipped


TOOLS = {"lemonade": (lemonade_store, plan_lemonade),
         "lmstudio": (lmstudio_store, plan_lmstudio),
         "ollama": (ollama_store, plan_ollama)}


def existing_ancestor(path: Path) -> Path:
    while not os.path.exists(path):  # also False where a parent is unreadable to us
        path = path.parent
    return path


def elevate_for(store: Path) -> None:
    """Re-run under sudo when a Linux service user owns the store (Lemonade, Ollama)."""
    if os.name == "nt" or os.geteuid() == 0 or os.environ.get("PLAYBOOKS_MIRROR_SUDO"):
        return
    if os.access(existing_ancestor(store), os.W_OK | os.X_OK):
        return
    print(f"{store} belongs to the tool's service user; retrying with sudo", flush=True)
    os.environ["PLAYBOOKS_MIRROR_SUDO"] = "1"
    os.execvp("sudo", ["sudo", "-n", "-E", sys.executable, *sys.argv])


def adopt(path: Path, anchor: Path) -> None:
    """Hand what we created as root back to the store's owner, so the tool can manage it."""
    if os.name == "nt" or os.geteuid() != 0:
        return
    st = anchor.stat()
    while path != anchor and anchor in path.parents:
        if path.stat().st_uid != st.st_uid:
            os.chown(path, st.st_uid, st.st_gid)
        path = path.parent


def cmd_seed(args) -> int:
    entries = [e for e in load_manifest(Path(args.manifest)).values() if e.get("group") == args.group]
    tool = TOOLS.get(args.group.split("-models", 1)[0])
    if not entries or not tool:
        print(f"nothing is mirrored for {args.group}")
        return 1
    if not os.environ.get("ARTIFACTORY_BASE"):
        print("ARTIFACTORY_BASE is not set, so the mirror is unreachable")
        return 1
    store_of, plan_of = tool
    store = Path(os.environ[STORE_OVERRIDE]) if os.environ.get(STORE_OVERRIDE) else store_of()
    elevate_for(store)
    anchor = existing_ancestor(store)
    plan, skipped = plan_of(entries, store)
    placed = 0
    for entry, dest in plan:
        if fetch(entry["dest"], dest, entry["sha256"]):
            adopt(dest, anchor)
            placed += 1
    print(f"{args.group}: {placed} of {len(entries)} mirrored files in place under {store}")
    return 0 if placed == len(entries) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(MANIFEST), help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True)
    fetch_p = sub.add_parser("fetch", help="put one mirrored file in place")
    fetch_p.add_argument("path", help="path in the mirror, as artifacts.json lists it under dest")
    fetch_p.add_argument("--to", required=True, help="where the file should end up")
    fetch_p.add_argument("--upstream", action="store_true",
                         help="when the mirror cannot serve it, download the artifacts.json url")
    fetch_p.set_defaults(func=cmd_fetch)
    seed_p = sub.add_parser("seed", help="put a dependency's mirrored files in its tool's store")
    seed_p.add_argument("group", help="artifacts.json group, named after the registry dependency")
    seed_p.set_defaults(func=cmd_seed)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""OIDC-only client shared by the opt-in OrchestrAI V2 controller.

Contract reference: ucicd-pipeline/.github/actions/orchestrai-run and
ci-actions-lib/ci_classes/orchestrai_controlplane.py. No private checkout,
stored API token, internal admin API or direct Jenkins call is involved.
"""

import base64
import copy
from dataclasses import dataclass
import hashlib
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
import signal
import ssl
import time
from urllib import error, parse, request

TERMINAL = {"passed", "failed", "unstable", "cancelled", "error"}


class ApiError(ValueError):
    def __init__(self, message, transient=False):
        super().__init__(message)
        self.transient = transient


class Interrupted(ApiError):
    pass


def https_url(value, name):
    parts = parse.urlsplit(value)
    if (parts.scheme != "https" or not parts.hostname or parts.username or
            parts.password or parts.query or parts.fragment):
        raise ApiError(f"{name} must be an HTTPS URL without credentials, query or fragment")
    return value.rstrip("/")


@dataclass(frozen=True)
class Settings:
    api: str
    audience: str
    portal: str
    workspace: str
    timeout: float = 300 * 60
    poll: float = 30
    start_timeout: float = 10 * 60
    outage_timeout: float = 60 * 60
    cleanup_timeout: float = 120

    @classmethod
    def from_env(cls, workspace, env):
        values = {}
        for key, field in (("CI_API_URL", "api"), ("OIDC_AUDIENCE", "audience"),
                           ("PORTAL_URL", "portal")):
            name = "ORCHESTRAI_V2_" + key
            raw = env.get(name, "").strip()
            if not raw:
                raise ApiError(f"Set repository variable {name} for this V2 deployment")
            values[field] = https_url(raw, name)
        if not values["api"].endswith(("/api/ci/v1", "/ci/v1")):
            raise ApiError("ORCHESTRAI_V2_CI_API_URL must name the supported CI API")
        return cls(workspace=workspace, **values)


class NoRedirect(request.HTTPRedirectHandler):
    # Never forward an OIDC bearer to an edge redirect or another host.
    def redirect_request(self, *_args, **_kwargs):
        return None


def http(method, url, headers, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, method=method, headers=headers)
    opener = request.build_opener(NoRedirect())
    try:
        try:
            response = opener.open(req, timeout=15)
        except error.HTTPError as exc:
            response = exc
        with response:
            raw = response.read(2 * 1024 * 1024 + 1)
            try:
                payload = json.loads(raw) if len(raw) <= 2 * 1024 * 1024 else None
            except (ValueError, UnicodeError):
                payload = None
            return response.code, payload
    except (error.URLError, HTTPException, TimeoutError, OSError) as exc:
        if isinstance(exc, ssl.SSLCertVerificationError) or isinstance(getattr(exc, "reason", None), ssl.SSLCertVerificationError):
            raise ApiError("V2 HTTPS certificate is not trusted by this runner; configure its CA trust") from None
        # Includes disconnects/timeouts while reading a body, not just connect.
        # Do not print exception URLs/headers or request bodies.
        raise ApiError(f"HTTPS request failed ({type(exc).__name__})", transient=True) from None


def error_detail(payload):
    """Current CP envelope is error:{code,message}; accept legacy detail too."""
    if not isinstance(payload, dict):
        return {}
    for key in ("error", "detail"):
        if isinstance(payload.get(key), dict):
            return payload[key]
    return payload


def code_of(payload):
    detail = error_detail(payload)
    code = detail.get("code", "") if isinstance(detail, dict) else ""
    # Only an API error code is printed, never arbitrary response text.
    return code if isinstance(code, str) and all(c.isalnum() or c == "_" for c in code) else ""


def run_of(payload):
    run = payload.get("run") if isinstance(payload, dict) else None
    return run if isinstance(run, dict) and isinstance(run.get("id"), str) and run["id"] else None


def save_state(path, state):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with open(temp, "w", encoding="utf-8") as handle:
        os.chmod(temp, 0o600)
        json.dump(state, handle)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def start_body(document, env):
    parameters = document["parameters"]
    plan = copy.deepcopy(parameters["PLAN_JSON"])
    settings = plan.setdefault("run_settings", {})
    # External exports are an explicit choice of this V2 request, not an
    # inherited legacy run-setting or the mere presence of a repo variable.
    settings.pop("result_publishers", None)
    settings["max_duration"] = int(parameters["MAX_DURATION"])
    if settings["max_duration"] <= 0 or settings["max_duration"] > 300:
        raise ApiError("V2 run duration must be 1..300 minutes, below the GitHub job limit")
    cp = document["config"]["control_plane"]
    publishers = copy.deepcopy(cp.get("result_publishers", []))
    for publisher in publishers:
        attributes = publisher.get("attributes", {})
        if attributes.get("github_run_id") == "{GITHUB_RUN_ID}":
            attributes["github_run_id"] = env.get("GITHUB_RUN_ID", "")
    if publishers:
        settings["result_publishers"] = publishers
    repo, run_id = env.get("GITHUB_REPOSITORY", ""), env.get("GITHUB_RUN_ID", "")
    return {
        "require_capacity": "queue",
        "plan_document": {
            "name": f"Playbooks V2 {document['batch_id']} {run_id}/{env.get('GITHUB_RUN_ATTEMPT', '')}",
            "description": f"Started by https://github.com/{repo}/actions/runs/{run_id}",
            "document": plan,
        },
        "builds_json": parameters["BUILDS_JSON"],
    }


class Client:
    def __init__(self, settings, env, transport=http, clock=time.monotonic,
                 wall_clock=time.time, sleep=time.sleep):
        self.settings, self.env, self.transport = settings, env, transport
        self.clock, self.wall_clock, self.sleep = clock, wall_clock, sleep
        self.token, self.expires = "", 0
        self.interrupted = False
        self.state = {}
        self.uncertain_start = False
        self.redactions = [env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")]

    def diagnostic(self, status, payload):
        detail = error_detail(payload)
        code = code_of(payload)
        message = detail.get("message", "")
        if not message and isinstance(payload, dict):
            message = next((payload[k] for k in ("detail", "error") if isinstance(payload.get(k), str)), "")
        message = " ".join(message.split()) if isinstance(message, str) else ""
        for secret in self.redactions + [self.token]:
            if secret:
                message = message.replace(secret, "[REDACTED]")
        # Do not echo bearer/query credentials even if an upstream message does.
        message = re.sub(r"(?i)bearer\s+\S+", "Bearer [REDACTED]", message)
        message = re.sub(r"(?i)([?&](?:token|key|password|secret|access_token)=)[^&\s]+", r"\1[REDACTED]", message)
        identifier = payload.get("request_id", "") if isinstance(payload, dict) else ""
        identifier = identifier if isinstance(identifier, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", identifier) else ""
        text = f"V2 CI API HTTP {status}" + (f" {code}" if code else "")
        if message:
            text += ": " + message[:500]
        if identifier:
            text += f" (request_id={identifier})"
        return text + "; inspect Workspace > CI access > Activity"

    def stop(self, *_args):
        self.interrupted = True
        raise Interrupted("GitHub job interrupted")

    def pause(self, seconds, cleanup=False):
        deadline = self.clock() + seconds
        while self.clock() < deadline:
            if self.interrupted and not cleanup:
                raise Interrupted("GitHub job interrupted")
            self.sleep(min(1, deadline - self.clock()))

    def bearer(self, fresh=False):
        if self.token and not fresh and self.wall_clock() < self.expires - 60:
            return self.token
        url = self.env.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
        req_token = self.env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
        parts = parse.urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or not req_token:
            raise ApiError("GitHub OIDC is unavailable; the calling job needs id-token: write")
        status, payload = self.transport("GET", url + ("&" if "?" in url else "?") +
                                         parse.urlencode({"audience": self.settings.audience}),
                                         {"Authorization": f"Bearer {req_token}", "Accept": "application/json"})
        token = payload.get("value") if isinstance(payload, dict) else None
        if status != 200 or not isinstance(token, str) or not token:
            raise ApiError(f"GitHub could not issue an OIDC token (HTTP {status})", status >= 500)
        print("::add-mask::" + token)
        self.redactions.append(token)
        self.token = token
        try:
            segment = token.split(".")[1]
            expiry = json.loads(base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))["exp"]
            self.expires = float(expiry)
        except (ValueError, KeyError, IndexError, TypeError):
            self.expires = self.wall_clock() + 120
        return token

    def call(self, method, path, body=None, key=None):
        for attempt in range(2):
            headers = {"Authorization": "Bearer " + self.bearer(fresh=attempt == 1),
                       "Accept": "application/json", "Content-Type": "application/json",
                       "X-OrchestrAI-Workspace": self.settings.workspace}
            if key:
                headers["Idempotency-Key"] = key
            status, payload = self.transport(method, self.settings.api + path, headers, body)
            if status != 401 or code_of(payload) != "token_expired" or attempt:
                return status, payload

    def retry(self, method, path, body=None, key=None, seconds=120, cleanup=False):
        deadline, delay = self.clock() + seconds, 2
        while True:
            if self.interrupted and not cleanup:
                raise Interrupted("GitHub job interrupted")
            try:
                status, payload = self.call(method, path, body, key)
                if status == 204 and path.endswith("/cancel"):
                    return {}
                if 200 <= status < 300 and isinstance(payload, dict):
                    return payload
                code = code_of(payload)
                transient = (status in (408, 429) or status >= 500 or
                             (status == 409 and code == "idempotency_in_progress") or
                             (200 <= status < 300 and not isinstance(payload, dict)) or
                             (status == 404 and payload is None))
                raise ApiError(self.diagnostic(status, payload), transient)
            except ApiError as exc:
                if method == "POST" and path == "/runs" and exc.transient:
                    self.uncertain_start = True
                if isinstance(exc, Interrupted) or not exc.transient or self.clock() >= deadline:
                    raise
                self.pause(min(delay, max(0, deadline - self.clock())), cleanup)
                delay = min(delay * 2, 30)

    def identity(self, document, body):
        names = ("GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_JOB")
        if any(not self.env.get(name) for name in names):
            raise ApiError("V2 execution requires GitHub repository/run/attempt/job identity")
        identity = [self.env[n] for n in names] + [document["batch_id"]]
        digest = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        return {"ci_api": self.settings.api, "workspace": self.settings.workspace,
                "key": hashlib.sha256(json.dumps(identity).encode()).hexdigest(),
                "request_hash": digest, "finished": False, "attempted": False}

    def start(self, document, body, path):
        expected = self.identity(document, body)
        if Path(path).is_file():
            saved = json.loads(Path(path).read_text())
            self.check_identity(saved, expected)
            self.state = saved
            if saved.get("run_id"):
                return saved["run_id"]
            if saved.get("finished"):
                raise ApiError("This submission was already refused; use a new GitHub run attempt")
            self.uncertain_start = bool(saved.get("attempted"))
        else:
            self.state = expected
        self.state["attempted"] = True
        save_state(path, self.state)  # Persist identity BEFORE the first POST.
        try:
            payload = self.retry("POST", "/runs", body, self.state["key"], self.settings.start_timeout)
        except ApiError as exc:
            if not exc.transient and not isinstance(exc, Interrupted) and not self.uncertain_start:
                self.state["finished"] = True  # Definite refusal, not a lost response.
                save_state(path, self.state)
            raise
        run = run_of(payload)
        if not run:
            raise ApiError("V2 start response contained no run ID", transient=True)
        self.state["run_id"] = run["id"]
        save_state(path, self.state)
        return run["id"]

    @staticmethod
    def check_identity(saved, expected):
        if any(saved.get(k) != expected[k] for k in ("ci_api", "workspace", "key", "request_hash")):
            raise ApiError("Saved V2 state belongs to a different job, request or deployment; refusing cleanup")

    def cancel(self, document, body, path):
        if not Path(path).is_file():
            return
        saved = json.loads(Path(path).read_text())
        self.check_identity(saved, self.identity(document, body))
        if saved.get("finished") or not saved.get("attempted"):
            return
        deadline = self.clock() + self.settings.cleanup_timeout
        rid = saved.get("run_id")
        if not rid:
            # A lost start response may have left a run active. Replay ONLY the
            # original request/key, then cancel; never issue a new submission.
            payload = self.retry("POST", "/runs", body, saved["key"],
                                 max(0, deadline - self.clock()), cleanup=True)
            run = run_of(payload)
            if not run:
                raise ApiError("Cannot recover the interrupted V2 submission; inspect the Portal")
            rid = saved["run_id"] = run["id"]
            save_state(path, saved)
        self.retry("POST", f"/runs/{parse.quote(rid, safe='')}/cancel", {},
                   seconds=max(0, deadline - self.clock()), cleanup=True)
        # Acceptance of cancellation is NOT proof that hardware is released.
        saved["cancel_requested"] = True
        self.state = saved
        save_state(path, saved)
        print(f"V2 cancellation requested: {rid}; verify terminal status/release in the Portal")

    def wait(self, rid, path):
        deadline, last = self.clock() + self.settings.timeout, None
        while True:
            if self.interrupted:
                raise Interrupted("GitHub job interrupted")
            if self.clock() >= deadline:
                raise ApiError("V2 run exceeded the 300-minute client budget")
            payload = self.retry("GET", f"/runs/{parse.quote(rid, safe='')}",
                                 seconds=min(self.settings.outage_timeout, deadline - self.clock()))
            run = run_of(payload)
            if not run or run["id"] != rid:
                raise ApiError("V2 returned an invalid or mismatched run")
            status = run.get("status")
            if status != last:
                print(f"V2 run {rid}: {status}")
                last = status
            if status in TERMINAL:
                self.state["finished"] = True
                save_state(path, self.state)
                return run
            self.pause(min(self.settings.poll, max(0, deadline - self.clock())))

    def execute(self, document, path):
        body = start_body(document, self.env)
        self.redactions += [value for value in document["parameters"]["BUILDS_JSON"].get("vars", {}).values()
                            if isinstance(value, str) and len(value) >= 4]
        if len(json.dumps(body).encode()) > 60 * 1024:
            raise ApiError("V2 start document exceeds the 60-KiB client limit; select fewer playbooks")
        old = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
        for sig in old:
            signal.signal(sig, self.stop)
        try:
            rid = self.start(document, body, path)
            run = self.wait(rid, path)
            payload = self.retry("GET", f"/runs/{parse.quote(rid, safe='')}/tests")
            tests = payload.get("tests")
            if not isinstance(tests, list) or any(not isinstance(t, dict) for t in tests):
                raise ApiError("V2 returned no valid test-result list")
            ok = run.get("status") == "passed" and run.get("tests_status") != "failed"
            return {"run_id": rid, "url": run.get("url") or self.settings.portal + "/#/runs/" + parse.quote(rid, safe=""),
                    "pipeline_url": run.get("pipeline_url", ""), "status": run.get("status"),
                    "pipeline_status": run.get("pipeline_status"), "tests_status": run.get("tests_status"),
                    "tests_summary": run.get("tests_summary") or {}, "tests": tests,
                    "verdict": "success" if ok else "failure"}
        except ApiError as exc:
            # Continue cleanup on repeated signals. The workflow's always step
            # can repeat it; the server-side plan timeout bounds runner loss.
            for sig in old:
                signal.signal(sig, lambda *_: None)
            try:
                self.cancel(document, body, path)
            except (ApiError, OSError, ValueError) as cleanup_error:
                print(f"::warning::V2 cleanup incomplete: {cleanup_error}")
            return {"verdict": "failure", "status": "cancelled" if isinstance(exc, Interrupted) else "error",
                    "error": str(exc), "run_id": self.state.get("run_id", "")}
        finally:
            for sig, handler in old.items():
                signal.signal(sig, handler)

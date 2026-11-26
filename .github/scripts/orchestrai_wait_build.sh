#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Wait until one OrchestrAI pipeline build finishes (STARTED_BUILD_URL, BATCH_ID).
# Writes build_url to $GITHUB_OUTPUT. Used for a batch's build and for its retry.
set -e
BUILD_URL="${STARTED_BUILD_URL}"
if [ -z "$BUILD_URL" ]; then
  echo "::error::No OrchestrAI pipeline build URL for batch ${BATCH_ID}"; exit 1
fi
echo "build_url=${BUILD_URL}" >> "$GITHUB_OUTPUT"
echo "Waiting for OrchestrAI pipeline build ..."
# SECURITY: pass credentials via a 0600 netrc file, never as `curl -u
# user:token` — argv is world-readable (/proc/<pid>/cmdline, ps) for the
# life of each curl, which would leak the pipeline token to any other
# process on a shared/persistent self-hosted runner. mktemp creates the
# file 0600; printf is a shell builtin, so the token never hits argv.
NETRC="$(mktemp)"
# Live progress (stage, machine, each playbook's outcome) printed while this
# loop waits; orchestrai_follow.py only prints and never decides anything here.
FOLLOW_PID=""
if [ "${ORCHESTRAI_FOLLOW:-1}" != "0" ] && command -v python3 >/dev/null; then
  python3 "$(dirname "$0")/orchestrai_follow.py" &
  FOLLOW_PID=$!
fi
trap 'rm -f "$NETRC"; if [ -n "$FOLLOW_PID" ]; then kill "$FOLLOW_PID" 2>/dev/null || true; fi' EXIT
NETRC_HOST=$(printf '%s' "$BUILD_URL" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##; s#[:/].*$##')
printf 'machine %s login %s password %s\n' \
  "$NETRC_HOST" "$ORCHESTRAI_PIPELINE_USER" "$ORCHESTRAI_PIPELINE_TOKEN" > "$NETRC"
# Bounded poll: wall-clock time (not a count of polls, which each take 15s
# plus the request) of run_settings.max_duration in orchestrai-config.yml
# (next to this script) plus 30 min for the build to wind down. It starts
# once the build has started; the wait for machines before it
# (acquire_timeout + 30 min) is --await-build's. The Test jobs'
# timeout-minutes budget both, per attempt.
CONFIG="$(dirname "$0")/../orchestrai-config.yml"
MAX_DURATION=$(sed -nE 's/^[[:space:]]+max_duration:[[:space:]]*([0-9]+).*/\1/p' "$CONFIG" | head -n1)
if [ -z "$MAX_DURATION" ]; then
  echo "::error::No run_settings.max_duration in $CONFIG"; exit 1
fi
DEADLINE=$((SECONDS + (MAX_DURATION + 30) * 60))
FAIL_MAX=20       # ~5min of consecutive unreachable polls -> give up
finished=""; fails=0
while [ "$SECONDS" -lt "$DEADLINE" ]; do
  if data=$(curl -sf --connect-timeout 10 --max-time 30 --netrc-file "$NETRC" "${BUILD_URL}api/json?tree=result,building" 2>/dev/null); then
    fails=0
    building=$(echo "$data" | python3 -c "import sys,json;print(json.load(sys.stdin).get('building',True))" 2>/dev/null || echo "True")
    result=$(echo "$data" | python3 -c "import sys,json;print(json.load(sys.stdin).get('result') or '')" 2>/dev/null || echo "")
    # The batch result reflects ALL its playbooks; this job's verdict is
    # resolved per-playbook in the next step from summary.json.
    if [ "$building" = "False" ] && [ -n "$result" ]; then
      echo "Batch build finished: $result (per-playbook verdict resolved next)"; finished=1
      # Up to 3 min for the follower to print the last results; its final read
      # of them retries for less (FINAL_RESULTS_RETRY_SECONDS, orchestrai_follow.py).
      for _ in $(seq 36); do
        if [ -z "$FOLLOW_PID" ] || ! kill -0 "$FOLLOW_PID" 2>/dev/null; then break; fi
        sleep 5
      done
      break
    fi
  else
    fails=$((fails + 1))
    if [ "$fails" -ge "$FAIL_MAX" ]; then
      echo "::error::OrchestrAI pipeline unreachable ($FAIL_MAX consecutive failures)"; exit 1
    fi
  fi
  sleep 15
done
if [ -z "$finished" ]; then
  echo "::error::Timed out waiting for OrchestrAI pipeline build"; exit 1
fi

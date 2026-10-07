# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# As the provisioning scripts check: the lms CLI, and the task that starts LM Studio's server at logon.
lms --help | Out-Null
if (-not $?) { exit 1 }
if (-not (Get-ScheduledTask -TaskName 'LM Studio Server' -ErrorAction SilentlyContinue)) { exit 1 }
exit 0

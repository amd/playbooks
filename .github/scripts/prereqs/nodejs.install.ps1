# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# Installs the current LTS, or upgrades an older Node.js in place; the runner task is elevated.
$p = Start-Detached winget @('install', '--id', 'OpenJS.NodeJS.LTS', '-e', '--accept-source-agreements', '--accept-package-agreements', '--silent')
$p.WaitForExit()
exit $p.ExitCode

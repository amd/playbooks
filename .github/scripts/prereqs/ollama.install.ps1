# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# Detached: the installer can launch the Ollama app, which must not inherit this step's pipe.
$p = Start-Detached winget @('install', '--id', 'Ollama.Ollama', '-e', '--accept-source-agreements', '--accept-package-agreements', '--silent')
$p.WaitForExit()
exit $p.ExitCode

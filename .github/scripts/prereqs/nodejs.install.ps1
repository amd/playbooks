# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

. "$PSScriptRoot\common.ps1"
# As the provisioning scripts do; only reached when Node.js is absent.
$p = Start-Detached winget @('install', '-e', '--id', 'OpenJS.NodeJS', '--accept-package-agreements', '--accept-source-agreements', '--silent')
$p.WaitForExit()
exit $p.ExitCode

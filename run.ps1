#!/usr/bin/env pwsh
# EGC runtime wrapper (Windows) — repository-isolated, cwd-independent.
#
# All runtime paths derive from the wrapper location ($PSScriptRoot), never
# from the current working directory. Repository-local binaries
# (node_modules\.bin, .venv\Scripts) always win over host binaries.
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrEmpty($PSScriptRoot)) {
    Write-Error '[EGC] ERROR: run.ps1 must be invoked as a script file so $PSScriptRoot resolves.'
    exit 1
}

$PROJECT_ROOT = $PSScriptRoot
$env:PROJECT_ROOT = $PROJECT_ROOT
$env:PATH = (Join-Path $PROJECT_ROOT 'node_modules\.bin') + ';' + (Join-Path $PROJECT_ROOT '.venv\Scripts') + ';' + $env:PATH

& node (Join-Path $PROJECT_ROOT 'scripts\egc.js') @args
exit $LASTEXITCODE

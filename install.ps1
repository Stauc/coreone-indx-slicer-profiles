<#
  Installs the CORE One INDX slicer profiles from this repository into the slicers' data folders (Windows).

  Usage (PowerShell, from the repository folder; close the slicers first):
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -PS3
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -PS2 -Orca
    powershell -ExecutionPolicy Bypass -File .\install.ps1 -All

  -PS2           PrusaSlicer 2.x: filament, print and printer .ini files
  -PS3           PrusaSlicer 3 alpha: user presets (.yaml); the mixed-nozzle preset source itself is added in the slicer (see the end of the run)
  -Orca          OrcaSlicer: filament and process .json files
  -OrcaMachines  also the OrcaSlicer machine presets (host, API key and Connect id are blank in the repository: fill them in afterwards)
  -All           -PS2 -PS3 -Orca
  -PS3DataDir    PrusaSlicer 3 data folder, if it is not found automatically (for example "$env:APPDATA\PrusaSlicer3-dev")
  -OrcaUser      OrcaSlicer user folder name under user\ (default: "default")

  Files that already exist are copied to a backup folder before they are overwritten.
#>
param(
  [switch]$PS2, [switch]$PS3, [switch]$Orca, [switch]$OrcaMachines, [switch]$All,
  [string]$PS3DataDir = '', [string]$OrcaUser = 'default'
)
$ErrorActionPreference = 'Stop'
$Repo = $PSScriptRoot
if ($All) { $PS2 = $true; $PS3 = $true; $Orca = $true }
if ($OrcaMachines) { $Orca = $true }
if (-not ($PS2 -or $PS3 -or $Orca)) {
  Write-Host 'Nothing selected. Use -PS2, -PS3, -Orca (with -OrcaMachines) or -All. See the top of install.ps1.'
  exit 1
}

$running = Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -match '^(prusa-slicer|prusa-slicer-console|PrusaSlicer|orca-slicer|OrcaSlicer)$' }
if ($running) {
  Write-Host ('Close the slicer first: ' + (($running | Select-Object -ExpandProperty ProcessName -Unique) -join ', '))
  exit 1
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'

function Copy-Profiles([string]$Src, [string]$Dst, [string]$Filter, [string]$BackupRoot) {
  if (-not (Test-Path $Src)) { Write-Host "  missing in repository: $Src"; return 0 }
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $n = 0
  foreach ($f in Get-ChildItem -LiteralPath $Src -File -Filter $Filter) {
    $target = Join-Path $Dst $f.Name
    if (Test-Path -LiteralPath $target) {
      $bdir = Join-Path $BackupRoot (Split-Path $Dst -Leaf)
      New-Item -ItemType Directory -Force -Path $bdir | Out-Null
      Copy-Item -LiteralPath $target -Destination (Join-Path $bdir $f.Name) -Force
    }
    Copy-Item -LiteralPath $f.FullName -Destination $target -Force
    $n++
  }
  return $n
}

if ($PS2) {
  $d = Join-Path $env:APPDATA 'PrusaSlicer'
  Write-Host "PrusaSlicer 2.x -> $d"
  if (-not (Test-Path (Join-Path $d 'vendor\PrusaResearch.ini'))) {
    Write-Host '  The Prusa Research profiles are not installed. Run PrusaSlicer once and add the CORE One INDX printer in the Configuration Wizard, then run this again.'
  } else {
    $b = Join-Path $d "_backup_install_$Stamp"
    foreach ($sub in 'filament','print','printer') {
      $n = Copy-Profiles (Join-Path $Repo "slicers\prusaslicer-2.x\$sub") (Join-Path $d $sub) '*.ini' $b
      Write-Host "  $sub : $n files"
    }
  }
}

if ($PS3) {
  $d = $PS3DataDir
  if (-not $d) {
    foreach ($c in 'PrusaSlicer3-dev','PrusaSlicer3','PrusaSlicer-3') {
      $p = Join-Path $env:APPDATA $c
      if (Test-Path (Join-Path $p 'presets')) { $d = $p; break }
    }
  }
  if (-not $d -or -not (Test-Path $d)) {
    Write-Host 'PrusaSlicer 3: data folder not found. Start PrusaSlicer 3 once, or pass -PS3DataDir "<folder>".'
  } else {
    Write-Host "PrusaSlicer 3 -> $d"
    $b = Join-Path $d "_backup_install_$Stamp"
    $n = Copy-Profiles (Join-Path $Repo 'slicers\prusaslicer-3-alpha\mixed-nozzles\user-presets') (Join-Path $d 'presets\user\stauc-indx-mixed\StaucINDXMixed') '*.yaml' $b
    Write-Host "  mixed-nozzle user presets: $n files"
    $n = Copy-Profiles (Join-Path $Repo 'slicers\prusaslicer-3-alpha\presets\user\prusa-research-fff\PrusaResearch') (Join-Path $d 'presets\user\prusa-research-fff\PrusaResearch') '*.yaml' $b
    Write-Host "  presets for Prusa's own INDX printer: $n files"
    $zip = Get-ChildItem -LiteralPath (Join-Path $Repo 'slicers\prusaslicer-3-alpha\mixed-nozzles') -Filter 'stauc-indx-mixed_offline_*.zip' | Sort-Object Name | Select-Object -Last 1
    if ($zip) {
      Write-Host ''
      Write-Host '  Next, in PrusaSlicer 3:'
      Write-Host '   1. Configuration > Preset Sources and Updates > Add Zip, pick:'
      Write-Host ('      ' + $zip.FullName)
      Write-Host '   2. Enable the source, add the printer "CORE One INDX Mixed 8T" and set the nozzle of each tool.'
    }
  }
}

if ($Orca) {
  $d = Join-Path $env:APPDATA "OrcaSlicer\user\$OrcaUser"
  Write-Host "OrcaSlicer -> $d"
  if (-not (Test-Path (Join-Path $env:APPDATA 'OrcaSlicer'))) {
    Write-Host '  OrcaSlicer data folder not found. Start OrcaSlicer once, then run this again.'
  } else {
    $b = Join-Path $d "_backup_install_$Stamp"
    $subs = @('filament','process')
    if ($OrcaMachines) { $subs += 'machine' }
    foreach ($sub in $subs) {
      $dst = Join-Path $d $sub
      $n = Copy-Profiles (Join-Path $Repo "slicers\orcaslicer\$sub") $dst '*.json' $b
      foreach ($f in Get-ChildItem -LiteralPath (Join-Path $Repo "slicers\orcaslicer\$sub") -File -Filter '*.json') {
        $info = Join-Path $dst ($f.BaseName + '.info')
        if (-not (Test-Path -LiteralPath $info)) {
          $t = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
          [IO.File]::WriteAllText($info, "sync_info = create`nuser_id = `nsetting_id = `nbase_id = `nupdated_time = $t`n")
        }
      }
      Write-Host "  $sub : $n files"
    }
    if ($OrcaMachines) { Write-Host '  Machine presets: fill in host, API key / Connect id again in OrcaSlicer.' }
    Write-Host '  Orca links filaments to machines by name; the files name the author''s machines ("Prusa CORE One INDX 8T HF 0.4 nozzle" / "Mixed Nozzles", "- LAN" / "- Connect").'
  }
}

Write-Host ''
Write-Host 'Done. Start the slicer again.'

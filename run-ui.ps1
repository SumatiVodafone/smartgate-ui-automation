param(
    [int]$Port = 8501,
    [switch]$DryRun
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$streamlitExe = Join-Path $projectRoot '.venv\Scripts\streamlit.exe'
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'
$appPath = Join-Path $projectRoot 'ui-streamlit\app.py'

if (Test-Path $streamlitExe) {
    $commandDescription = "$streamlitExe run $appPath --server.port $Port"
    if ($DryRun) {
        Write-Host $commandDescription
        exit 0
    }

    & $streamlitExe run $appPath --server.port $Port
    exit $LASTEXITCODE
}

if (Test-Path $pythonExe) {
    $commandDescription = "$pythonExe -m streamlit run $appPath --server.port $Port"
    if ($DryRun) {
        Write-Host $commandDescription
        exit 0
    }

    & $pythonExe -m streamlit run $appPath --server.port $Port
    exit $LASTEXITCODE
}

Write-Error "Could not find Streamlit in .venv. Run: python -m pip install -r ui-streamlit/requirements.txt"
exit 1
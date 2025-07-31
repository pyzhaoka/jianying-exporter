# 验证生成的EXE文件
$exePath = "dist\main.exe"
$minSize = 5MB  # 预期最小文件大小

if (-not (Test-Path $exePath)) {
    Write-Error "EXE file not found at $exePath"
    exit 1
}

$fileInfo = Get-Item $exePath
if ($fileInfo.Length -lt $minSize) {
    Write-Warning "EXE file size suspiciously small ($($fileInfo.Length) bytes)"
}

Write-Output "EXE verification passed:"
Write-Output "Path: $($fileInfo.FullName)"
Write-Output "Size: $([math]::Round($fileInfo.Length/1MB,2)) MB"
Write-Output "Version: $($fileInfo.VersionInfo.FileVersion)"

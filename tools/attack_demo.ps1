# attack_demo.ps1 - simulate benign + malicious traffic for AegisAIR demo
# Run in PowerShell: .\attack_demo.ps1

$base = "http://127.0.0.1:8000"

Write-Host "== 1) Normal page views =="
1..5 | ForEach-Object { Invoke-RestMethod -Uri "$base/" -Method GET > $null; Start-Sleep -Milliseconds 100 }
Write-Host "done."

Write-Host "`n== 2) Normal API requests =="
1..3 | ForEach-Object { Invoke-RestMethod -Uri "$base/api/data?i=$_" -Method GET > $null; Start-Sleep -Milliseconds 100 }
Write-Host "done."

Write-Host "`n== 3) Brute-force login attempts (10 wrong attempts) =="
1..10 | ForEach-Object {
    Invoke-RestMethod -Uri "$base/login" -Method POST -Body @{ user='admin'; pass='wrong' } -ContentType 'application/x-www-form-urlencoded' > $null
    Write-Host -NoNewline "."
    Start-Sleep -Milliseconds 150
}
Write-Host "`n done."

Write-Host "`n== 4) SQL-injection style attempt =="
Invoke-RestMethod -Uri "$base/login" -Method POST -Body @{ user="' OR 1=1 --"; pass='test' } -ContentType 'application/x-www-form-urlencoded' > $null
Write-Host "done."

Write-Host "`n== 5) Admin page access attempt =="
Invoke-RestMethod -Uri "$base/admin" -Method GET > $null
Write-Host "done."

Write-Host "`n== 6) Mix traffic burst =="
1..20 | ForEach-Object {
    switch ($_ % 4) {
        0 { Invoke-RestMethod -Uri "$base/" -Method GET > $null }
        1 { Invoke-RestMethod -Uri "$base/login" -Method POST -Body @{ user='alice'; pass='wrong' } -ContentType 'application/x-www-form-urlencoded' > $null }
        2 { Invoke-RestMethod -Uri "$base/api/data" -Method GET > $null }
        3 { Invoke-RestMethod -Uri "$base/admin" -Method GET > $null }
    }
    Start-Sleep -Milliseconds 50
}
Write-Host "done.`n"

Write-Host "Attack demo finished. Check AegisAIR dashboard for denylist/incidents."

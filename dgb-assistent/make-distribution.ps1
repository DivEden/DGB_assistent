# DGB Assistent Distribution Creator
Write-Host "=== DGB Assistent Distribution Pakke ===" -ForegroundColor Cyan
Write-Host ""

# Create distribution package
$distDir = "DGB-Assistent-Distribution"
if (Test-Path $distDir) {
    Remove-Item $distDir -Recurse -Force
}
New-Item -ItemType Directory -Path $distDir | Out-Null

# Copy files
Copy-Item "dist\DGB-Assistent.exe" "$distDir\" -Force
Copy-Item "install.bat" "$distDir\" -Force
if (Test-Path "README.md") {
    Copy-Item "README.md" "$distDir\LÆSMIG.txt" -Force
}

# Create simple installer instructions
$instructions = @"
=== DGB Assistent Installation ===

For at installere DGB Assistent:

1. Højreklik på 'install.bat'
2. Vælg 'Kør som administrator'  
3. Følg instruktionerne på skærmen

Efter installation kan du finde DGB Assistent ved at:
- Trykke Windows-tasten og søge efter "DGB"
- Gå til Start Menu > Alle Apps > DGB Assistent

=== Manuel Installation ===
Hvis du foretrækker manuel installation:
1. Kopiér DGB-Assistent.exe til en mappe (f.eks. C:\Program Files\DGB Assistent\)
2. Opret en genvej på skrivebordet eller i Start Menu

=== Funktioner ===
- Simpel Billedkomprimering (komprimér til KB størrelse)
- Gruppe Billedbehandler (gruppér og navngiv a, b, c...)
- Individuel Billedbehandler (navngiv hvert billede)
- Museum Organisering (automatisk til korrekte mapper)

=== Support ===
For hjælp og opdateringer: https://github.com/diveden/dgb-assistent
"@

$instructions | Out-File -FilePath "$distDir\Installation Guide.txt" -Encoding UTF8

Write-Host "Distribution pakke oprettet: $distDir" -ForegroundColor Green
Write-Host "Du kan nu ZIP'e denne mappe og dele den med brugere!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Indeholder:" -ForegroundColor Yellow
Get-ChildItem $distDir | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
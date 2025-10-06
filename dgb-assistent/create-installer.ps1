# DGB Assistent Windows Installer Creator
# Dette script opretter en professionel Windows installer (.msi)

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = ".\installer"
)

# Check if WiX Toolset is available
$wixPath = Get-Command "candle.exe" -ErrorAction SilentlyContinue
if (-not $wixPath) {
    Write-Host "WiX Toolset ikke fundet. Installér WiX Toolset fra: https://wixtoolset.org/" -ForegroundColor Red
    Write-Host "Alternativt kan du bruge install.bat scriptet i stedet." -ForegroundColor Yellow
    exit 1
}

# Create installer directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Create WiX source file
$wixContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="DGB Assistent" 
           Language="1033" 
           Version="$Version" 
           Manufacturer="DivEden" 
           UpgradeCode="{12345678-1234-1234-1234-123456789012}">
    
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="En nyere version af [ProductName] er allerede installeret." />
    
    <MediaTemplate EmbedCab="yes" />
    
    <Feature Id="ProductFeature" Title="DGB Assistent" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <!-- Directory structure -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="DGB Assistent" />
      </Directory>
      <Directory Id="ProgramMenuFolder">
        <Directory Id="ApplicationProgramsFolder" Name="DGB Assistent" />
      </Directory>
    </Directory>
    
    <!-- Components -->
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="{87654321-4321-4321-4321-210987654321}">
        <File Id="DGBAssistentEXE" 
              Source="dist\DGB-Assistent.exe" 
              KeyPath="yes" 
              Checksum="yes" />
      </Component>
    </ComponentGroup>
    
    <!-- Start Menu Shortcut -->
    <DirectoryRef Id="ApplicationProgramsFolder">
      <Component Id="ApplicationShortcut" Guid="{11111111-2222-3333-4444-555555555555}">
        <Shortcut Id="ApplicationStartMenuShortcut"
                  Name="DGB Assistent"
                  Description="Billedbehandling og Museum Organisering"
                  Target="[#DGBAssistentEXE]"
                  WorkingDirectory="INSTALLFOLDER" />
        <RemoveFolder Id="CleanUpShortCut" Directory="ApplicationProgramsFolder" On="uninstall" />
        <RegistryValue Root="HKCU" 
                       Key="Software\Microsoft\DGB Assistent" 
                       Name="installed" 
                       Type="integer" 
                       Value="1" 
                       KeyPath="yes" />
      </Component>
    </DirectoryRef>
  </Product>
</Wix>
"@

$wixFile = Join-Path $OutputDir "DGBAssistent.wxs"
$wixContent | Out-File -FilePath $wixFile -Encoding UTF8

Write-Host "WiX source fil oprettet: $wixFile" -ForegroundColor Green

# Compile with candle
$objFile = Join-Path $OutputDir "DGBAssistent.wixobj"
& candle.exe -out $objFile $wixFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "WiX compilation successful" -ForegroundColor Green
    
    # Link with light
    $msiFile = Join-Path $OutputDir "DGB-Assistent-$Version.msi"
    & light.exe -out $msiFile $objFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Windows Installer oprettet: $msiFile" -ForegroundColor Green
        Write-Host "Du kan nu distribuere denne .msi fil til brugere!" -ForegroundColor Cyan
    } else {
        Write-Host "Light linking fejl" -ForegroundColor Red
    }
} else {
    Write-Host "Candle compilation fejl" -ForegroundColor Red
}
"@

$installerScript = @"
# Simple PowerShell installer creator
# Run this if you don't have WiX Toolset

Write-Host "=== DGB Assistent Distribution Pakke ===" -ForegroundColor Cyan
Write-Host ""

# Create distribution package
`$distDir = "DGB-Assistent-Distribution"
if (Test-Path `$distDir) {
    Remove-Item `$distDir -Recurse -Force
}
New-Item -ItemType Directory -Path `$distDir | Out-Null

# Copy files
Copy-Item "dist\DGB-Assistent.exe" "`$distDir\" -Force
Copy-Item "install.bat" "`$distDir\" -Force
Copy-Item "README.md" "`$distDir\LÆSMIG.txt" -Force -ErrorAction SilentlyContinue

# Create simple installer instructions
`$instructions = @"
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

=== Support ===
For hjælp og opdateringer: https://github.com/diveden/dgb-assistent
"@

`$instructions | Out-File -FilePath "`$distDir\Installation Guide.txt" -Encoding UTF8

Write-Host "Distribution pakke oprettet: `$distDir" -ForegroundColor Green
Write-Host "Du kan nu ZIP'e denne mappe og dele den med brugere!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Indeholder:" -ForegroundColor Yellow
Get-ChildItem `$distDir | ForEach-Object { Write-Host "  - `$(`$_.Name)" }
"@

$installerScript | Out-File -FilePath "create-installer.ps1" -Encoding UTF8
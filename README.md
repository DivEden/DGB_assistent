# DGB Assistent

DGB Assistent er et Python-baseret desktop program udviklet til billedbehandling og museum organisering. Programmet tilbyder fire hovedfunktioner til effektiv håndtering af digitale billedsamlinger.

## Funktioner

**Simpel Billedkomprimering**
Komprimerer billeder til en specifik filstørrelse i KB med automatisk kvalitetsjustering.

**Gruppe Billedbehandler** 
Batch-behandling af billedsamlinger med systematisk navngivning og organisering.

**Individuel Billedprocessor**
Avanceret billedbehandling med filters og tilpassede indstillinger for enkelte billeder.

**Museum Organisering**
Specialiseret værktøj til katalogisering og organisering af museums billedsamlinger.

## Axiell Integration

Programmet understøtter integration med Axiell WebAPI til museum databaser. API-credentials kan konfigureres gennem programmets interface.

## Installation og Brug

Kør den medfølgende `DGB-Assistent.exe` fil. Programmet kræver ingen installation og fungerer som en standalone applikation.

## Udvikling

### Forudsætninger
- Python 3.8 eller nyere
- Alle dependencies fra `requirements.txt`

### Setup
```bash
# Klon repository
git clone https://github.com/DenGamleBy2025/dgb-assistent.git
cd dgb-assistent

# Opret virtual environment
python -m venv .venv
.venv\Scripts\activate

# Installer dependencies
pip install -r requirements.txt
```

### Kør programmet
```bash
python src/main.py
```

### Byg executable

**Windows:**
```bash
# Brug PowerShell script (anbefalet)
.\build.ps1

# Eller batch fil
.\build.bat

# Eller direkte PyInstaller
pyinstaller build.spec
```

Den færdige executable findes i `dist/DGB-Assistent.exe` efter succesfuld bygning.

### Projektstruktur
```
src/
├── main.py              # Entry point
├── config.py            # Konfiguration
├── gui/
│   └── main_window.py   # Hovedinterface
├── apps/image_tools/    # Billedbehandlings moduler
├── utils/               # Hjælpefunktioner og API
└── assets/              # Styling og ressourcer
```

## Licens

MIT License - se LICENSE fil for detaljer.
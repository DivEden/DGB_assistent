# 🚀 DGB Assistent

**En moderne dansk applikationslauncher og digitalt arbejdsområde**

DGB Assistent er en professionel desktop-applikation bygget med Python og Tkinter, designet til at fungere som en central hub for dine vigtigste arbejdsværktøjer.

![DGB Assistent](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12+-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Funktioner

- 🎨 **Moderne Design** - Elegant brugergrænse med premium farver og animationer
- 🚀 **Automatiske Opdateringer** - Seamless opdateringer direkte fra GitHub
- ⚙️ **Indstillinger** - Fuld brugerkontrol over app-præferencer og opdateringer
- 🔍 **Søgefunktion** - Hurtig navigation mellem apps og funktioner
- 📱 **Responsiv** - Tilpasser sig forskellige skærmstørrelser
- 🛡️ **Sikkerhed** - Automatisk backup før opdateringer
- 🇩🇰 **Dansk** - Komplet lokalisering til danske brugere

## 🖥️ For Slutbrugere

### Installation
1. Download den seneste version fra [Releases](https://github.com/diveden/dgb-assistent/releases)
2. Kør `DGB-Assistent.exe` - ingen installation påkrævet!
3. Applikationen tjekker automatisk for opdateringer

### Funktioner
- **App Launcher** - Hurtig adgang til dine værktøjer
- **Kategorisering** - Organiser apps efter type
- **Indstillinger** - Konfigurer opdateringer og præferencer
- **Auto-Update** - Få automatisk besked om nye versioner

## 👨‍💻 For Udviklere

### Opsætning
```bash
# 1. Klon repository
git clone https://github.com/diveden/dgb-assistent.git
cd dgb-assistent

# 2. Opret virtuelt miljø
python -m venv .venv
.venv\Scripts\activate

# 3. Installer dependencies
pip install -r requirements.txt

# 4. Kør applikationen
python src/main.py
```

### Bygning af Executable
```bash
# Windows
.\build.bat

# Eller manuelt med PyInstaller
pyinstaller --onefile --windowed --name="DGB-Assistent" src/main.py
```

## 🏗️ Projekt Struktur

```
dgb-assistent/
├── src/
│   ├── main.py                 # Applikations entry point
│   ├── config.py              # Konfiguration og indstillinger
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py     # Hoved GUI interface
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py         # Hjælpefunktioner
│   │   ├── settings.py        # Indstillingshåndtering
│   │   └── updater.py         # Auto-update system
│   └── assets/
│       └── styles.css         # Styling
├── build/                     # Byggeresultater
├── requirements.txt           # Python dependencies
├── build.bat                  # Windows byggescript
├── AUTO_UPDATE_SETUP.md       # Auto-update guide
└── README.md                  # Denne fil
```

## 🔧 Teknisk Stack

- **Python 3.12+** - Kernesprog
- **Tkinter** - GUI framework
- **PyInstaller** - Executable packaging
- **Requests** - HTTP requests til auto-updates
- **Pillow** - Billedbehandling

## 🚀 Auto-Update System

DGB Assistent inkluderer et professionelt auto-update system:

- ✅ Automatisk GitHub release checking
- ✅ Elegant update notifikationer på dansk
- ✅ En-klik download og installation
- ✅ Sikkerhedsbackup før opdateringer
- ✅ Brugerindstillinger for opdateringsfrekvens

### Opsætning af Updates (For Udviklere)

1. **Opdater version** i `src/config.py`:
   ```python
   APP_VERSION = "1.1.0"
   ```

2. **Byg ny executable**:
   ```bash
   .\build.bat
   ```

3. **Opret GitHub Release**:
   - Tag: `v1.1.0`
   - Upload `DGB-Assistent.exe` i en ZIP-fil
   - Alle brugere får automatisk besked!

Se `AUTO_UPDATE_SETUP.md` for detaljeret guide.

## 🎨 Design Philosophy

DGB Assistent følger moderne design-principper:

- **Minimal & Clean** - Fokus på funktionalitet
- **Premium Farver** - #002852 blå og hvid tema
- **Responsiv** - Fungerer på alle skærmstørrelser
- **Dansk UX** - Designet specifikt til danske brugere
- **Professionel** - Matcher kommercielle applikationers kvalitet

## 📋 Kommende Funktioner

- [ ] Plugin system til tredjepartsapps
- [ ] Mørkt tema
- [ ] Keyboard shortcuts
- [ ] Export/import af indstillinger
- [ ] Performance dashboard
- [ ] Integration med Windows services

## 🤝 Bidrag

1. Fork repository
2. Opret feature branch (`git checkout -b feature/ny-funktion`)
3. Commit ændringer (`git commit -am 'Tilføj ny funktion'`)
4. Push til branch (`git push origin feature/ny-funktion`)
5. Opret Pull Request

## 📄 Licens

Dette projekt er licenseret under MIT License - se [LICENSE](LICENSE) filen for detaljer.

## 📞 Support

- 🐛 **Bug Reports**: [Issues](https://github.com/diveden/dgb-assistent/issues)
- 💡 **Feature Requests**: [Discussions](https://github.com/diveden/dgb-assistent/discussions)
- 📧 **Kontakt**: Opret et issue for support

## 📈 Changelog

### v1.0.0 (Oktober 2025)
- 🎉 Første release af DGB Assistent
- ✅ Moderne GUI med premium design
- ✅ Auto-update system med GitHub integration
- ✅ Komplet indstillingspanel
- ✅ Dansk lokalisering
- ✅ Standalone executable

---

**Bygget med ❤️ af diveden | Designet til danske brugere 🇩🇰**
# SARA Upload System - Brugervejledning

## Oversigt

DGB Assistent indeholder nu et integreret SARA upload system, der automatisk uploader komprimerede billeder til SARA's billedserver og genererer en CSV import-fil.

## Hvordan det virker

### 1. Billedbehandling
Alle tre apps (Individuel, Gruppe, Simpel) behandler dine billeder og opretter:
- **Small/komprimerede versioner** (ca. 300 KB) - bruges til SARA upload
- **Large/høj kvalitet versioner** - bruges til lokal lagring

### 2. SARA Upload Proces

Når du klikker "Gem i SARA" knappen:

1. **Login til SARA API**
   - Systemet logger automatisk ind med DGB's credentials
   - Bruger Basic Authentication

2. **Upload billeder**
   - Hver komprimeret billedfil får et unikt UUID filnavn (f.eks. `a1b2c3d4-5678-90ab-cdef-1234567890ab.jpg`)
   - Billederne uploades til SARA's billedserver via `writecontent` kommandoen
   - Original filnavn gemmes til reference

3. **Generér CSV import-fil**
   - Systemet opretter en CSV fil med følgende kolonner:
     - `IN` - Inventory Number (objektnummer, f.eks. 0054x0007)
     - `FN` - File Name (UUID filnavnet på serveren)
   
   - CSV filen gemmes på dit skrivebord med timestamp
   - Format: **Semicolon-separated**, UTF-8 with BOM

4. **Manuel redigering i SARA**
   - "Vis offentligt" og "Licenstype" er visningsfelter (computed fields)
   - De kan IKKE importeres via CSV
   - Du skal indstille disse manuelt i SARA efter import

### 3. Import til SARA

Efter upload skal du:

1. Åbn SARA i din browser
2. Gå til Import funktionen
3. Vælg den genererede CSV fil fra dit skrivebord
4. Import til `collection` databasen
5. Billederne linkes automatisk via UUID reference
6. **Rediger manuelt**: Sæt "Vis offentligt" og "Licenstype" for hver billedfil i SARA

## Understøttede Objektnummer Formater

Systemet genkender automatisk følgende formater i filnavne:

- **Traditionelt**: `0054x0007`, `1234X4321`
- **Genstands format**: `00073;15`, `12345;2015`
- **AAB format**: `AAB 1234`
- **Standalone**: `1234`

### Eksempler på gyldige filnavne:
- `0054x0007.jpg`
- `AAB 1234 a.jpg`
- `00073;15.jpg`

## Tekniske Detaljer

### API Endpoint
```
https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx
```

### Authentication
- Method: HTTP Basic Authentication
- Username: `adlibhosting\DGB-API-USER`
- Password: (gemt sikkert i koden)

### Upload Kommandoer
```
POST /wwwopac.ashx?command=writecontent&server=images&value={UUID_FILENAME}
Content-Type: image/jpeg
Body: {BINARY_IMAGE_DATA}
```

### CSV Import Format
```csv
IN;FN;mu;Fl
0054x0007;a1b2c3d4-5678-90ab-cdef-1234567890ab.jpg;x;Public Domain - PD
```

**Vigtigt**: SARA bruger **semikolon** (`;`) som separator, IKKE komma!

**Field Codes:**
- `IN` = Inventory Number (objektnummer)
- `FN` = File Name (mediefil.reference - UUID filename)
- `mu` = Vis offentligt (x = ja, blank = nej)
- `Fl` = Licenstype (note: lowercase 'l')

### Licenstype Valgmuligheder

Efter import kan du manuelt vælge mellem disse i SARA:
- Public Domain - PD
- Creative Commons - CC BY-NC-ND
- Creative Commons - CC BY-NC-SA
- Creative Commons - CC BY-ND
- Creative Commons - CC BY-NC
- Creative Commons - CC BY-SA
- Creative Commons - CC BY
- No Known Copyright - NKC
- Copyright - C

### Vis Offentligt
- **Ja** = Billedet vises offentligt
- **Nej** = Billedet vises ikke offentligt

**Bemærk**: Disse felter skal sættes manuelt i SARA efter CSV import.

## Fejlfinding

### "Ingen objektnumre fundet"
- Sørg for at dine filnavne indeholder gyldige objektnumre
- Brug format som `0054x0007` eller `AAB 1234`

### "Upload fejlede"
- Tjek din internetforbindelse
- Kontakt support hvis problemet fortsætter

### "CSV import fejler i SARA"
- Kontroller at CSV filen er korrekt formateret
- Tjek at objektnumrene eksisterer i SARA
- Sørg for at database navnet er `collection`

## Support

Hvis du oplever problemer:
1. Tjek at alle filnavne har gyldige objektnumre
2. Kontroller internetforbindelse
3. Kontakt DGB support med fejlbeskeder

---

**Version**: 1.0
**Sidst opdateret**: 2024

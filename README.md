# Pizza Station Ares

2D akční roguelike hra z pohledu shora inspirovaná hrou *The Binding of Isaac*. Hra je zasazená do pizzerie na Marsu a běží v reálném čase (60 FPS).

## Autoři a rozdělení práce

- **Lukáš Kráčmar** - programování hry, herní logika, generování místností, databáze účtů, automatické testy
- **Linda Matušková** - kompletní dokumentace projektu (`README.md`, `DESIGN_DOKUMENT.md`, ruční testovací scénář, kontrola odevzdání)

## Popis hry

Píše se rok 2097 a pracuješ jako kuchař na vesmírné pizzerii na Marsu. V kuchyni se ale něco pokazilo - suroviny zmutovaly, rozvážkové drony se zbláznily a základnu obsadily vesmírné ančovičky.

Úkolem je projít **5 pater** stanice, vyčistit jednotlivé místnosti od nepřátel, posbírat lepší vybavení a v posledním 5. patře porazit hlavního bosse (**Giant Calzone**). Když vstoupíš do místnosti s nepřáteli, dveře se zamknou a otevřou se až ve chvíli, kdy všechny v místnosti porazíš. Na každém patře je taky sklad se zásobami (`$` na minimapě) a místnost s bossem patra (`B`), po kterém se otevře poklop do dalšího patra. Když ti dojdou životy (HP), hra končí a jedeš od prvního patra znovu (permadeath).

Součástí hry je i hlavní menu s nastavením rozlišení a kvality grafiky, ukládání rozehrané hry a přihlašování k účtům přes databázi.

## Použité technologie

- **Python 3** (testováno na Pythonu 3.10+) - hlavní programovací jazyk
- **Pygame-CE (`pygame-ce`)** - vykreslování 2D grafiky, herní smyčka 60 FPS, vstupy z klávesnice a myši
- **SQLite3 (`sqlite3`) + `hashlib`** (ze standardní knihovny Pythonu) - ukládání uživatelských účtů, zahashovaných hesel (SHA-256), statistik a rozehraných her do souboru `accounts.db`
- **JSON (`json`)** - ukládání nastavení a hry pro nepřihlášeného hráče (Guest)
- **`unittest`** - automatické testy herní logiky, databáze a bota, který hru testuje
- **Git** - verzování projektu
- **AI asistent** - pomoc při psaní kódu, generování 16x16 pixel art spritů ve `sprites.py` a ladění chyb

Hra nepotřebuje stahovat žádné externí obrázky - všechny sprity se skládají přímo z kódu při startu a databáze se sama vytvoří při prvním spuštění.

## Postup spuštění (na cizím počítači)

Před spuštěním je potřeba mít nainstalovaný **Python 3** (verze 3.10 nebo novější) a naklonovaný nebo rozbalený tento repozitář.

### Windows (PowerShell nebo Příkazový řádek)

Otevři terminál ve složce s projektem a zadej:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Linux / macOS

Otevři terminál ve složce s projektem a zadej:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

*(Pokud už je virtuální prostředí `.venv` vytvořené a nainstalované, stačí příště spustit jen `.venv\Scripts\python main.py` na Windows nebo `.venv/bin/python main.py` na Linuxu/Macu.)*

## Ovládání

| Klávesa / Myš | Akce |
|---|---|
| **W, A, S, D** nebo **Šipky** | Pohyb postavy (v menu přepínání položek) |
| **Pohyb myší** | Míření zbraní / klikání na tlačítka v menu |
| **Levé tlačítko myši (LMB)** | Střelba směrem ke kurzoru (dá se držet) |
| **H / E / Pravé tlačítko myši** | Sníst kousek pizzy (doplní +8 HP) |
| **F5** | Rychlé uložení rozehrané hry |
| **M** | Uložit hru a vrátit se do hlavního menu |
| **L** | Otevřít přihlášení / registraci (v hlavním menu) |
| **R / Enter** | Nová hra po smrti nebo po výhře |
| **ESC** | Uložit a ukončit hru (v podmenu návrat zpět) |

## Účty a ukládání postupu

- V pravém dolním rohu hlavního menu je tlačítko **LOGIN / SIGN UP**.
- **Registrace (Sign Up)** vytvoří nový účet v SQLite databázi `accounts.db`.
- **Přihlášení (Log In)** načte uloženou rozehranou hru, nejvyšší skóre, nejvyšší dosažené patro a nastavení grafiky/rozlišení pro daný účet.
- **Testovací účet pro vyzkoušení:** jméno `admin`, heslo `admin`. Má hotový plný postup (skóre 9999, připravený save rovnou v 5. patře před bossem a každá nová hra začíná s nejlepší výbavou - Pizza Cutter, zástěra a 35 HP).
- Bez přihlášení se hraje jako **Guest** (rozehraná hra se ukládá lokálně do `savegame.json`).

## Testování

### 1. Automatické testy

V projektu je sada 18 automatických testů v `tests/test_game.py` (kontrolují generování pater a průchodnost místností, kolize, střelbu, sbírání předmětů, ukládání, registraci/přihlášení v databázi a obsahují i bota, který sám odehraje 60 her).

Spuštění testů (s aktivovaným `.venv`):

```bash
python -m unittest discover -s tests -v
```

### 2. Ruční testovací scénář

1. Spusť hru příkazem `python main.py` - mělo by se otevřít hlavní menu s vesmírným pozadím.
2. Klikni vpravo dole na **LOGIN / SIGN UP**, zadej `admin` / `admin` a klikni na **LOG IN** - v menu se dole zobrazí `ACCOUNT: admin`.
3. Jdi do **SETTINGS**, zkus přepnout rozlišení a kvalitu grafiky a vrať se přes **SAVE & BACK TO MENU**.
4. Klikni na **PLAY -> LOAD SAVED GAME** - načte se 5. patro s 35 HP a zbraní Pizza Cutter.
5. Vyzkoušej pohyb přes **WASD**, míření myší a střelbu **levým tlačítkem myši**.
6. Dojdi podle minimapy vpravo do místnosti označené `B` (Boss) a zkus souboj s Giant Calzone (při zranění se dá vyléčit pizzou přes **H** nebo pravé tlačítko myši).
7. Stiskni **M** pro uložení a návrat do menu a v **PLAY -> START NEW GAME** ověř, že jde normálně rozjet novou hru od 1. patra.

## Přehled souborů v projektu

| Soubor | Co dělá |
|---|---|
| `main.py` | Okno hry, vykreslování místností, minimapy a menu, vstupy z klávesnice a myši |
| `game.py` | Pravidla hry: pohyb, kolize, střelba, zamykání místností, AI nepřátel, ukládání |
| `database.py` | SQLite databáze účtů (registrace, přihlášení, statistiky, admin účet) |
| `dungeon.py` | Generování náhodných propojených místností, dveří a nábytku |
| `entities.py` | Třídy pro hráče, nepřátele a projektily |
| `items.py` | Definice předmětů a zbraní |
| `sprites.py` | Všechny 16x16 pixel art sprity, podlahy, zdi a dekorace |
| `settings.py` | Nastavení konstant (rozměry okna, rychlosti, HP, cooldowny) |
| `tests/test_game.py` | Automatické testy hry a databáze |
| `DESIGN_DOKUMENT.md` | Návrhový dokument ke hře |
| `DENIK_SELHANI_AI.md` | Záznam případů, kdy AI udělala chybu nebo něco nevhodného, a jak jsem to řešil |
| `RETROSPEKTIVA.md` | Krátké zhodnocení práce na projektu a práce s AI |

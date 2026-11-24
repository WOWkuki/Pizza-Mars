# Design dokument - Pizza Station Ares

**Autoři:** Lukáš Kráčmar (vývoj hry), Linda Matušková (dokumentace)  
**Žánr:** 2D akční roguelike (top-down shooter)  
**Téma:** Pizzerie na Marsu  

---

## 1. Základní koncept a příběh

**Pizza Station Ares** je 2D pixel-artová akční roguelike hra z pohledu shora. Hratelností vychází hlavně ze hry *The Binding of Isaac* - hráč prochází náhodně vygenerované patro složené z jednotlivých místností, střílí myší po nepřátelích a sbírá vylepšení.

Děj se odehrává v roce 2097 na orbitální/marsovské pizzerii. Suroviny v kuchyni zmutovaly, rozvážkové drony začaly útočit na personál a stanici zaplavily vesmírné ančovičky. Hráč hraje za posledního kuchaře na směně, který se musí probojovat přes 5 pater stanice až k hlavnímu bossovi, kterým je obří oživlé **Giant Calzone**.

## 2. Hlavní herní mechaniky (Core Loop)

1. **Průchod po místnostech:** Jedna místnost vždy zabírá celou herní obrazovku (mřížka 19x13 dlaždic). Mezi místnostmi se přechází dveřmi na severu, jihu, východě a západě.
2. **Zamykání dveří:** Pokud jsou v místnosti nepřátelé, dveře se po vstupu zamknou. Odemknou se až ve chvíli, kdy hráč všechny nepřátele v místnosti zabije. Za vyčištění místnosti se hráči doplní 1 HP a občas vypadne kousek pizzy.
3. **Boj v reálném čase:** Hráč se plynule pohybuje pomocí kláves `WASD`, míří kurzorem myši a střílí levým tlačítkem myši. Po zásahu má hráč krátkou dobu nesmrtelnosti (i-frames), aby nedostal několik zásahů během jedné vteřiny.
4. **Speciální místnosti a postup patry:**
   - **Startovní místnost** - bezpečná místnost, kde hráč začíná patro.
   - **Sklad / Supply Room (`$`)** - místnost bez nepřátel, kde leží zbraň nebo vylepšení.
   - **Boss místnost (`B`)** - na patrech 1 až 4 je v ní silnější strážce patra. Po jeho zabití se uprostřed otevře žlutý poklop (hatch) do dalšího patra. Na 5. patře tu čeká finální boss Giant Calzone.
5. **Permadeath a ukládání:** Když hráči klesnou životy na 0, run končí a uložená rozehraná hra se smaže. Pokud ale hráč hru jen vypne nebo odejde do menu (`M` / `F5`), rozehraný postup se uloží a dá se v něm pokračovat přes *Load Saved Game*.

## 3. Nepřátelé a Boss

Každý typ nepřítele má vlastní chování (AI), aby souboje nebyly pořád stejné:

- **Mutant Meatball (Zmutovaný masový knedlíček):** Základní nepřítel, který se kymácí a jde přímo po hráči na blízko.
- **Rogue Delivery Drone (Zblázněný rozvážkový dron):** Drží si od hráče odstup, poletuje do stran a střílí po kuchaři laserové střely.
- **Alien Anchovy (Vesmírná ančovička):** Rychlejší nepřítel, který hráče pronásleduje a v pravidelných intervalech dělá rychlý výpad (lunge).
- **Giant Calzone (Finální boss v 5. patře):** Má hodně životů, vystřeluje vějíř tří střel roztaveného sýra najednou a občas do místnosti vyplivne další Mutant Meatballs.

Statistiky nepřátel (životy a útok) se postupně zvyšují podle toho, v jakém patře hráč zrovna je.

## 4. Zbraně a předměty

Hráč začíná se základní zbraní (*Hot Dough Launcher* - střílí kousky horkého těsta) a základní kuchařskou uniformou. Cestou může najít:

- **Pizza Slice (Kousek pizzy):** Uloží se do inventáře. Po stisknutí `H`, `E` nebo pravého tlačítka myši vyléčí +8 HP.
- **Oxygen Tank (Kyslíková bomba):** Zvýší maximální životy o +5 HP a rovnou o 5 HP doléčí.
- **Rolling Pin (Váleček na těsto):** Lepší zbraň (+2 poškození, rychlejší střelba). Garantovaně padá v 1. patře ve skladu.
- **Pizza Cutter (Kráječ na pizzu):** Nejlepší zbraň ve hře (+4 poškození, střílí rotující ocelové kotouče s vyšší kadencí).
- **Heat-Shield Apron (Žáruvzdorná zástěra):** Zbroj, která dává +2 obranu (snižuje obdržené poškození).
- **Mars Credits (Kredity):** Měna, která padá z nepřátel a v místnostech, započítává se do celkového skóre.

Pokud hráč sebere zbraň nebo zbroj, kterou už má (nebo slabší), automaticky se prodá za 5 kreditů.

## 5. Prostředí, grafika a UI

- **Vizuální styl:** 2D pixel art v rozlišení 16x16 pixelů na dlaždici/postavu, který se ve hře vykresluje 3x zvětšený (48x48 px). Všechny sprity jsou definované přímo v kódu (`sprites.py`) pomocí barevné palety. Místnosti mají různé styly (kuchyně, jídelna s červenobílými ubrusy, mrazák, sklad, marsovský prach) a generuje se v nich nábytek (velké jídelní stoly se stoličkami, kuchyňské pulty, pece na pizzu, mrazáky, bedny, okna s výhledem na Mars a neonové nápisy).
- **Animace:** Kuchař i nepřátelé mají dvoufázovou animaci pohybu, kuchař drží v ruce aktuální zbraň natočenou směrem ke kurzoru myši (včetně zpětného rázu a záblesku při výstřelu) a v pecích bliká oheň.
- **Uživatelské rozhraní (UI):**
  - Vlevo je samotná místnost (912x624 px), vpravo boční panel (300 px) s ukazatelem patra, HP barem, výbavou, počtem pizz, kredity, **minimapou patra** a výpisem zpráv z boje.
  - **Hlavní menu:** Tlačítka *Play* (výběr mezi *Load Saved Game* a *Start New Game*), *Settings* (změna rozlišení okna a kvality grafiky Low/Medium/High), *Quit* a vpravo dole přihlášení k účtu (*Login / Sign Up*).

## 6. Systém účtů a technické rozdělení

Aby mělo smysl hru hrát opakovaně a šel snadno testovat konec hry, přidali jsme přihlašovací systém napojený na lokální **SQLite databázi** (`accounts.db`):
- Hráč si může zaregistrovat vlastní účet (heslo se ukládá jako SHA-256 hash). Ke každému účtu se ukládá nejvyšší skóre, nejvyšší patro, počet výher, nastavení a aktuálně rozehraná hra.
- Pro testování je v databázi předpřipravený účet `admin` / `admin`, který má plný postup a uloženou pozici v 5. patře.

Projekt je rozdělený tak, aby herní logika nebyla zamíchaná do vykreslování:
- `settings.py` - konstanty a nastavení
- `dungeon.py` - generátor patra, místností, dveří a překážek
- `entities.py` a `items.py` - datové třídy pro hráče, monstra, střely a itemy
- `game.py` - čistá herní logika bez Pygame vykreslování (díky tomu jdou snadno pouštět automatické testy)
- `database.py` - práce se SQLite databází účtů
- `sprites.py` - pixel art sprity
- `main.py` - Pygame okno, menu, vykreslování a ovládání

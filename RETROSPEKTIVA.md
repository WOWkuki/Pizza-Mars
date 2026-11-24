# Retrospektiva

**Jméno:** Lukáš Kráčmar (týmový projekt s Lindou Matuškovou)  
**Projekt:** Pizza Station Ares  

Na projektu jsme pracovali ve dvou - já jsem řešil hlavně samotné programování hry a Linda Matušková vzala kompletní dokumentaci (README, design dokument, testovací scénář a kontrolu zadání), což nám hodně ušetřilo čas před odevzdáním.

## Co bych příště udělal jinak

- **Líp si ujasnit zadání hned na začátku:** Na startu jsem napsal dost obecně, že chci roguelike z pizzerie na Marsu, a neřekl jsem rovnou, že to nechci na tahy, ale v reálném čase s mířením myší jako v Isaacovi. Muselo se to pak celé předělávat z tahové hry na real-time, čemuž bych se příště vyhnul, kdybych si ovládání a styl promyslel předem.
- **Nepřidávat věci jen do počtu:** Chtěl jsem víc odemykatelných map, aniž bych měl vymyšlené, v čem se budou doopravdy lišit. Zbytečně jsme tím strávili čas a nakonec jsem je stejně nechal smazat, protože to bylo pořád to samé pod jiným názvem. Příště bych radši rovnou dělal míň věcí, ale pořádně.
- **Zvuky a hudba:** Na začátku jsem si říkal, že zvuky dořeším později, ale nakonec jsme řešili předělávku soubojů, nábytek v místnostech, opravu rozlišení a přihlašování do databáze, takže na zvuky už nedošlo. Příště bych si na ně nechal čas před koncem projektu.

## Kde AI pomohla

- **Grafika a pixel art v kódu:** Nejsem grafik a kreslit ručně desítky spritů (kuchaře, monstra, animace chůze, stoly, pece, zbraně) by mi zabralo strašně moc času. AI dokázala poskládat 16x16 pixel art přímo přes textové mřížky ve `sprites.py`, což vypadá ve hře překvapivě dobře.
- **Matematika a kolize:** Hodně mi ušetřila práci u věcí jako otáčení držené zbraně pod úhlem ke kurzoru myši (`atan2`), počítání vektorů střel, klouzání postav podél překážek nebo generování propojených místností tak, aby vždycky existovala cesta k bossovi.
- **Databáze a automatické testy:** Rychle pomohla připravit ukládání účtů do SQLite databáze (`database.py`) včetně hashování hesel a napsat automatické testy s botem, který hru projede mockrát za sebou a odhalí, jestli se někde nedá zaseknout.
- **Vysvětlení Gitu:** Na začátku jsem Gitu moc nerozuměl a AI mi pomohla nastavit repozitář, `.gitignore` a průběžně ukládat hotové kroky do commitů.

## Kde AI překážela

- **Domýšlí si věci po svém, když je zadání krátké:** Když člověk nenapíše přesně, jak si něco představuje, AI si vybere vlastní cestu (jako s tou tmavou tahovkou na začátku) a pak se musí spousta kódu přepisovat.
- **Generuje věci „naoko“:** U těch 4 map AI sice splnila zadání na papíře (přidala 4 mapy a odemykání), ale reálně do hry nepřidala nic nového, jen přebalila to samé do jiných názvů. Člověk jí musí kontrolovat, jestli to fakt dává herně smysl.
- **Nepočítá se specifickým prostředím na PC:** AI testovala kód jen v bezhlavém (headless) režimu a nenapadlo ji, že na Linuxu s dlaždicovým správcem oken (Hyprland) má okno jinou velikost, než jakou si hra vyžádá, takže změna rozlišení u mě na počítači okamžitě spadla.
- **Velké kusy kódu najednou:** AI občas vychrlí stovky řádků v jednom kroku, takže když pak chci pochopit, kde přesně se co děje (kvůli úpravám nebo obhajobě), musím si ty soubory zpětně projít a pročíst.

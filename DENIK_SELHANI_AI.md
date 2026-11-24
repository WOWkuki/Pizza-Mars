# Deník selhání AI

**Jméno:** Lukáš Kráčmar  
**Projekt:** Pizza Station Ares  

Během vývoje hry jsem používal AI asistenta na generování kódu, spritů a úpravy mechanik. Níže jsou konkrétní případy, kdy AI udělala něco špatně, nepochopila záměr nebo vyrobila chybu, na kterou jsem přišel při testování.

---

## Případ 1: Tahová hra ve tmě místo akční střílečky + přepálená obtížnost

- **Co jsem chtěl:** Chtěl jsem udělat 2D roguelike z pizzerie na Marsu, který se bude hrát svižně a akčně (podobně jako *The Binding of Isaac*), kde dobře uvidím na místnost.
- **Co AI udělala špatně:** Protože jsem na začátku napsal jen „roguelike“, AI automaticky udělala staromódní tahovou hru na čtverečkové síti, kde se nepřátelé pohnuli jen když jsem udělal krok. Navíc přidala hodně malé zorné pole (FOV), takže většina obrazovky byla černá a bylo vidět jen pár políček kolem kuchaře. V úplně prvním nástřelu taky nastavila nepřátelům moc vysoké staty, takže ani testovací bot nedokázal vyhrát jedinou hru ze 150 pokusů.
- **Jak jsem to poznal:** Poznal jsem to jednak z výsledků testovacího bota (0 výher ze 150 her) a hlavně hned jak jsem hru poprvé sám zapnul - trhaný pohyb po políčkách a tma všude kolem mě vůbec nebavily a nebylo pořádně vidět, kam jdu.
- **Jak jsem to opravil:** Upřesnil jsem zadání, ať hru předěláme z tahovky na normální real-time pohyb (60 FPS) přes `WASD`, míření myší a střelbu levým tlačítkem myši, a ať jedna místnost vyplní obrazovku a je celá normálně osvětlená se zamykacími dveřmi. Zároveň se snížily životy a útok ančovičky i bosse, aby hra byla férová a dohratelná.

---

## Případ 2: Pád hry (`ValueError`) při změně rozlišení okna na Linuxu

- **Co jsem chtěl:** Chtěl jsem přidat do hry startovní menu s nastavením (Settings), kde půjde měnit rozlišení okna a kvalita grafiky.
- **Co AI udělala špatně:** AI v `main.py` ve funkci `present()` použila příkaz `pygame.transform.scale(self.screen, self.window_size, self.display)`. Spolehla se na to, že okno (`self.display`) bude mít vždycky na pixel přesně takovou velikost, jakou mu hra nastaví v `self.window_size`. Jenže na Linuxu používám dlaždicový správce oken (Hyprland), který drží velikost okna podle rozložení obrazovky a nenechá Pygame okno libovolně zmenšit.
- **Jak jsem to poznal:** Když jsem hru spustil, šel do Settings a kliknul na změnu rozlišení, hra okamžitě spadla do terminálu s chybou `ValueError: Destination surface not the given width or height`.
- **Jak jsem to opravil:** Zkopíroval jsem chybový výpis z terminálu a nechali jsme předělat `present()` i přepočet souřadnic myši `to_canvas_pos()`. Místo škálování natvrdo přímo do `self.display` se obraz nejdřív přeškáluje na zvolené rozlišení do pomocné plochy a pak se přizpůsobí skutečné velikosti okna zjištěné přes `self.display.get_size()`. Potom už přepínání rozlišení přestalo padat.

---

## Případ 3: „Nové odemykatelné mapy“, které byly jen přejmenované kopie

- **Co jsem chtěl:** Chtěl jsem do hry přidat víc map, které by si hráč postupně odemykal a vybíral před startem hry.
- **Co AI udělala špatně:** AI vygenerovala 4 mapy (*Pizza Station Ares*, *Polar Cryo-Vaults*, *Olympus Lava Ovens*, *Anchovy Mothership*) a obrazovku pro výběr mapy. Na první pohled v menu to vypadalo hezky, ale ve skutečnosti to byla pořád úplně stejná hra se stejnými nepřáteli a stejným bossem, jen s jiným nadpisem a prohozenými barvami podlah, které už ve hře stejně byly.
- **Jak jsem to poznal:** Při vyzkoušení jednotlivých map jsem hned viděl, že se v nich nic reálně nemění a jsou to jen 4 stejné věci pod jiným jménem, což působilo uměle a zbytečně.
- **Jak jsem to opravil:** Rozhodl jsem se tenhle krok vrátit zpátky. Nechal jsem všechny 4 extra mapy i výběrovou obrazovku smazat ze `settings.py`, `dungeon.py`, `game.py` a `main.py`. Místo toho jsem radši vymyslel funkci, která dává větší smysl - přihlašování a registraci účtů napojenou na SQLite databázi (`database.py`), kam se ukládá postup hráče, a testovací účet `admin` / `admin` s plným postupem.

---

## Případ 4: Kuchař po průchodu dveřmi blikal bez zbraně

- **Co jsem chtěl:** Chtěl jsem, aby měl kuchař v ruce viditelnou zbraň, která se otáčí za myší, a aby postavy měly animace.
- **Co AI udělala špatně:** Při vstupu do nové místnosti s nepřáteli dostane hráč na necelého půl vteřiny nesmrtelnost (`iframe_timer = 0.45`), aby ho hned ve dveřích něco nezabilo. AI ale na tenhle `iframe_timer` napojila blikání postavy kuchaře a zapomněla do stejné podmínky dát vykreslení zbraně. Výsledek byl, že při každém vstupu do místnosti kuchař zablikal (zmizel), zatímco zbraň zůstala viset sama ve vzduchu.
- **Jak jsem to poznal:** Všimnul jsem si toho vizuálně při přecházení mezi místnostmi, že postava divně problikává i když do mě nikdo nestřelil, a zbraň v tu chvíli levituje.
- **Jak jsem to opravil:** Upravili jsme vykreslování v `main.py` tak, aby se blikání spouštělo jen při skutečném zásahu od nepřítele (`hit_flash`) a aby se při bliknutí schoval kuchař i se zbraní dohromady.

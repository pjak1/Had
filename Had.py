import pyglet
import random
from pathlib import Path
from win32api import GetSystemMetrics
VELIKOST_CTVERCE = 64
# Načtení obrázků
cesta_casti = Path("casti_hada")
cesta_hranice = Path("Hranice")
casti_hada = {}
pozadi = Path("Background")
for cesta in cesta_casti.glob("*.png"):
    casti_hada[cesta.stem] = pyglet.image.load(cesta)
for cesta in cesta_hranice.glob("*.png"):
    hranice_png = pyglet.image.load(cesta)

for cesta in pozadi.glob("*.png"):
    pozadi_png = pyglet.image.load(cesta)

window = pyglet.window.Window(GetSystemMetrics(0), GetSystemMetrics(1), fullscreen=True)


class Stav:
    def __init__(self):
        self.vyska = window.height // VELIKOST_CTVERCE
        self.sirka = window.width // VELIKOST_CTVERCE
        self.had_zije = True

    def KonecHry(self):
        konec_hry = pyglet.text.Label(f"Skóre: {len(had.had)-2}\n(Stiskněte mezerník pro restart nebo ESC pro konec)", font_size=24, x=window.width // 2, y=window.height // 2, width=window.width, align="center", anchor_x="center", anchor_y="center", multiline=True)
        return konec_hry

    def Restart(self):
        had.had.clear()
        had.had = [(6, 7), (7, 7)]
        self.had_zije = True
        had.smer_pohybu = 1, 0
        jabko.pozice_jidla.clear()
        jabko.Pridat_jidlo()
        pomeranc.pozice_jidla.clear()
        pomeranc.Pridat_jidlo()


stav = Stav()


class Hranice:
    def __init__(self):
        self.pozice = []

    def Vytvorit(self):
        for y in range(0, stav.vyska + 1):
            self.pozice.append((0, y))
            self.pozice.append((stav.sirka - 1, y))

        for x in range(0, stav.sirka + 1):
            self.pozice.append((x, 0))
            self.pozice.append((x, stav.vyska))


hranice = Hranice()
hranice.Vytvorit()


class Had:
    def __init__(self):
        self.had = [(6, 7), (7, 7)]
        self.smer_pohybu = 1, 0
        self.odkud = ""
        self.kam = ""
        self.smery_ve_fronte = []
        self.cast_hada = 0

    def Pohyb(self):
        if self.smery_ve_fronte:
            # Fronta směru pohybu po rychlém stisknutí kláves
            novy_smer = self.smery_ve_fronte[0]
            del self.smery_ve_fronte[0]
            stary_smer_x, stary_smer_y = self.smer_pohybu
            novy_smer_x, novy_smer_y = novy_smer
            if(stary_smer_x, stary_smer_y) != (-novy_smer_x, -novy_smer_y):
                self.smer_pohybu = novy_smer
        if not stav.had_zije:
            return
        # Pohyb - nová pozice = stará pozice + nový směr zadaný hráčem
        stara_x, stara_y = self.had[-1]
        smer_x, smer_y = self.smer_pohybu
        nova_x = stara_x + smer_x
        nova_y = stara_y + smer_y
        # Kontrola vylezení z hrací plochy
        nova_hlava = nova_x, nova_y
        if nova_hlava in hranice.pozice:
            stav.had_zije = False
            stav.KonecHry()
        # Když had narazí sám do sebe
        if nova_hlava in self.had:
            stav.had_zije = False
            stav.KonecHry()
        self.had.append(nova_hlava)

        # Jezení jídla
        if nova_hlava in jabko.pozice_jidla:
            jabko.pozice_jidla.remove(nova_hlava)
            jezeni = pyglet.media.load("Zvuky/Snake_eating.wav")
            jezeni.play()
            jabko.Pridat_jidlo()
        elif nova_hlava in pomeranc.pozice_jidla:
            pomeranc.pozice_jidla.remove(nova_hlava)
            jezeni = pyglet.media.load("Zvuky/Snake_eating.wav")
            jezeni.play()
            pomeranc.Pridat_jidlo()
        else:
            del self.had[0]

    def Smery(self):
        delkaHada = len(self.had)
        delkaHada -= 1
        # Určuje směr předchozí části
        if self.had[self.cast_hada - 1][0] < self.had[self.cast_hada][0]:
            self.odkud = "left"
        if self.had[self.cast_hada - 1][0] > self.had[self.cast_hada][0]:
            self.odkud = "right"
        if self.had[self.cast_hada - 1][1] < self.had[self.cast_hada][1]:
            self.odkud = "bottom"
        if self.had[self.cast_hada - 1][1] > self.had[self.cast_hada][1]:
            self.odkud = "top"
        if self.cast_hada == 0:
            self.odkud = "end"
        # Určuje kam má směřovat část hada
        if self.cast_hada == delkaHada:
            self.kam = "tongue"
            self.cast_hada = 0
            return
        if self.had[self.cast_hada][0] < self.had[self.cast_hada + 1][0]:
            self.kam = "right"
        if self.had[self.cast_hada][0] > self.had[self.cast_hada + 1][0]:
            self.kam = "left"
        if self.had[self.cast_hada][1] < self.had[self.cast_hada + 1][1]:
            self.kam = "top"
        if self.had[self.cast_hada][1] > self.had[self.cast_hada + 1][1]:
            self.kam = "bottom"
        self.cast_hada += 1


had = Had()


class Jidlo:
    def __init__(self):
        self.pozice_jidla = []

    def Pridat_jidlo(self):
        for pridej_jidlo in range(50):
            x = random.randrange(stav.sirka)
            y = random.randrange(stav.vyska)
            pozice = x, y
            if (pozice not in self.pozice_jidla) and (pozice not in had.had) and (pozice not in jidlo.pozice_jidla) and (pozice not in hranice.pozice):
                self.pozice_jidla.append(pozice)
                jidlo.pozice_jidla.append(pozice)
                return


jidlo = Jidlo()


class Jabko(Jidlo):
    def __init__(self):
        super().__init__()
        self.pozice_jidla = []
        self.Pridat_jidlo()


jabko = Jabko()


class Pomeranc(Jidlo):
    def __init__(self):
        super().__init__()
        self.pozice_jidla = []
        self.Pridat_jidlo()


pomeranc = Pomeranc()

# Vykreslování


@window.event
def on_draw():
    window.clear()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
    pozadi_png.blit(5, 10, width=window.width, height=window.height)
    # Hranice
    for x, y in hranice.pozice:
        hranice_png.blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)

    # Had
    for x, y in had.had:
        had.Smery()
        odkud = had.odkud
        kam = had.kam
        if not stav.had_zije and had.kam == "tongue":
            casti_hada[odkud + "-" + "dead"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
            break
        casti_hada[odkud + "-" + kam].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    # Jidlo
    for x, y in jabko.pozice_jidla:
        casti_hada["apple"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    for x, y in pomeranc.pozice_jidla:
        casti_hada["orange"].blit(x * VELIKOST_CTVERCE, y * VELIKOST_CTVERCE, width=64, height=64)
    if stav.had_zije == False:
        stav.KonecHry().draw()


# Ovládání pohybu
@window.event
def on_key_press(kod_znaku, pomocna_klavesa):  # povinné 2 parametry
    if kod_znaku == pyglet.window.key.LEFT:
        novy_smer = -1, 0
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.RIGHT:
        novy_smer = 1, 0
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.UP:
        novy_smer = 0, 1
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.DOWN:
        novy_smer = 0, -1
        had.smery_ve_fronte.append(novy_smer)
    if kod_znaku == pyglet.window.key.SPACE and stav.had_zije == False:
        stav.Restart()


def Pohyb(prodleva):
    had.Pohyb()


pyglet.clock.schedule_interval(Pohyb, 1 / 6)  # idealní rychlost je 1 / 6

pyglet.app.run()

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.core.window import Window

"""
    Třída Floor - widget - zajišťuje scrollování textury podlahy / pozadí
    Parametr - is_floor -> nastavení rozměrů a rychlosti scrollování (pro zem / pozadí)
    Funkce:
        on_size(self, *args)
        scroll(self, dt)
"""


class Floor(Widget):
    # Objekt pro texturu
    tex = ObjectProperty(None)

    # Cesty k obrázkům
    IMG_FLOOR = "img/base.png"
    IMG_BG = "img/bg.png"

    # Parametr is_floor, defaultně na True

    def __init__(self, is_floor=True, **kwargs):
        super(Floor, self).__init__(**kwargs)
        # Pokud je is_floor True, nastaví se pro podlahu cesta, scroll_speed a rozměry
        if is_floor:
            self.img_src = self.IMG_FLOOR
            self.scroll_speed = 1.136
            self.size_hint = 1, None
            self.size[1] = 100
        # Pokud je is_floor False, nastaví se pro pozadí cesta, scroll speed a rozměry
        else:
            self.img_src = self.IMG_BG
            self.scroll_speed = 10
            self.size_hint = 1, 1
        # Načtení textury do ObjectProperty self.tex
        self.tex = Image(source=self.img_src).texture
        # Nastavení wrapu textury na repeat - když nestačí do konce okna, vloží se znovu
        self.tex.wrap = 'repeat'
        # Nastaví se uv rozměry pro texturu
        self.tex.uvsize = (Window.width / self.tex.width, -1)

    def on_size(self, *args):
        self.tex.uvsize = (self.width / self.tex.width, -1)

    # Scrollování textury podle dt (uplynulý čas od posledního průběhu smyčky)

    def scroll(self, dt):
        self.tex.uvpos = ((self.tex.uvpos[0] + dt / self.scroll_speed), self.tex.uvpos[1])

        # Vložení textury do texture
        texture = self.property('tex')
        texture.dispatch(self)

from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.image import Image
from kivy.core.window import Window

"""
    Třída Bird jako obrázek kvůli práci s texturou, parametr id
    Funkce:
        check_collision(self, p) - returnuje True / False + nastaví proměnnou alive na False
        change_texture(self, dt) - mění texturu
"""


class Bird(Image):
    # Cesty k obrázkům (podle polohy křídel - d, m, u)
    IMGD = "img/bird-d.png"
    IMGM = "img/bird-m.png"
    IMGU = "img/bird-u.png"

    # alive jako boolproperty - kontrola, jestli žije
    alive = BooleanProperty(True)
    # score - počítá score
    score = NumericProperty(0)

    def __init__(self, bird_id=0, **kwargs):
        super(Bird, self).__init__(**kwargs)
        # Načtení obrázků jako textur do listu (pro Widget, nefungovalo, zatím vyřazeno)

        # self.textures = [Image(source=self.IMGD, keep_ratio=True).texture,
        #                  Image(source=self.IMGM, keep_ratio=True).texture,
        #                  Image(source=self.IMGU, keep_ratio=True).texture]

        # id
        self.bird_id = bird_id
        # Bool - žije ještě?
        self.alive = True
        # Nastavení score na 0
        self.score = 0
        # Načtení v2 -> list s cestami k obrázkům (pro Image - změní se source)
        self.textures = [self.IMGD, self.IMGM, self.IMGU]
        # Index aktuální textury
        self.texture_idx = 0
        # Zdroj pro texturu (přímo)
        self.source = self.textures[0]
        # Proměnná pro sčítání času
        self.time = 0

    # Kontrola kolize, parametr p je widget pipe (trubka)
    def check_collision(self, p):
        # Podmínka pro kolizi; je rozdělena na 3 části:
        # 1. kolize se spodní trubkou (rozděleně, protože v jednom widgetu jsou obě dvě)
        # 2. kolize s vrchní trubkou
        # 3. kolize se zemí
        if self.collide_widget(
                Widget(pos=(p.pos[0], 0), size=(p.pipe_body_texture.width, p.pipe_center - p.GAP_SIZE / 2))) \
                or self.collide_widget(Widget(pos=(p.pos[0], p.pipe_center + p.GAP_SIZE / 2), size=(
                p.pipe_body_texture.width, Window.height - p.pipe_center - p.GAP_SIZE / 2))) \
                or self.pos[0] <= 100:
            self.alive = False
            return True
        return False

    # Změna obrázku ptáka - provizorní po dvou desetinách sekundy
    def change_texture(self, dt):
        self.time += dt
        if self.time > 0.2:
            self.texture_idx = self.texture_idx + 1 if self.texture_idx < 2 else 0
            print(self.texture_idx)
            self.source = self.textures[self.texture_idx]
            self.time = 0

    def passed_pipe(self):
        self.score += 1

    def __str__(self):
        return f"\n\n" \
               f"Size = {self.size}\n" \
               f"Pos  = {self.pos}\n" \
               f"Cen_y= {self.center_y}\n" \
               f"Alive= {self.alive}\n"

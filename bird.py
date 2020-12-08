from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.image import Image
from kivy.core.window import Window

"""
    Třída Bird jako obrázek kvůli práci s texturou, parametr id
    Funkce:
        check_collision(self, p) - returnuje True / False + nastaví proměnnou alive na False
        change_texture(self, dt) - mění texturu
        passed_pipe() - přidá score
        jump() - skočí (reset času od skoku)
        move(dt) - pohyb (padání / skok) a rotace podle toho
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
    # rychlost
    vel = NumericProperty(0)
    # Počet průbehu smyčkou od posledního skoku
    tick_count = NumericProperty(0)
    # Maximální rotace
    MAX_ROT = NumericProperty(25)
    # Rychlost rotace
    ROT_VEL = NumericProperty(3)
    # Úhel rotace
    angle = NumericProperty(0)
    # Červená barva
    r = NumericProperty(1)

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
        self.textures = [self.IMGD, self.IMGM, self.IMGU, self.IMGM]
        # Index aktuální textury
        self.texture_idx = 0
        # Zdroj pro texturu (přímo)
        self.source = self.textures[0]
        # Proměnná pro sčítání času
        self.time = 0
        self.r = 1
        self.color = [1, 1, 1, 1]

    # Kontrola kolize, parametr p je widget pipe (trubka)
    def check_collision(self, p):
        if self.center_y <= 100 + self.height / 2:
            return True
        # Podmínka pro kolizi; je rozdělena na 3 části:
        # 1. kolize se spodní trubkou (rozděleně, protože v jednom widgetu jsou obě dvě)
        # 2. kolize s vrchní trubkou
        # 3. kolize se zemí

        # if self.collide_widget(
        #         Widget(pos=(p.pos[0], 0), size=(p.pipe_body_texture.width, p.pipe_center - p.GAP_SIZE / 2))) \
        #         or self.collide_widget(Widget(pos=(p.pos[0], p.pipe_center + p.GAP_SIZE / 2), size=(
        #         p.pipe_body_texture.width, Window.height - p.pipe_center - p.GAP_SIZE / 2))):
        #     return True
        if abs(self.center_x - p.center_x) < int(p.width / 2 + self.width / 2):
            if self.center_y + int(self.height / 2) >= p.pipe_center + int(p.GAP_SIZE / 2) or \
                    self.center_y - int(self.height / 2) <= p.pipe_center - int(p.GAP_SIZE / 2):
                return True
        return False

    # Změna obrázku
    def change_texture(self, dt):
        self.time += dt
        if self.time > 0.2:
            self.texture_idx = self.texture_idx + 1 if self.texture_idx < len(self.textures) - 1 else 0
            self.source = self.textures[self.texture_idx]
            self.time = 0

    # Když proletěl trubkou -> score += 1
    def passed_pipe(self):
        self.score += 1

    # Skok - nastavení počáteční rychlosti a resetování času od posledního skoku
    def jump(self):
        self.vel = 400
        self.tick_count = 0

    # Pohyb a rotace
    def move(self, dt):
        self.tick_count += 1

        # změna souřadnice y podle vrhu svislého (s upravenými konstantami)
        d = 2 * self.vel * 1 / 70 - 20 * 1 / 70 * (self.tick_count * 2 - 1)

        # Jestli po přičtení d bude pořád na obrazovce, přičte d. Jinak nastaví pozici těsně pod okraj
        self.center_y = self.center_y + d if self.center_y - d < Window.height - self.height / 2 else Window.height - self.height / 2 - 2

        # Jestli letí nahoru
        if d > 0:
            # Nakloní se nahoru na max. úhel
            if self.angle < self.MAX_ROT:
                self.angle = self.MAX_ROT
        # Pokud je úhel větší než 0, ale padá dolů
        elif self.angle > 0:
            # Mění úhel podle rychlosti
            self.angle -= self.ROT_VEL
        # Jinak dokud nesměřuje přímo dolů, rotuje poloviční rychlostí
        else:
            if self.angle > -90:
                self.angle -= self.ROT_VEL / 2

    def dead_move(self):
        self.x -= 5

    def __str__(self):
        return f"\n\n" \
               f"Size = {self.size}\n" \
               f"Pos  = {self.pos}\n" \
               f"Cen_y= {self.center_y}\n" \
               f"Alive= {self.alive}\n"

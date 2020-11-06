from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.core.window import Window
from kivy.clock import Clock
from random import randint

# Import třídy Pipe
from pipe import Pipe
from floor import Floor
from bird import Bird

"""
    Třída FlappyBirdGame jako FloatLayout
    -> tělo hry
    funkce:
        add_bird(bird_count) - přidá ptáky (podle bird_count)
        remove_bird(bird) - odstraní ptáka
        add_pipe() - přidá trubku
        remove_pipe() - odebere trubku
        collision() - při kolizi některého z ptáků s trubkou ... (do budoucna)
        update(dt) - hlavní smyčka
"""


class FlappyBirdGame(FloatLayout):
    # listy jako ListProperty
    birds = ListProperty(None)
    birds_alive = ListProperty(None)
    pipes = ListProperty(None)
    floor = ObjectProperty(None)
    bg = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(FlappyBirdGame, self).__init__(**kwargs)
        # Pole pro objekty
        self.birds = []
        ### Zatím dělané pro self.birds -> později nahradit
        self.birds_alive = []
        self.pipes = []
        # Měření času
        self.time = 0

        # Keyboard
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Přidá podlahu a pozadí (problémy s indexem ???)
        self.floor = Floor(True)
        self.add_widget(self.floor, 3000000)
        self.bg = Floor(False)
        self.add_widget(self.bg, 4000000)
        # Přidá na začátek ptáky
        self.add_bird(20)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(keycode)
        if keycode[1] == 'w':
            for b in self.birds:
                b.jump()

    # Přidá počet ptáků podle parametru
    def add_bird(self, bird_count):
        for i in range(0, bird_count):
            print(i)
            bird = Bird()
            # Pozice y na střed herní plochy
            # bird.center_y = (Window.height + 100 / 2)
            bird.center_y = 250 + 15 * i
            # Přidá objekt do listu objektů
            self.birds.append(bird)
            # Přidá widget
            self.add_widget(bird, i)
            print(f"Bird{bird.size}, {bird.pos}")

    # Odstraní ptáka
    def remove_bird(self, bird):
        self.birds.remove(bird)
        self.remove_widget(bird)
        # Když nezbývá žádný -
        if len(self.birds) == 0:
            # Vypne aplikaci (zatím)
            App.get_running_app().stop()

    # Přidá trubku
    def add_pipe(self):
        new_pipe = Pipe()
        # x pozice -> vpravo od obrazovky
        new_pipe.center_x = Window.width + new_pipe.width
        # y pozice -> náhodně - nejblíž 150px od okraje / podlahy
        new_pipe.pipe_center = randint(250, Window.height - 150)
        print("New pipe")
        # Přidá trubku
        self.add_widget(new_pipe, len(self.birds) + 1)
        self.pipes.append(new_pipe)

    # Odstraní trubku
    def remove_pipe(self, p):
        self.remove_widget(p)
        self.pipes.remove(p)
        print(f"REMOVING PIPE {p}")

    # Při kolizi ...
    def collision(self, bird):
        # Nechá odebrat ptáka
        self.remove_bird(bird)

    def passed(self, pipe):
        # volá metodu passed() dané trubky, která nastaví is_passed na True
        pipe.passed()
        # Každému přičte bod v passed_pipe()
        for b in self.birds:
            b.passed_pipe()

    # Hlavní smyčka, parametr dt (změna času od posledního průběhu)
    def update(self, dt):
        # Součet času
        self.time += dt
        # Scroll pozadí a podlahy
        self.floor.scroll(dt)
        self.bg.scroll(dt)
        # Pro každou z trubek:
        for p in self.pipes:
            # Pohne trubkou
            p.move()
            # A pro každého z ptáků
            for b in self.birds:
                # Kontrola kolize
                if b.check_collision(p):
                    # Předá kolidujícího ptáka dál do self.collision
                    self.collision(b)
            # Jestli pták bezpečně prošel trubkou,
            if p.pos[0] + p.width > b.pos[0] + b.width:
                self.passed(p)
            # Když je trubka za obrazovkou...
            if p.pos[0] + p.size[0] < -50:
                # ...nechá se odebrat
                self.remove_pipe(p)
        # Pro každého ptáka
        for bird in self.birds:
            # Pohyb textury
            bird.change_texture(dt)
            bird.move(dt)
        # Později jako jiný Clock ... ???
        # Když je součet časů víc než 2s
        if self.time > 2:
            # Resetuje se součet
            self.time = 0
            # Přidá trubku
            self.add_pipe()


class MainApp(App):

    def build(self):
        game = FlappyBirdGame()
        # Spouští smyčku frekvencí 60Hz
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == "__main__":
    # nastavení obrazovky ???

    # Config.set('graphics', 'fullscreen', False)
    # Config.set('graphics', 'width', 1000)
    # Config.set('graphics', 'height', 500)
    # Config.set('graphics', 'window_state', 'maximized')
    # Config.set('graphics', 'borderless', True)
    # Config.set('graphics', 'resizable', True)
    # Config.write()
    MainApp().run()

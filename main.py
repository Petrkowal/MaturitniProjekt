from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

from random import randint
import time

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
    pipes = ListProperty(None)
    floor = ObjectProperty(None)
    current_pipe = ObjectProperty(None)
    bg = ObjectProperty(None)
    MIN_WIDTH = 600
    MIN_HEIGHT = 800
    pipes_passed = NumericProperty(0)

    def __init__(self, **kwargs):
        super(FlappyBirdGame, self).__init__(**kwargs)
        # Pole pro objekty
        self.birds = []
        self.pipes = []
        self.current_pipe = None
        # Měření času
        self.time = 0
        # Přidá podlahu a pozadí (problémy s indexem ???)
        self.floor = None
        self.bg = None
        self.population = 20
        self.pipes_passed = 0
        self.score_label = None
        self.population_input = None
        Window.bind(on_resize=self.on_window_resize)

        self.prepare()

    def on_window_resize(self, window, width, height):
        if Window.width < self.MIN_WIDTH:
            Window.size = self.MIN_WIDTH, Window.height
        if Window.height < self.MIN_HEIGHT:
            Window.size = Window.width, self.MIN_HEIGHT
        self.stop()

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

    def kill_bird(self, bird):
        bird.alive = False
        bird.color = [255, 1, 1, 1]

    # Odstraní ptáka
    def remove_bird(self, bird):
        self.birds.remove(bird)
        self.remove_widget(bird)

    def any_bird_alive(self):
        alive = 0
        for b in self.birds:
            if b.alive:
                alive += 1
        if alive == 0:
            # Vypne aplikaci (zatím)
            # App.get_running_app().stop()
            self.restart()

    # Přidá trubku
    def add_pipe(self):
        new_pipe = Pipe()
        # x pozice -> vpravo od obrazovky
        new_pipe.center_x = Window.width + new_pipe.width
        # y pozice -> náhodně - nejblíž 150px od okraje / podlahy
        new_pipe.pipe_center = randint(250, Window.height - 150)
        print("New pipe")
        print(new_pipe)
        # Přidá trubku
        self.add_widget(new_pipe, len(self.birds) + 8)
        self.pipes.append(new_pipe)

    # Odstraní trubku
    def remove_pipe(self, p):
        self.remove_widget(p)
        self.pipes.remove(p)
        print(f"REMOVING PIPE {p}")

    # Při kolizi ...
    def collision(self, bird):
        # Nechá odebrat ptáka
        self.kill_bird(bird)
        self.any_bird_alive()

    def passed(self, pipe):
        # volá metodu passed() dané trubky, která nastaví is_passed na True
        pipe.passed()
        for p in self.pipes:
            if not p.is_passed:
                self.current_pipe = p
                break
        self.pipes_passed += 1
        self.score_label.text = f"Score: {self.pipes_passed}"
        # Každému přičte bod v passed_pipe()
        for b in self.birds:
            b.passed_pipe()

    # Restartuje hru
    def restart(self):
        self.stop()

    def stop(self, *args):
        self.birds = []
        self.pipes = []
        # self.clear_widgets()
        Clock.unschedule(self.update)
        # self.prepare()

    # Při zapnutí
    def prepare(self):
        self.clear_widgets()
        # Keyboard
        self.pipes_passed = 0
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        # Přidá podlahu a pozadí (problémy s indexem ???)
        self.floor = Floor(True)
        self.add_widget(self.floor, 3000000)
        self.bg = Floor(False)
        self.add_widget(self.bg, 4000000)

        self.time = 0

        btn_run = Button(text='Start')
        btn_run.pos[0] = 25
        btn_run.bind(on_press=self.run)
        self.add_widget(btn_run)

        btn_stop = Button(text='Stop')
        btn_stop.pos[0] = 100
        btn_stop.bind(on_press=self.stop)
        self.add_widget(btn_stop)

        btn_exit = Button(text='Exit')
        btn_exit.pos[0] = Window.width - 75
        btn_exit.bind(on_press=self.exit)
        self.add_widget(btn_exit)

        population_label = Label(text="Population (1 - 100):", font_size=20, color=(0, 0, 0, 1))
        population_label.pos[0] = 250
        self.add_widget(population_label)

        self.population_input = TextInput(text=f"{self.population}", multiline=False, font_size=20, input_filter='int',
                                          halign='center')
        self.population_input.pos[0] = 370
        self.add_widget(self.population_input)

        btn_set = Button(text='Set')
        btn_set.pos[0] = 445
        btn_set.bind(on_press=self.submit)
        self.add_widget(btn_set)

        self.score_label = Label(text=f"Score: {self.pipes_passed}", font_size=40, color=(0, 0, 0, 1))
        self.score_label.pos[0] = int(Window.width / 2)
        self.score_label.pos[1] = int(Window.height - 100 - self.score_label.size[1])
        self.add_widget(self.score_label)

    def submit(self, *args):
        if int(self.population_input.text) < 1:
            self.population = 1
        elif int(self.population_input.text) > 100:
            self.population = 100
        else:
            self.population = int(self.population_input.text)
        self.stop()

    def exit(self, instance):
        App.get_running_app().stop()

    # Spustí hru
    def run(self, instance):
        self.restart()
        self.prepare()
        # Přidá na začátek ptáky
        self.add_bird(self.population)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    # Hlavní smyčka, parametr dt (změna času od posledního průběhu)
    def update(self, dt):
        if len(self.pipes):
            if self.pipes[-1].pos[0] < Window.width + self.pipes[0].width - 600:
                # Resetuje se součet
                self.time = 0
                # Přidá trubku
                self.add_pipe()
        else:
            self.add_pipe()
            self.current_pipe = self.pipes[0]
        # Součet času
        self.time += dt
        # Scroll pozadí a podlahy
        self.floor.scroll(1 / 60)
        self.bg.scroll(1 / 60)
        # Pro každou z trubek:
        for p in self.pipes:
            # Pohne trubkou
            p.move()
            # Jestli pták bezpečně prošel trubkou,
            # if p.pos[0] + p.width < b.pos[0] + b.width:
            if p.pos[0] + p.width < 216 and not p.is_passed:
                self.passed(p)
            # Když je trubka za obrazovkou...
            if p.pos[0] + p.size[0] < -50:
                # ...nechá se odebrat
                self.remove_pipe(p)
        # Pro každého ptáka
        for bird in self.birds:
            if bird.alive:
                # Pohyb textury
                bird.change_texture(dt)
                bird.move(dt)
                if bird.check_collision(self.current_pipe):
                    # Předá kolidujícího ptáka dál do self.collision
                    self.collision(bird)

            else:
                bird.dead_move()


class MainApp(App):

    def build(self):
        game = FlappyBirdGame()
        # game.start()
        return game


if __name__ == "__main__":
    # nastavení obrazovky ???

    # Config.set('graphics', 'fullscreen', False)
    # Config.set('graphics', 'width', 1000)
    # Config.set('graphics', 'height', 500)
    # Config.set('graphics', 'minimum_width', '1000')
    # Config.set('graphics', 'window_state', 'maximized')
    # Config.set('graphics', 'borderless', True)
    # Config.set('graphics', 'resizable', True)
    # Config.write()
    MainApp().run()

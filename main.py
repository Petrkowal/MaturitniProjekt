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
from ai import BirdAI

"""
    Třída FlappyBirdGame (FloatLayout)
    -> tělo hry
    Metody:
        set_window_size() - nastaví okno
        _keyboard_closed() - odbinduje klávesnici
        _on_keyboard_down() - skok při stisku klávesy
        add_bird(bird_count) - přidá daný počet ptáků
        remove_bird(bird) - odstraní daného ptáka
        any_bird_alive() - restart hry, jestli už nikdo nežije
        add_pipe() - přidá trubku za pravý okraj okna v náhodné výšce
        remove_pipe(pipe) - odstraní trubku
        collision(bird) - při kolizi "zabije" ptáka
        passed(pipe) - Při proskočení trubkou ji označí jako passnutou, zrychlí hru a zvedne score
        update_label() - updatuje label při změně hodnoty (neupdatuje se sám)
        prepare() - připraví hru na další start (promaže listy objektů, smaže widgety atd)
        stop() - vyčistí listy objektů a přeruší clock
        create_ai() - vytvoří NN model
        submit() - veme hodnoty z inputů a nastaví je do hry
        exit() - vypne aplikaci
        player_control_toggle() - přepíná lidského hráče (True, False)
        retrain() - vygenerování nového modelu
        run() - spuštění hry
        schedule_int() - nastaví clock
        update()- hlavní smyčka
"""


class FlappyBirdGame(FloatLayout):
    # Listy pro objekty
    birds = ListProperty(None)  # List pro všechny ptáky
    pipes = ListProperty(None)  # List pro trubky
    # Objekty
    floor = ObjectProperty(None)  # Objekt pro podlahu (zem)
    current_pipe = ObjectProperty(None)  # Objekt -> následující trubka
    bg = ObjectProperty(None)  # Pozadí (kvůli scrollování)
    pipes_passed = NumericProperty(0)  # Počet úspěšně překonaných překážek (trubek) - score
    # Konstanty
    WIDTH = 1800  # Šířka okna
    HEIGHT = 1000  # Výška okna
    MAX_GAME_SPEED = 8  # Maximální rychlost hry
    FPS = 60  # FPS

    def __init__(self, **kwargs):
        super(FlappyBirdGame, self).__init__(**kwargs)
        # Pole pro objekty
        self.birds = []
        self.pipes = []
        self.current_pipe = None
        self.player_control = False  # Bool - bude hrát (i) člověk?
        self.floor = None
        self.bg = None
        self.population = 2  # Populace bude 2 na začátku
        self.birds_alive = self.population  # Počet živých
        self.pipes_passed = 0
        self.score_label = None  # Label pro score
        self.population_input = None  # Uživatelský vstup - populace
        self.bird_ai = None  # Objekt pro model
        self._keyboard = None  # Klávesnice...
        self.game_speed = 0  # Rychlost hry
        self.set_window_size(self.WIDTH, self.HEIGHT)  # Nastaví šířku a výšku okna
        self.prepare()  # Připraví hru

    # Nastaví šířku a výšku okna
    def set_window_size(self, width, height):
        Window.size = width, height

    # Unbind klávesnice
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    # Při zmáčknutí tlačítka vyskočí hráčem ovládané objekty
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(keycode)
        if keycode[1] == 'w' or keycode[1] == 'up' or keycode[1] == 'spacebar':  # Při stisku W, šipky nahoru, mezerníku
            for b in self.birds:  # Projde všechny ptáky, pokud je ovládaný člověkem, skočí
                if b.human:
                    b.jump()

    # Přidá počet ptáků podle parametru bird_count
    def add_bird(self, bird_count):
        for i in range(0, bird_count):
            bird = Bird()  # Vytvoří objekt ptáka podle třídy Bird()
            bird.center_y = 250 + 15 * i  # Nastaví mu pozici (y)
            if i == 0 and self.player_control:  # Pokud bude hrát člověk, první pták bude ovládaný člověkem
                bird.human = True
                bird.color = [1, 1, 1, 1]  # A bude mít originální barvu
            if i != 0 and self.player_control:  # Pokud hraje člověk, ostatní budou napůl průhlední
                bird.color = [1, 1, 1, 0.5]
            self.birds.append(bird)  # Přidá ptáka do listu
            self.add_widget(bird, i)  # Přidá ho jako widget
            print("NEW_BIRD")

    # "zabije" daného ptáka, změní mu barvu na červenou
    def kill_bird(self, bird):
        # Změní počet živých
        self.birds_alive = self.birds_alive - 1 if self.birds_alive else 0
        bird.alive = False
        bird.color = [255, 1, 1, 1]

    # Odstraní ptáka
    def remove_bird(self, bird):
        self.birds.remove(bird)
        self.remove_widget(bird)

    # Jestli už nikdo nežije, restartuje hru (vyvolaná jen při kolizi)
    def any_bird_alive(self):
        alive = 0
        for b in self.birds:
            if b.alive:
                alive += 1
        if alive == 0:
            self.stop()

    # Přidá trubku
    def add_pipe(self):
        new_pipe = Pipe()
        # x pozice -> vpravo od obrazovky
        new_pipe.center_x = Window.width + new_pipe.width
        # y pozice -> náhodně - nejblíž 150px od okraje / podlahy
        new_pipe.pipe_center = randint(350, Window.height - 150)
        print("New pipe")  # Výpis
        print(new_pipe)
        # Přidá trubku - index nastaví na počet ptáků + počet ostatních widgetů (button, label atd)
        # Kvůli správnému zobrazení trubky => mezi pozadím a podlahou
        self.add_widget(new_pipe, len(self.birds) + 10)  # index podle počtu widgetů (např + 10 atd) -> trubky
        self.pipes.append(new_pipe)

    # Odstraní trubku
    def remove_pipe(self, p):
        self.remove_widget(p)
        self.pipes.remove(p)
        print(f"REMOVING PIPE {p}")

    # Při kolizi ...
    def collision(self, bird):
        self.kill_bird(bird)  # Nechá "zabít" ptáka
        self.any_bird_alive()  # Zkontroluje, jestli ještě někdo žije

    # Zrychlí hru, volá metodu passed dané trubky, změní aktuální trubku
    def passed(self, pipe):
        # Změna rychlosti
        if self.game_speed <= self.MAX_GAME_SPEED:  # MAX = 8 -- log 1.015 (8 / 5) = 32
            self.game_speed *= 1.015  # 1.02 => 24 | 1.01 => 47 (48) | 1.015 => 32
        self.floor.set_scroll_speed(self.game_speed)
        pipe.passed()
        for p in self.pipes:
            p.set_velocity(self.game_speed)
        # //
        # První nepassnutá trubka se nastaví jako aktuální
        for p in self.pipes:
            if not p.is_passed:
                self.current_pipe = p
                break
        self.pipes_passed += 1
        self.update_label()
        # Každému přičte bod v passed_pipe()
        for b in self.birds:
            b.passed_pipe()

    # Aktualizuje label
    def update_label(self):
        self.score_label.text = f"Player: {self.player_control}  Birds alive: {self.birds_alive}  Score: {self.pipes_passed}"

    # Příprava hry
    def prepare(self):
        self.clear_widgets()  # Smazání všech widgetů
        self.pipes_passed = 0  # Reset passnutých trubek
        # Nastavení klávesnice
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        # Podlaha a pozadí
        self.floor = Floor(True)
        self.add_widget(self.floor, 3000000)
        self.bg = Floor(False)
        self.add_widget(self.bg, 4000000)
        self.game_speed = 5  # Rychlost hry

        # Přidání a nastavení tlačítek, labelů
        # Nepovedlo se mi to nastavit přes .kv - trubky před podlahou / nebyly vidět
        # Button - start hry
        btn_run = Button(text='Start')
        btn_run.pos[0] = 25
        btn_run.bind(on_press=self.run)
        self.add_widget(btn_run)

        # Button - zastavení hry
        btn_stop = Button(text='Stop')
        btn_stop.pos[0] = 80
        btn_stop.bind(on_press=self.stop)
        self.add_widget(btn_stop)

        # Button - vypnutí aplikace
        btn_exit = Button(text='Exit')
        btn_exit.pos[0] = Window.width - 75
        btn_exit.bind(on_press=self.exit)
        self.add_widget(btn_exit)

        # Label - populace
        population_label = Label(text="Population (1 - 100):", font_size=20, color=(0, 0, 0, 1))
        population_label.pos[0] = 205
        self.add_widget(population_label)

        # TextInput - populace
        self.population_input = TextInput(text=f"{self.population}", multiline=False, font_size=20, input_filter='int',
                                          halign='center')
        self.population_input.pos[0] = 325
        self.add_widget(self.population_input)

        # Button - načtení z inputu
        btn_set = Button(text='Set')
        btn_set.pos[0] = 400
        btn_set.bind(on_press=self.submit)
        self.add_widget(btn_set)

        # Button - bude / nebude hrát člověk
        btn_player = Button(text='Player')
        btn_player.pos[0] = 455
        btn_player.bind(on_press=self.player_control_toggle)
        self.add_widget(btn_player)

        # Button - znovu vytvoří model (natrénuje znovu a na jiných datech)
        btn_retrain = Button(text='Retrain')
        btn_retrain.pos[0] = 510
        btn_retrain.bind(on_press=self.retrain)
        self.add_widget(btn_retrain)

        # Score label: Hráč, Počet živých, Score
        self.score_label = Label(
            text=f"Player: {self.player_control}  Birds alive: {self.birds_alive}  Score: {self.pipes_passed}",
            font_size=40,
            color=(0, 0, 0, 1))
        self.score_label.pos[0] = int(Window.width / 2)
        self.score_label.pos[1] = int(Window.height - 100 - self.score_label.size[1])
        self.add_widget(self.score_label)

    # Stopne hru - vymaže listy objektů a přeruší clock
    def stop(self, *args):
        self.birds = []
        self.pipes = []
        Clock.unschedule(self.update)

    # Vytvoří neuronovou síť a natrénuje ji
    def create_ai(self):
        self.bird_ai = BirdAI(Window.height, Window.width, 48)

    # Načte data z inputu a aplikuje je; zastaví
    def submit(self, *args):
        if int(self.population_input.text) < 1:
            self.population = 1
        elif int(self.population_input.text) > 100:
            self.population = 100
        else:
            self.population = int(self.population_input.text)
            self.birds_alive = self.population
        self.stop()

    # Vypne aplikaci
    def exit(self, *args):
        App.get_running_app().stop()

    # Přepne bool - player_control; updatuje label
    def player_control_toggle(self, *args):
        self.player_control = not self.player_control
        print(self.player_control)
        self.update_label()

    # Vytvoří nové AI a restartuje hru
    def retrain(self, *args):
        self.stop()
        self.create_ai()
        self.run()

    # Spustí hru
    def run(self, *args):
        self.stop()
        self.prepare()
        if not self.bird_ai:  # Pokud ještě není AI
            # Vytvoří AI, jestli to má cenu (když hraje jen člověk bez botů, nemá cenu zdlouhavě trénovat AI)
            if not self.player_control or not self.population == 1:
                self.create_ai()
        # Přidá na začátek ptáky
        self.add_bird(self.population)
        self.schedule_int()

    # Zapne hodiny (clock)
    def schedule_int(self):
        Clock.schedule_interval(self.update, 1.0 / self.FPS)

    # Hlavní smyčka
    def update(self, *args):
        # Jestli existuje nějaká trubka
        if len(self.pipes):
            # A jestli poslední trubka je víc než 600 px od okraje
            if self.pipes[-1].pos[0] < Window.width + self.pipes[0].width - 600:
                # Přidá trubku
                self.add_pipe()
        else:  # Když není žádná trubka, jednu přidá a nastaví ji jako aktuální
            self.add_pipe()
            self.current_pipe = self.pipes[0]
        # Scroll pozadí a podlahy
        self.floor.scroll(1 / self.FPS)
        self.bg.scroll(1 / self.FPS)

        for p in self.pipes:  # Pro každou trubku
            p.move()  # Pohne trubkou
            if p.pos[0] + p.width < 216 and not p.is_passed:  # Jestli pták proletěl
                self.passed(p)  # Vyvolá passed
            if p.pos[0] + p.size[0] < -50:  # Když trubka projde za obrazovku, odebere ji
                self.remove_pipe(p)

        for bird in self.birds:  # Pro každého ptáka
            if bird.alive:  # Jestli žije
                if not bird.human:  # Jestli není ovládaný člověkem
                    # Připraví data pro NN
                    data = [bird.center_y,  # Pozice y daného ptáka
                            self.current_pipe.x - bird.x + bird.width,  # Vzdálenost od začátku trubky
                            self.current_pipe.pipe_center - self.current_pipe.GAP_SIZE / 2,  # y spodní trubky
                            self.current_pipe.pipe_center + self.current_pipe.GAP_SIZE / 2]  # y horní trubky
                    if self.bird_ai.predict(data) > 0.5:  # Jestli NN vyhodnotí, že má skočit, skočí
                        bird.jump()

                # Pohyb a změna textury (mávání křídel)
                bird.change_texture()
                bird.move()
                # Kontrola kolizí
                if bird.check_collision(self.current_pipe):
                    self.collision(bird)  # Předá ptáka dál

            else:  # Když nežije, zůstává u trubky a odjede z obrazovky, pak jej odstraní
                bird.dead_move(self.game_speed)
                if bird.x + bird.width < 0:
                    self.remove_bird(bird)


class MainApp(App):

    def build(self):
        game = FlappyBirdGame()
        return game


if __name__ == "__main__":
    # nastavení obrazovky ???

    # Config.set('graphics', 'fullscreen', False)
    Config.set('graphics', 'width', 1800)
    Config.set('graphics', 'height', 1000)
    # Config.set('graphics', 'minimum_width', '1000')
    # Config.set('graphics', 'window_state', 'maximized')
    # Config.set('graphics', 'borderless', True)
    Config.set('graphics', 'resizable', False)
    Config.write()
    MainApp().run()

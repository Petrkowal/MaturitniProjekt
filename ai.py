import tensorflow as tf
import numpy as np
from random import randint


# def f(x):
#     return -2 / 7 * x ** 2 + 80 / 7 * x + 2 / 7

# Vytvoří model podle struktury
def create_model(structure=None):
    if structure is None:
        structure = [["dense", {"units": 16, "activation": "relu"}],
                     ["dense", {"units": 16, "activation": "relu"}]]

    model = tf.keras.models.Sequential()
    tf.keras.backend.set_floatx('float64')
    for i, layer in enumerate(structure):
        if i == 0:  # První vrstva (vstupní)
            model.add(tf.keras.layers.Dense(layer[1]["units"], activation=layer[1]["activation"], input_dim=2))
        else:  # Skryté vrstvy
            model.add(tf.keras.layers.Dense(layer[1]["units"], activation=layer[1]["activation"]))
    model.add(tf.keras.layers.Dense(1, activation="tanh"))  # Výstupní vrstva
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=["accuracy"])

    return model


# Náhodně vygeneruje data pro trénování
def create_train_data(number_of_data, win_hei):
    data = []
    for i in range(number_of_data):
        bird_center_y = randint(125, win_hei - 25)
        lower_pipe_y = randint(250, win_hei - 150) - 100  # Spodní, horní nranice; polovina GAP_SIZE
        data.append([bird_center_y, lower_pipe_y])
    return data


# Podle dat zhodnotí (podmínkami), jestli by za daných situací měl skočit, nebo neměl skočit
def calculate_outputs(data, bird_height):
    outputs = []
    for i in data:
        # Jestli je pod úrovní následující trubky, měl by skočit, jinak ne
        if i[0] - bird_height / 2 < 130 or i[0] - bird_height / 2 < i[1] + 15:
            outputs.append(1)
        else:
            outputs.append(0)
    return outputs


# Přemapuje data mezi 0 a 1
def map_data(data, win_hei, win_width):
    data = [data[0] / win_hei, data[1] / win_hei]
    data = np.array(data).reshape(1, 2)
    return data


'''
Třída BirdAI - pro NN
Vstupy:
    šířka, výška okna
    výška ptáka
    počet trénovacích dat
    počet epoch (trénování)
Metody:
    create_ai() - nechá vytvořit model a trénovací data, spustí trénování modelu
    map_all_data() - nechá přemapovat vstupy mezi 0 a 1
    trin_model() - natrénuje model
    predict(data) - metoda se vyvolává z hlavní smyčky - pošle vstupní data a NN se rozhodne, zda skočit
'''


class BirdAI:
    def __init__(self, window_height, window_width, bird_height, train_data=50000, epochs=2):
        self.TRAIN_DATA = train_data  # Počet trénovacích dat
        self.EPOCHS = epochs  # Počet epoch trénování
        self.bird_height = bird_height
        self.window_height = window_width
        self.window_width = window_width
        self.dataset = []  # Dataset pro učení NN
        self.model = None
        self.create_ai()
        # inputs:
        #       bird y
        #       vzdálenost bird - pipe
        #       y - lower pipe
        #       y - upper pipe

    def create_ai(self):
        self.model = create_model()
        # Vytvoření trénovacích dat
        self.dataset.append(create_train_data(self.TRAIN_DATA, self.window_height))
        # Vytvoření outputů podle trénovacích dat
        self.dataset.append(calculate_outputs(self.dataset[0], self.bird_height))
        self.map_all_data()  # Přemapování dat mezi 0 a 1
        # Převedení na numpy array, reshape
        self.dataset[0] = np.array(self.dataset[0]).reshape(self.TRAIN_DATA, 2)
        self.dataset[1] = np.array(self.dataset[1]).reshape(self.TRAIN_DATA, 1)
        self.train_model()  # Trénování modelu

    # Přemapování: 0 - 1
    def map_all_data(self):
        for i in range(self.TRAIN_DATA):
            self.dataset[0][i] = map_data(self.dataset[0][i], self.window_height, self.window_width)

    # Trénování modelu
    def train_model(self):
        self.model.fit(self.dataset[0], self.dataset[1], epochs=self.EPOCHS, batch_size=32, shuffle=True)

    # Protáhne vstupní data modelem, výsledek returnuje
    def predict(self, data):
        data = map_data(data, self.window_height, self.window_width)
        return self.model(np.array(data).reshape(1, 2))  # Stejné jako model.predict(), ale rychlejší

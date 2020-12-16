import tensorflow as tf
import numpy as np
from random import randint


# Jednodušší = může skočit, i když je v mezeře a nerozbije se o vrchní trubku (skok není dost dlouhý)
# Složitější = nemůže skočit v mezeře - 1.

# dx, dy = 2 * 5 * 20, 2 * 114,5
# dy, dy = 405, 240 = relativní souřadnice vrcholu kvadra. funkce
# r, s = ?, ? (vzít ze hry)
# r = pipe_center - dx
# A[x,y] = bird[x,y]
# V[x + dx, y + dy] = Vrchol kvadra. funkce
# T[x + r, y + s] = Target point
# T[xr, yr] = Target point
# x + r = xr
# pipe_center - dx = xr
# pipe_center - dx = x + r

# dx = ZHRUBA 40 nebo 41
# dy = ZHRUBA (+- 10) 230 ASI ??

# if f(x) == f(x + dx) - dy == f(x + r) - s

# CHECKOVANI OBDELNIKU POMOCI abs(a - b) < obdelnik_width (nebo height) / 2

# if abs(f(x) - (f(x + dy) - dy)) < 20 and abs(f(x) - (f(x + r) - s)) < 20:
# if abs(f(x) - (f(x + dy) - dy)) < 20 and abs(f(x) - (f(x + r) - s)) < 20:

def f(x):
    return -2 / 7 * x ** 2 + 80 / 7 * x + 2 / 7


def create_model():
    structure = [["dense", {"units": 16, "activation": "relu"}],
                 ["dense", {"units": 16, "activation": "relu"}]]

    model = tf.keras.models.Sequential()
    tf.keras.backend.set_floatx('float64')
    for i, layer in enumerate(structure):
        if i == 0:
            model.add(tf.keras.layers.Dense(layer[1]["units"], activation=layer[1]["activation"], input_dim=4))
        else:  # Hidden layers
            model.add(tf.keras.layers.Dense(layer[1]["units"], activation=layer[1]["activation"]))
    model.add(tf.keras.layers.Dense(1, activation="tanh"))
    model.compile(loss='mean_squared_error', optimizer='adam', metrics=["accuracy"])

    return model


def create_train_data(number_of_data, win_hei, win_wid, bird_height):
    data = []
    for i in range(number_of_data):
        bird_center_y = randint(125, win_hei - 25)
        distance_to_pipe = randint(0, win_wid)
        pipe_center = randint(250, win_hei - 150)
        lower_pipe_y = pipe_center - 100
        upper_pipe_y = pipe_center + 100
        data.append([bird_center_y, distance_to_pipe, lower_pipe_y, upper_pipe_y])
    return data


def calculate_outputs(data, bird_height):
    outputs = []
    for i in data:
        # Jednonušší
        # if i[0] - bird_height / 2 < 130 or i[0] - bird_height / 2 < i[2] + 25:
        #     outputs.append(1)
        # else:
        #     outputs.append(-1)

        # Složitější
        dx = 40
        dy = 230
        pipe_x = i[1]
        pipe_center = i[2] + 100
        x = 0
        y = i[0]
        r = pipe_x - dx
        s = pipe_center - dy

        # CHECK PŘES PRINT JEŠTĚ!!!!!!
        # 20 -> tolerance obdelniku
        # 1. řadek = 1. jump
        # 2. řadek = přes trubku - 20 taky tolerance
        if abs(f(r) - (pipe_center - dy)) < 20:
            outputs.append(1)
        elif abs(pipe_x - dx) < 20 and abs(pipe_center - dy) < 20:
            outputs.append(1)

        # elif i[0] - bird_height / 2 < i[2] + 25 and f(r) - dy < pipe_center - dy -1000:
        #     outputs.append(1)

        else:
            outputs.append(0)

        # if (abs(f(x) - (f(x + dy) - dy)) < 10 and abs(f(x) - (f(x + r) - s)) < 20):
        #     jump()
        # elif bird_y < pipe_y:
        #         1
        # else
        #     -1

    return outputs


def validate(data, win_hei, win_width):
    data = [data[0] / win_hei, data[1] / win_width, data[2] / win_hei, data[3] / win_hei]
    data = np.array(data).reshape(1, 4)
    return data


class BirdAI:

    def __init__(self, window_height, window_width, bird_height, train_data=50000, epochs=2):
        self.TRAIN_DATA = train_data
        self.EPOCHS = epochs
        self.bird_height = bird_height
        self.window_height = window_width
        self.window_width = window_width
        self.dataset = []
        self.model = create_model()
        self.dataset.append(create_train_data(self.TRAIN_DATA, self.window_height, self.window_width, self.bird_height))
        self.dataset.append(calculate_outputs(self.dataset[0], bird_height))
        self.scale_data()
        self.dataset[0] = np.array(self.dataset[0]).reshape(self.TRAIN_DATA, 4)
        self.dataset[1] = np.array(self.dataset[1]).reshape(self.TRAIN_DATA, 1)
        self.train_model()
        # inputy:
        #       bird y
        #       vzdálenost bird - pipe
        #       y - lower pipe
        #       y - upper pipe

    def scale_data(self):
        print(self.dataset[0])
        for i in range(self.TRAIN_DATA):
            self.dataset[0][i] = validate(self.dataset[0][i], self.window_height, self.window_width)
        print(self.dataset[0])

    def train_model(self):
        self.model.fit(self.dataset[0], self.dataset[1], epochs=self.EPOCHS, batch_size=32, shuffle=True)

    def predict(self, data):
        data = validate(data, self.window_height, self.window_width)
        return self.model(np.array(data).reshape(1, 4))  # Stejné jako model.predict(), ale rychlejší

import tensorflow as tf
import numpy as np
from random import randint


# Jednodušší = může skočit, i když je v mezeře a nerozbije se o vrchní trubku (skok není dost dlouhý)
# Složitější = nemůže skočit v mezeře - 1.
def create_model():
    structure = [["dense", {"units": 8, "activation": "relu"}],
                 ["dense", {"units": 8, "activation": "relu"}]]

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
        if i[0] - bird_height / 2 < 130 or i[0] - bird_height / 2 < i[2] + 25:
            outputs.append(1)
        else:
            outputs.append(0)
    return outputs


def validate(data, win_hei, win_width):
    data = [data[0] / win_hei, data[1] / win_width, data[2] / win_hei, data[3] / win_hei]
    data = np.array(data).reshape(1, 4)
    return data


class BirdAI:
    TRAIN_DATA = 100000

    def __init__(self, window_height, window_width, bird_height):
        self.bird_height = bird_height
        self.window_height = window_width
        self.window_width = window_width
        self.dataset = []
        self.model = create_model()
        self.dataset.append(create_train_data(self.TRAIN_DATA, self.window_height, self.window_width, self.bird_height))
        self.dataset.append(calculate_outputs(self.dataset[0], bird_height))

        print(self.dataset[0])
        for i in range(self.TRAIN_DATA):
            self.dataset[0][i] = validate(self.dataset[0][i], self.window_height, self.window_width)
        print(self.dataset[0])
        self.dataset[0] = np.array(self.dataset[0]).reshape(self.TRAIN_DATA, 4)
        self.dataset[1] = np.array(self.dataset[1]).reshape(self.TRAIN_DATA, 1)
        self.train_model()
        # inputy:
        #       bird y
        #       vzdálenost bird - pipe
        #       y - lower pipe
        #       y - upper pipe

    def train_model(self):
        self.model.fit(self.dataset[0], self.dataset[1], epochs=1, batch_size=32, shuffle=True)

    def predict(self, data):
        data = validate(data, self.window_height, self.window_width)
        return self.model(np.array(data).reshape(1, 4))  # Stejné jako model.predict(), ale rychlejší

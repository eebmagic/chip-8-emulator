import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.animation as animation

WIDTH, HEIGHT = 64, 32
def generate_data():
    return np.round(np.random.rand(HEIGHT, WIDTH))

def update(data):
    mat.set_data(data)
    return mat 

def data_gen():
    while True:
        yield generate_data()

fig, ax = plt.subplots()
mat = ax.matshow(generate_data())
ani = animation.FuncAnimation(fig, update, data_gen, interval=1_000,
                              save_count=50)
plt.show()
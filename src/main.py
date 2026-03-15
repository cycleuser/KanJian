import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Simple magma eruption and solidification simulation
# This is a basic 1D model of lava flow cooling

class MagmaSimulation:
    def __init__(self, length=100, dx=1.0, dt=0.1, alpha=0.1, cooling_rate=0.01):
        self.length = length
        self.dx = dx
        self.dt = dt
        self.alpha = alpha  # thermal diffusivity
        self.cooling_rate = cooling_rate
        self.x = np.linspace(0, length*dx, length)
        self.T = np.ones(length) * 1200  # initial temperature in Celsius, magma temp
        self.T[0] = 1200  # eruption point
        self.solidified = np.zeros(length, dtype=bool)
        self.solidification_temp = 800  # temperature at which solidification starts

    def update(self):
        # Heat equation: dT/dt = alpha * d²T/dx² - cooling
        d2T_dx2 = np.gradient(np.gradient(self.T, self.dx), self.dx)
        self.T += self.dt * (self.alpha * d2T_dx2 - self.cooling_rate * (self.T - 20))  # ambient temp 20C

        # Solidification: if T < solidification_temp, mark as solidified
        self.solidified = self.T < self.solidification_temp

        # Eruption: keep source hot
        self.T[0] = 1200

    def animate(self, frames=200):
        fig, ax = plt.subplots()
        line, = ax.plot(self.x, self.T, 'r-')
        solidified_line, = ax.plot(self.x, self.solidified * 800, 'k-')  # black for solidified

        def animate_frame(i):
            self.update()
            line.set_ydata(self.T)
            solidified_line.set_ydata(self.solidified * 800)
            return line, solidified_line

        ani = animation.FuncAnimation(fig, animate_frame, frames=frames, interval=50, blit=True)
        plt.xlabel('Distance (m)')
        plt.ylabel('Temperature (C)')
        plt.title('Magma Eruption and Solidification Simulation')
        plt.show()

if __name__ == "__main__":
    sim = MagmaSimulation()
    sim.animate()
import numpy as np
import matplotlib.pyplot as plt


def distance_to_time(distance):
    p = np.array([ 0.03314466, -0.07916051])
    return p[0] * distance + p[1]


def main():
    times = np.arange(7) + 1
    distances = np.array([
        [31, 31.5, 31.5],  # 1s
        [64, 62, 62.5],  # 2s
        [94.5, 91, 93],  # 3s
        [124.5, 122, 124],  # 4s
        [156, 155, 154],  # 5s
        [185, 189, 187],  # 6s
        [203, 208, 216],  # 7s
    ])

    avg_distances = np.mean(distances, axis=1)

    p = np.polyfit(avg_distances, times, 1)

    def distance_to_time_fit(distance):
        return p[0] * distance + p[1]

    print(f'{p = }')

    plt.figure()
    plt.scatter(avg_distances, times)
    distances_to_plot = np.linspace(0, 210, 20)
    plt.plot(distances_to_plot, distance_to_time_fit(distances_to_plot))
    plt.xlabel("Average Distance (cm)")
    plt.ylabel("Time (s)")
    plt.title("Distance vs Time")
    plt.show()


if __name__ == "__main__":
    main()

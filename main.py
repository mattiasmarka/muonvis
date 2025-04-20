import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

dtype = np.dtype([("event_id", float),
                     ("x", float),
                     ("y", float),
                     ("z", float),
                     ("time", float),
                     ("deposited_energy", float),
                     ("track_id", int),
                     ("detector_id", int),
                     ("kinetic_energy", float),
                     ("particle_type", int),
                     ("dunno", str)])


def construct_tracks(data):
    tracks = dict()
    for row in data:
        key = (row["event_id"], row["track_id"])
        if key not in tracks:
            tracks[key] = []
        tracks[key].append((row["x"], row["y"], row["z"]))
    return tracks


def plot_tracks(ax, tracks):
    lines = []
    for key in tracks:
        x, y, z = zip(*tracks[key])
        lines.append(ax.plot(x, y, z, "red")[0])
    return lines


def main(nframes=1000, time_window=30e9, vislength=60e9):
    data = np.genfromtxt(open("example.csv"), delimiter=",", dtype=dtype)
    min_time, max_time = data["time"].min(), data["time"].max()
    data = data[data["time"] <= min_time + vislength]

    min_x, max_x = data["x"].min(), data["x"].max()
    min_y, max_y = data["y"].min(), data["y"].max()
    min_z, max_z = data["z"].min(), data["z"].max()

    fig = plt.figure(dpi=300)
    ax = fig.add_axes((0, 0, 1, 1), projection="3d", facecolor="k")

    ax.view_init(elev=0, azim=90) # Camera angel
    ax.set_proj_type('ortho')
    ax.set_facecolor('k')
    ax.grid(False)
    ax.set_axis_off()

    # make the panes transparent
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # make the grid lines transparent
    ax.xaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax.yaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)
    ax.zaxis._axinfo["grid"]['color'] = (1, 1, 1, 0)

    def set_lims():
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_x, max_x)
        #ax.set_zlim(min_z, max_x)

        ax.set_zlim(-200, 0)

    def update(frame):
        # time = ((max_time - min_time) / nframes) * frame + min_time
        time = min_time + frame * 1e9/30
        ddata = data[np.where(np.logical_and(data["time"] > time - time_window * 0.5,
                                                   data["time"] < time + time_window * 0.5))]
        tracks = construct_tracks(ddata)
        ax.clear()
        set_lims()
        return plot_tracks(ax, tracks)

    anim = animation.FuncAnimation(fig, update, frames=list(range(1, nframes + 1)), blit=True)
    videowriter = animation.FFMpegWriter(fps=30)
    anim.save("example.mp4", writer=videowriter)


if __name__ == "__main__":
    main()

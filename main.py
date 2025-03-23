import numpy
from matplotlib import pyplot
from matplotlib import animation

dtype = numpy.dtype([("event_id", int),
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
        lines.append(ax.plot(x, y, z, "k")[0])
    return lines


def main(nframes=1000, time_window=30e9):
    data = numpy.genfromtxt(open("example.csv"),
                            delimiter=",",
                            dtype=dtype)
    min_time, max_time = data["time"].min(), data["time"].max()

    min_x, max_x = data["x"].min(), data["x"].max()
    min_y, max_y = data["y"].min(), data["y"].max()
    min_z, max_z = data["z"].min(), data["z"].max()
    fig = pyplot.figure(dpi=300)
    ax = fig.add_axes((0, 0, 1, 1), projection="3d")
    tracks = construct_tracks(data)
    print(max([len(tracks[key]) for key in tracks]))
    if True:
        return

    def set_lims():
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_x, max_x)
        ax.set_zlim(min_z, max_x)

    def update(frame):
        time = ((max_time - min_time) / nframes) * frame + min_time
        ddata = data[numpy.where(numpy.logical_and(data["time"] > time - time_window * 0.5,
                                                   data["time"] < time + time_window * 0.5))]
        tracks = construct_tracks(ddata)
        ax.clear()
        set_lims()
        return plot_tracks(ax, tracks)
    anim = animation.FuncAnimation(
        fig, update, frames=list(
            range(
                1, nframes + 1)), blit=True)
    videowriter = animation.FFMpegWriter(fps=30)
    anim.save("example.mp4", writer=videowriter)


if __name__ == "__main__":
    main()

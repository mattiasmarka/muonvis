import numpy

dtype = numpy.dtype([("event_id", float),
                     ("x", float),
                     ("y", float),
                     ("z", float),
                     ("time", float),
                     ("deposited_energy", float),
                     ("track_id", int),
                     ("detector_id", int),
                     ("kinetic_energy", float),
                     ("particle_type", str),
                     ("dunno", str)])


def get_data(fname):
    return numpy.loadtxt(fname, dtype=dtype, delimiter=",")

def construct_tracks(data):
    tracks = dict()
    for row in data:
        key = (row["event_id"], row["track_id"])
        if key not in tracks:
            tracks[key] = []
        tracks[key].append((row["x"], row["y"], row["z"]))
    return tracks
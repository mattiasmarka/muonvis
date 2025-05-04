import numpy
import unittest

dtype = numpy.dtype([("event_id", int),
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

def tracks_in_det(data):
    tracks_in_det = dict()
    for row in data:
        key = (row["event_id"], row["track_id"])
        if key not in tracks_in_det:
            tracks_in_det[key] = []
        tracks_in_det[key].append((row["x"], row["y"], row["z"]))
    return tracks_in_det

def line_from_pts(p0, p1):
    x1, y1, z1 = p0
    x2, y2, z2 = p1
    ax, ay, by = x1, y1, z1
    bx, by, bz = x2 - x1, y2 - y1, z2 - z1
    return ax, ay, by, bx, by, bz

def safe_div(a, b):
    if b == 0.0:
        return a * float("inf")
    else:
        return a / b

def line_intrscts_plane(line, plane):
    ax, ay, az, bx, by, bz = line
    cx, cy, cz, d = plane
    t = -safe_div(d + ax*cx + ay*cy + az*cz, bx*cx + by*cy + bz*cz)
    return (ax + bx*t, ay + by*t, az + bz * t)

XMIN, XMAX = 0, 1024
YMIN, YMAX = 0, 2048
ZMIN, ZMAX = 170, 770

def tracks_in_chmbr(tracks_in_det):
    tracks_in_chmbr = dict()
    for key in tracks_in_det:
        track_in_det = tracks_in_det[key]
        if len(track_in_det) <= 1:
            continue
        p0, p1 = track_in_det[:2]
        line = line_from_pts(p0, p1)
        intersects = []
        for xp in (XMIN, XMAX):
            intersect = line_intrscts_plane(line, (1, 0, 0, -xp))
            x, y, z = intersect
            if (YMIN <= y <= YMAX) and (ZMIN <= z <= XMAX):
                intersects.append(intersect)
        if len(intersects) < 2:
            for yp in (YMIN, YMAX):
                if len(intersects) == 2:
                    break
                intersect = line_intrscts_plane(line, (0, 1, 0, -yp))
                x, y, z = intersect
                if (XMIN <= x <= XMAX) and (ZMIN <= z <= XMAX):
                    intersects.append(intersect)
        if len(intersects) < 2:
            for zp in (ZMIN, ZMAX):
                if len(intersects) == 2:
                    break
                intersect = line_intrscts_plane(line, (0, 0, 1, -zp))
                x, y, z = intersect
                if (XMIN <= x <= XMAX) and (YMIN <= y <= YMAX):
                    intersects.append(intersect)
        if len(intersects) <= 1:
            continue
        tracks_in_chmbr[key] = intersects
    return tracks_in_chmbr
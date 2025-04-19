import ursina
import numpy
from numpy import random

from data import *

SCALE_DET = 5000
SCALE_VIS = 6

LOOKBACK_TIME = 60e9 # ns
LIFE_TIME = .5e9 # ns

def vec3(x, y, z):
    scale = SCALE_VIS / SCALE_DET
    return ursina.Vec3(x * scale , y * scale, z * scale)

app = ursina.Ursina()
data = get_data("example.csv")

min_time_det = data["time"].min()
min_time_vis = ursina.time.time_ns()

app = ursina.Ursina()

entities = {}

def update():
    global entities
    time = ursina.time.time_ns() - min_time_vis
    time_det = min_time_det + time
    where = numpy.logical_and(data["time"] > time_det - LOOKBACK_TIME,
                              data["time"] <= time_det + time)
    tracks = construct_tracks(data[where])
    for entity in entities:
        if entity in tracks:
            entities[entity].alpha /= 1.005
        if entities[entity].alpha <= 1.005**(-LIFE_TIME) / 1.005 :
            ursina.destroy(entities[entity])
            entities[entity] = False
    for track in tracks:
        if track not in entities:
            entities[track] = ursina.Entity(
                model=ursina.Mesh(
                    vertices=[vec3(*coords) for coords in tracks[track]],
                    mode="line"))
    entities = {entity:entities[entity] for entity in entities if entities[entity] != False}
        
app.run()
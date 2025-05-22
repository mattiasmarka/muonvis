import ursina
import ursina.prefabs.video_recorder as video_recorder
import os
import shutil
import numpy
import cv2

from data import *

SCALE_DET = 2048
SCALE_VIS = 6

SCALE = SCALE_VIS / SCALE_DET

HALFLIFE = 2e9 # ns
MAXLIFE = 8e9 # ns
LOOKBACK_TIME = 1e9 # ns

FANRADIUS = 560 / 2

SCREENDIR = "./screenshots"

DUR = 60

FPS = 24

fix = lambda x, xmin, xmax: (x - xmin - (xmax - xmin) / 2) * SCALE

def det_to_vis(x, y, z):
    return ursina.Vec3(fix(y, YMIN, YMAX),
                       fix(z, ZMIN, ZMAX),
                       -fix(x, XMIN, XMAX))
def draw_box():
    for y in (YMIN, YMAX):
        for z in (ZMIN, ZMAX):
            color = ursina.color.gray
            if y == YMIN and z == ZMIN:
                color = ursina.color.red
            ursina.Entity(model=ursina.Mesh(vertices=[det_to_vis(XMIN, y, z),
                                                      det_to_vis(XMAX, y, z)],
                                            mode="line"),
                          color=color)
    for x in (XMIN, XMAX):
        for z in (ZMIN, ZMAX):
            color = ursina.color.gray
            if x == XMIN and z == ZMIN:
                color = ursina.color.green
            ursina.Entity(model=ursina.Mesh(vertices=[det_to_vis(x, YMIN, z),
                                                      det_to_vis(x, YMAX, z)],
                                            mode="line"),
                          color=color)
    for x in (XMIN, XMAX):
        for y in (YMIN, YMAX):
            color = ursina.color.gray
            if x == XMIN and y == YMIN:
                color = ursina.color.blue
            ursina.Entity(model=ursina.Mesh(vertices=[det_to_vis(x, y, ZMIN),
                                                      det_to_vis(x, y, ZMAX)],
                                            mode="line"),
                          color=color)
    return

def draw_fan():
    color = ursina.color.gray
    ursina.Entity(model=ursina.Circle(radius=FANRADIUS * SCALE, mode="line", resolution=64),
                  color=ursina.color.white,
                  position=det_to_vis(XMAX, (YMAX - YMIN) / 2, ZMIN + (ZMAX - ZMIN) / 2))

entities = dict()
min_time_vis = ursina.time.time_ns()

def add_entities(tracks):
    global entities
    time = ursina.time.time_ns() - min_time_vis
    for key in tracks:
        creation_time = time
        if key in entities:
            continue
        entities[key] = (ursina.Entity(
            model=ursina.Mesh(
                vertices=[det_to_vis(*coords) for coords in tracks[key]],
                mode="line"),
            color=ursina.color.blue),
                         creation_time)
    return

def fade_out_entities():
    global entities
    time = ursina.time.time_ns() - min_time_vis
    for key in entities:
        entity, creation_time = entities[key]
        if entity.alpha > 0:
            entity.alpha = 2**(-(time - creation_time) / HALFLIFE)
    return

def clean_entities():
    global entities
    time = ursina.time.time_ns() - min_time_vis
    for key in entities:
        entity, creation_time = entities[key]
        if time - creation_time >= MAXLIFE:
            entity.alpha = 0
            ursina.destroy(entity)
            entities[key] = False
    entities = {key:entities[key] for key in entities if entities[key] != False}
    return

data = get_data("example.csv")

min_time_det = data["time"].min()

encoder = None
out = None

ttime = 0

app = ursina.Ursina(size=(1000, 1000))
app.fps = FPS

last_time = None

def update():
    global encoder, out, ttime, last_time
    current_time = ursina.time.time()
    delta_time = current_time - last_time
    if delta_time < 1.0 / FPS:
        ursina.time.sleep(1 / FPS - delta_time)
    last_time = current_time
    time = ursina.time.time_ns() - min_time_vis
    time_det = min_time_det + time
    where = numpy.logical_and(data["time"] > time_det - LOOKBACK_TIME,
                              data["time"] <= time_det)
    tracks = tracks_in_chmbr(tracks_in_det(data[where]))
    add_entities(tracks)
    fade_out_entities()
    clean_entities()
    if ttime == 0.0:
        print("make!")
        encoder = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter('%d.mp4' % ursina.time.time(), encoder, FPS, (app.win.get_x_size(), app.win.get_y_size()))
    image = numpy.frombuffer(app.win.getScreenshot().get_ram_image_as("RGBA").get_data(), dtype=numpy.uint8)
    image = image.reshape(app.win.get_x_size(), app.win.get_y_size(), 4)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    image = numpy.flipud(image)
    ttime += ursina.time.dt
    out.write(image)
    if ttime >= DUR:
        print("release!")
        out.release()
        ttime = 0
    return

last_time = ursina.time.time()

if __name__ == "__main__":
    ursina.camera.orthographic = True
    ursina.camera.fov=1.65
    ursina.Sky(color=ursina.color.color(0,0,0))
    # ursina.EditorCamera(rotate_around_mouse_hit=True)
    # draw_box()
    # draw_fan()
    app.run()

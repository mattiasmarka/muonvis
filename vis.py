import ursina

from data import *

SCALE_DET = 2048
SCALE_VIS = 6

SCALE = SCALE_VIS / SCALE_DET

HALFLIFE = 1e9 # ns
MAXLIFE = 5e9 # ns
LOOKBACK_TIME = 15e9 # ns

def det_to_vis(x, y, z):
    fix = lambda x, xmin, xmax: (x - xmin - (xmax - xmin) / 2) * SCALE
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

def update():
    time = ursina.time.time_ns() - min_time_vis
    time_det = min_time_det + time
    where = numpy.logical_and(data["time"] > time_det - LOOKBACK_TIME,
                              data["time"] <= time_det)
    tracks = tracks_in_chmbr(tracks_in_det(data[where]))
    add_entities(tracks)
    fade_out_entities()
    clean_entities()
    return
    
if __name__ == "__main__":
    app = ursina.Ursina()
    ursina.Sky(color=ursina.color.color(0,0,0))
    ursina.EditorCamera(rotate_around_mouse_hit=True)
    draw_box()
    app.run()

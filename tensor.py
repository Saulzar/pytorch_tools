import torch
from tools.image import index_map, cv


def split(t, dim = 0):
    return [chunk.squeeze(dim) for chunk in t.chunk(t.size(dim), dim)]


def tile_batch(t, cols=int(6)):
    assert(t.dim() == 4)

    if(t.size(0)) == 1:
        return t[0]

    h = t.size(1)
    w = t.size(2)

    rows = (t.size(0) - 1) // cols + 1
    out = t.new(rows * h, cols * w, t.size(3)).fill_(0)

    for i in range(0, t.size(0)):
        x = i % cols
        y = i // cols

        tile = out.narrow(1, x * w, w).narrow(0, y * h, h)
        tile.copy_(t[i])

    return out

def show_batch_t(data, cols=int(6), scale=1):
    return show_batch(data.permute(0, 2, 3, 1), cols=cols, scale=scale)


def show_batch(t, cols=int(6), scale=1):
    tiled = tile_batch(t, cols)
    tiled = cv.resize (tiled, (tiled.size(0) * scale, tiled.size(1) * scale), interpolation = cv.INTER_NEAREST)

    return cv.display(tiled)

def show_indexed_batch(t, cols=int(6)):
    colorizer = index_map.colorizer_t(255)
    tiled = tile_batch(t, cols)

    color = colorizer(tiled)
    return cv.display(color)

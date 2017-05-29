
import torch
import random
import math

from tools import tensor
import tools.image.cv as cv

def random_check(lower, upper):
    if (lower >= upper):
        return (lower + upper) / 2
    else:
        return random.randint(lower, upper)

def random_region(image, size, border = 0):

    w, h = image.size(1), image.size(0)
    tw, th = size

    # assert(w >= tw + border * 2 and h >= th + border * 2)

    x1 = random_check(border, w - tw - border)
    y1 = random_check(border, h - th - border)

    return ((x1 + tw * 0.5, y1 + th * 0.5), (tw * 0.5, th * 0.5))



def scaling(sx, sy):
    return torch.DoubleTensor ([
      [sx, 0, 0],
      [0, sy, 0],
      [0, 0, 1]])

def rotation(a):
    sa = math.sin(a)
    ca = math.cos(a)

    return torch.DoubleTensor ([
      [ca, -sa, 0],
      [sa,  ca, 0],
      [0,   0, 1]])

def translation(tx, ty):
    return torch.DoubleTensor ([
      [1, 0, tx],
      [0, 1, ty],
      [0, 0, 1]])


def adjust_colors(image, gamma_dev = 0.2):
    gamma = random.uniform(1-gamma_dev, 1+gamma_dev)
    return cv.adjust_gamma(image, gamma)


def compose(fs):
    def composed(image, targets):
        for f in fs:
            image, targets = f(image, targets)
        return image, targets
    return composed



def normalize(mean=[0.406, 0.456, 0.485], std=[0.225, 0.224, 0.229]):
    def f(image, target):
        image = image.float().div_(255)
        for i in range(0, 2):
            image.select(2, i).sub_(mean[i]).div_(std[i])
        return image, target.long()
    return f


def scale_to(dest_size):
    def f(image, target):
        image = cv.warpAffine(image, t, dest_size, flags = cv.INTER_CUBIC, borderMode = cv.BORDER_CONSTANT)
        target = cv.warpAffine(target, t, dest_size, flags = cv.INTER_NEAREST, borderMode = cv.BORDER_CONSTANT)
        return image, target
    return f



def random_crop(min_crop, dest_size, max_scale = 1, border = 20, squash_dev = 0.1, rotation_dev = 5, gamma_dev = 0.1):
    def crop(image, target):

        base_scale = random.uniform(1, min(max_scale, image.size(1) / dest_size[0], image.size(0) / dest_size[1]))
        sx, sy = base_scale, base_scale * random.uniform(1-squash_dev, 1+squash_dev)

        crop_size = (math.floor(sx * min_crop[0]), math.floor(sy * min_crop[1]))
        centre, extents = random_region(image, crop_size, border)

        toCentre = translation(-centre[0], -centre[1])
        fromCentre = translation(dest_size[0] * 0.5, dest_size[1] * 0.5)

        flip = 1 if random.uniform(0.0, 1.0) > 0.5 else -1

        r = rotation(random.uniform(-rotation_dev, rotation_dev) * (math.pi / 180))
        s = scaling(flip / sx, 1 / sy)
        t = fromCentre.mm(s).mm(r).mm(toCentre)

        image = cv.warpAffine(image, t, dest_size, flags = cv.INTER_CUBIC, borderMode = cv.BORDER_CONSTANT)
        target = cv.warpAffine(target, t, dest_size, flags = cv.INTER_NEAREST, borderMode = cv.BORDER_CONSTANT)

        for d in range(0, 2):
            image.select(2, d).copy_(adjust_colors(image.select(2, d), gamma_dev))

        return image, target.long()
    return crop

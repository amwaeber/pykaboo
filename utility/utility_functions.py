import numpy as np


def test():
    pass


def two_d_gaussian_sym(xy, amplitude, xo, yo, sigma, offset):
    xo = float(xo)
    yo = float(yo)
    g = offset + amplitude * np.exp(- (((xy[0] - xo) ** 2) + ((xy[1] - yo) ** 2)) / (2 * sigma ** 2))
    return g.ravel()


def affine_trafo(raw_coords, real_coords):
    primary = np.array(raw_coords)
    secondary = np.array(real_coords)

    # Pad the data with ones, so that our transformation can do translations too
    if primary.shape[0] >= 3:
        pad = lambda x: np.hstack([x, np.ones((x.shape[0], 1))])
        x = pad(primary)
        y = pad(secondary)
        a, res, rank, s = np.linalg.lstsq(x, y, rcond=1e-4)
        return a
    else:
        return []


def flatten_list(lst):
    return [item for sublist in lst for item in sublist]
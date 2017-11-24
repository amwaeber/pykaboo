import dxfgrabber
import os
from dxfwrite import DXFEngine as dxf
from matplotlib import patches as patches
from matplotlib.path import Path

from utility.config import paths
from utility.utility_functions import flatten_list


class DwgXchFile:
    def __init__(self):
        self.location = None
        self.entities = []
        self.new_entities = []
        self.layers = []
        self.shapes = []
        self.patch_list = []
        self.new_patch_list = []

    def load(self, fname, flayers, fshapes):
        self.location = fname
        self.layers = flayers
        self.shapes = fshapes
        dwg_in = dxfgrabber.readfile(fname)
        for l in range(len(self.layers)):
            all_layer_cont = [entity for entity in dwg_in.entities if entity.layer == self.layers[l]]
            if self.shapes[l] == 'POLYLINE':
                for entity in all_layer_cont:
                    if not (entity.points[0] == entity.points[-1]):
                        entity.points.append(entity.points[0])
            self.entities.append(all_layer_cont)

        for l in range(len(self.layers)):
            if self.layers[l] == 'ALIGN':
                for entity in self.entities[l]:
                    codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points) - 2)] + [Path.CLOSEPOLY]
                    path = Path([p[:-1] for p in entity.points], codes)
                    self.patch_list.append(patches.PathPatch(path, fill=False, color='c'))
            elif self.layers[l] == 'COORD':
                for entity in self.entities[l]:
                    self.patch_list.append(patches.Circle(entity.center[:-1], entity.radius, fill=False, color='g'))
            elif self.layers[l] == 'MAGNET':
                for entity in self.entities[l]:
                    codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points) - 2)] + [Path.CLOSEPOLY]
                    path = Path([p[:-1] for p in entity.points], codes)
                    self.patch_list.append(patches.PathPatch(path, fill=False, color='r'))

    def add(self, magnet_name, pos):
        dwg_mag = dxfgrabber.readfile(os.path.join(paths['dxf'], magnet_name + '.dxf'))
        all_layer_cont = [entity for entity in dwg_mag.entities if entity.layer == 'MAGNET']
        for entity in all_layer_cont:
            entity.points = [(pt[0] + 470 + pos[0], pt[1] + 470 + pos[1]) for pt in entity.points]
            if not (entity.points[0] == entity.points[-1]):
                entity.points.append(entity.points[0])
        self.new_entities.append(all_layer_cont)
        added_patches = []
        for entity in self.new_entities[-1]:
            codes = [Path.MOVETO] + [Path.LINETO for i in range(len(entity.points) - 2)] + [Path.CLOSEPOLY]
            path = Path(entity.points, codes)
            added_patches.append(patches.PathPatch(path, fill=False, color='y'))
        self.new_patch_list.append(added_patches)

    def remove_last(self):
        self.new_entities.pop()
        self.new_patch_list.pop()

    def save(self, fname):
        dwg_out = dxf.drawing(fname)
        for ind, layer in enumerate(self.layers):
            dwg_out.add_layer(layer, color=ind + 1)
        for align in self.entities[0]:
            pline = dxf.polyline(align.points, color=256, layer='ALIGN')
            pline.close()
            dwg_out.add(pline)
        for coord in self.entities[1]:
            dwg_out.add(dxf.circle(coord.radius, coord.center, color=256, layer='COORD'))
        for mag in self.entities[2]:
            pline = dxf.polyline(mag.points, color=256, layer='MAGNET')
            pline.close()
            dwg_out.add(pline)
        for mag in flatten_list(self.new_entities):
            pline = dxf.polyline(mag.points, color=256, layer='MAGNET')
            pline.close()
            dwg_out.add(pline)
        dwg_out.save()



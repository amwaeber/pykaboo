#!python3

import pylab

tum_raw = [
(  0, 101, 189),  #TUM Blue   
(65, 190, 255),  #TUM Light Blue 
(145, 172, 107),  #TUM Green     
#(181, 202, 130),  #TUM Light Green 
(255, 180,   0),  #TUM Yellow    
(255, 128,   0),  #TUM Orange   
(229, 52, 24),  #TUM Red       
(202, 33, 63)  #TUM Dark Red    
]

offsets = [.0, .35, .5,  .75, .85, .95, 1.0]

tum_colors = [( offsets[ci], (col[0]/255.0, col[1]/255.0, col[2]/255.0)) for ci, col in enumerate(tum_raw)]

tum_jet = pylab.matplotlib.colors.LinearSegmentedColormap.from_list("tum_jet", tum_colors)

# xs = numpy.linspace(-1,1,101)

# xs, ys = pylab.meshgrid(xs,xs)

# fig=pylab.figure()
# fig.add_subplot(211)
# pylab.imshow(numpy.exp(-(xs*xs + ys*ys)/200.0))
# fig.add_subplot(212)
# pylab.imshow(numpy.exp(-(xs*xs + ys*ys)/200.0), cmap=tum_jet)
# pylab.show()

# fig=pylab.figure()
# fig.add_subplot(211)
# pylab.imshow(xs, aspect=.3)
# fig.add_subplot(212)
# pylab.imshow(xs, cmap=tum_jet, aspect=.3)
# pylab.show()


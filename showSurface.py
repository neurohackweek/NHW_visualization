import os
import matplotlib.pyplot as plt
import nibabel as nb
import ipyvolume
import ipyvolume.pylab as p3
import numpy as np

def showSurface(surface,overlay=None,frame=0,newfigure=True,colormap='summer',figsize=np.array([600,600]),
                figlims=np.array([[-100,100],[-100,100],[-100,100]])):
    '''
    Displays a surface mesh in gifti or FreeSurfer (FS) surface format with/without an overlay inside
    Jupyter notebook for interactive visualization.

    Parameters
    ----------
    surface: str, gifti opject
        Path to surface file in gifti or FS surface format or an already loaded gifti object of surface
    overlay: str, gifti opject
        Path to overlay file in gifti or FS annot or anaotimcal (.curv,.sulc,.thickness) format or an already loaded
        gifti object of overlay, default None
    frame: int
        indice of the frame (timepoint or functional data frame) to show
    newfigure: bool
        Create a new figure else prints into the last figure (in order to visualize both hemispheres in
        one plot), default True
    colormap: string
        A matplotlib colormap, default summer
    figsize: ndarray
        Size of the figure to display, default [600,600]
    figLims: ndarray
        x,y and z limits of the axes, default [[-100,100],[-100,100],[-100,100]])

    '''

    if isinstance(surface,str):
        if not os.path.exists(surface):
            error('File does not exist, please provide a valid file path to a gifti or FreeSurfer file.')
        filename, file_extension = os.path.splitext(surface)
        if file_extension is '.gii':
            surface = nb.load(surface)
        else:
            fsgeometry = nb.freesurfer.read_geometry(surface)
            x,y,z = fsgeometry[0].T
            vertex_edges=fsgeometry[1]

    if isinstance(surface,nb.gifti.gifti.GiftiImage):
        try:
            vertex_spatial=surface.darrays[0]
            vertex_edges=surface.darrays[1]
            x, y, z = vertex_spatial.data.T
        except:
            raise ValueError('Please provide a valid gifti file.')

    if not isinstance(frame,int):
        ValueError('Please provide a valid integer frame index.')

    if isinstance(overlay,list):
        if frame>len(overlay) or frame < 0:
            error('Frame index out of bounds, please provide a valid frame index.')
        overlay = overlay[frame]

    if isinstance(overlay,str):
        if not os.path.exists(overlay):
            error('File does not exist, please provide a valid file path to a gifti or FreeSurfer file.')
        filename, file_extension = os.path.splitext(overlay)

        if file_extension is '.gii':
            overlay = nb.load(overlay)
        elif (file_extension in ('.annot','')):
            annot = nb.freesurfer.read_annot(overlay)
            activation = annot[0]
        elif (file_extension in ('.curv','.thickness','.sulc')):
            activation = nb.freesurfer.read_morph_data(overlay)

    if isinstance(overlay,nb.gifti.gifti.GiftiImage):
        try:
            activation=overlay.darrays[0].data
        except:
            raise ValueError('Please provide a valid gifti file')


    if newfigure:

        fig = p3.figure(width=figsize[0], height=figsize[1])
        fig.camera_fov = 1
        fig.style = {'axes': {'color': 'black',
          'label': {'color': 'black'},
          'ticklabel': {'color': 'black'},
          'visible': False},
         'background-color': 'white',
         'box': {'visible': False}}
        fig.xlim = (figlims[0][0], figlims[0][1])
        fig.ylim = (figlims[1][0], figlims[1][1])
        fig.zlim = (figlims[2][0], figlims[2][1])


    # plot surface
    if overlay is None:
        p3.plot_trisurf(x, y, z, triangles=vertex_edges.data)
    else:
        my_color = plt.cm.get_cmap(colormap)
        colors=my_color((activation-min(activation))/(max(activation)-min(activation)))
        p3.plot_trisurf(x, y, z, triangles=vertex_edges.data, color=colors[:,:3])

    if newfigure:
        p3.show()

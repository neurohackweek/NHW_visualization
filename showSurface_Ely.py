from __future__ import print_function
import os, sys, time
import numpy as np
import nibabel as nb
import matplotlib.pyplot as plt
import ipyvolume
import ipyvolume.pylab as p3

def showSurface(surface,overlay=None,frame=0,newfigure=True,colormap='summer',figsize=np.array([600,600]),
                figlims=np.array([[-100,100],[-100,100],[-100,100]]),showZeroes=True):
    '''
    Displays a surface mesh in gifti or FreeSurfer (FS) surface format with/without an overlay inside  
    Jupyter notebook for interactive visualization.

    Parameters
    ----------
    surface: str, gifti object
        Path to surface file in gifti or FS surface format or an already loaded gifti object of surface
    overlay: str, gifti object
        Path to overlay file in gifti or FS annot or anaotimcal (.curv,.sulc,.thickness) format or an already loaded 
        gifti object of overlay, default None
    frame: int
        index of the frame (timepoint or functional data frame) to show
    newfigure: bool
        Create a new figure else prints into the last figure (in order to visualize both hemispheres in 
        one plot), default True
    colormap: string
        A matplotlib colormap, default summer
    figsize: ndarray
        Size of the figure to display, default [600,600]
    figLims: ndarray
        x,y and z limits of the axes, default [[-100,100],[-100,100],[-100,100]])
    showZeroes: bool
        Display vertices with intensity = 0, default True

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
        raise ValueError('Please provide a valid integer frame index.')
    
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
            
    if showZeroes is False:
        try:
            mkeep,mkill=zmask(surface,overlay)
        except:
            raise ValueError('Overlay required for medial wall masking.')
    
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
    elif showZeroes is False:
        my_color = plt.cm.get_cmap(colormap)
        colors=my_color(oscale(activation))
        p3.plot_trisurf(x, y, z, triangles=vertex_edges.data[mkeep], color=colors[:,:3])
    else:
        my_color = plt.cm.get_cmap(colormap)
        colors=my_color(oscale(activation))
        p3.plot_trisurf(x, y, z, triangles=vertex_edges.data, color=colors[:,:3])

    if newfigure:
        p3.show()
        
    return 1

def zmask(surf,mask):
    '''
    Masks out vertices with intensity=0 from overlay. Also returns masked-out vertices.
    
    Parameters
    ----------
    surf: gifti object
        already loaded gifti object of target surface
    mask: gifti object
        already loaded gifti object of overlay with zeroes at vertices of no interest (e.g. medial wall)
    '''
    keep=(mask.darrays[0].data!=0) # nonzero values of mask
    kill=(mask.darrays[0].data==0) # zero values of mask
    ikeep=[i for i, e in enumerate(keep) if e != 0] # indices of nonzero mask values
    ikill=[i for i, e in enumerate(kill) if e != 0] # indices of zero mask values
    killdict={ii:1 for ii in ikill} # fun fact, iterating over a dictionary is ~exponentially faster vs. over a list
    mask_kill=np.zeros([surf.darrays[1].data.shape[0]],dtype=bool) # create empty arrays matching surface mesh dimentions
    mask_keep=mask_kill.copy()
    for ii, row in enumerate(surf.darrays[1].data):
        for item in row:
            if item in killdict.keys():
                mask_kill[ii]=True
                continue
            else:
                mask_keep[ii]=True
                continue
    return mask_keep, mask_kill

def mwpad(overlay,template,frame=0):
    '''
    Adds intensity=0 vertices along medial wall of overlay

    Parameters
    ----------
    overlay: gifti object
        gifti object overlay to be padded (e.g. hemisphere data array from a cifti file)
    template: gifti object
        gifti object with zeroes at medial wall vertices, otherwise matched to overlay (e.g. myelin map)
    frame: int
        index of the timepoint to show, default 0, ignored if overlay only has one timepoint
    '''
    padolay=nb.gifti.gifti.GiftiImage()
    padded=np.zeros(template.darrays[0].data.shape[0])
    count=0        
    for i, x in enumerate(template.darrays[0].data):
        if x!=0:
            if overlay.darrays[0].data.ndim > 1:
                padded[i]=overlay.darrays[0].data[frame,count]
            else:
                padded[i]=overlay.darrays[0].data[count]
            count=count+1
    padarray=nb.gifti.gifti.GiftiDataArray(padded)
    padolay.add_gifti_data_array(padarray)
    return padolay

def oscale(overlay):
    '''
    Scales input array values to between zero and one, as needed for iPyVolume colormaps.
    For now, olay must be a 1D array (single timepoint).
    
    Parameters
    ----------
    overlay: gifti object
        gifti object overlay to be scaled (e.g. myelin map)
    '''
    scaled=np.asarray((overlay-min(overlay))/(max(overlay)-min(overlay)))
    return scaled



# coding: utf-8

# # Interactive longitudinal volumetric data visualization using `niwidgets`

# ## Basic `niwidgets` functionality using 3D volumes

# In[ ]:

import os
from niwidgets import NiftiWidget
import nilearn.plotting as nip
from ipywidgets import interact, fixed, IntSlider, FloatSlider
from nilearn import image
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np

get_ipython().magic('matplotlib inline')

nhw = os.environ['NHW']

filename = os.path.join(nhw,'data','subjA','subjA_t0_pet_mni.nii.gz')
filename_4D = os.path.join(nhw,'data','subjA','subjA_4D_pet_mni.nii.gz')


# Here's the default niwidget:

# In[2]:

my_widget = NiftiWidget(filename)
my_widget.nifti_plotter()


# It is possible to specify your own plotting function rather than use the default plotter in niwidgets. All the arguments following the `plotting_func` variable are passed onto the plotting function as interactive parameters (unless you put the variable inside `ipywidgets`'  `fixed()` function). `colormap` or `cmap` is always passed as an interactive parameter, with colormap options being obtained from matplotlib within niwidgets.

# In[3]:

my_widget.nifti_plotter(plotting_func=nip.plot_glass_brain, 
                        threshold=1., 
                        display_mode=fixed("lyrz"))


# ## Extending `niwidgets` functionality to 4D images

# The idea is to write a function to plot a single 3D volume from a 4D volume. This function needs to take as input the index along the 4th dimension to be plotted. We can then use niwidgets with our custom plotting function and specify the index along 4th dimension as an interactive parameter.
# 
# Below is a function to plot a given time point on the glass brain from a 4D volume:

# In[4]:

def plot_glass_brain_4D_timepoint(filename_4D, t=0, **kwargs):
    iterator = image.iter_img(filename_4D)
    nip.plot_glass_brain(next(islice(iterator, t, t+1)), **kwargs)


# In[5]:

plot_glass_brain_4D_timepoint(filename_4D, 0, colorbar=True)


# In[6]:

plot_glass_brain_4D_timepoint(filename_4D, 1, colorbar=True)


# Now we use this function within `niwidgets` plotter. We need to pre-specify the allowed range for the 4th dimension index -- otherwise the plotter crashes if the interactive index is set outside the allowed range.

# In[7]:

# how to set the max for the t IntSlider?
# Keep colorbar the same across t
# Crashes kind of easily
# very slow

my_4D_widget = NiftiWidget(filename_4D)
my_4D_widget.nifti_plotter(plotting_func=plot_glass_brain_4D_timepoint, 
                           t=IntSlider(min=0,max=3), 
                           threshold=FloatSlider(min=0,max=3,step=0.1,continuous_update=False),
                           display_mode=fixed("lyrz"),
                           colorbar=fixed(True))


# Below is a modified version of the `_plot_slices` function in `niwidgets` to handle 4D data.

# In[8]:

# 1) get the default plotter in niwidgets and manipulate it.
# 2) write function for an spaghetti plot showing the longitudinal trend at selected voxel

def plot_timepoint_slices(data, figure, x, y, z, t=0, colormap='viridis', figsize=(15, 5)):
    """
    Plots x,y,z slices at time point t.
    """
    
    coords = [x, y, z]
    views = ['Sagittal', 'Coronal', 'Axial']
    
    axes = [figure.add_subplot(231), figure.add_subplot(232), figure.add_subplot(233),
            figure.add_subplot(234)]
    
    
    data = data.dataobj.get_unscaled()
    print(data.shape)
    for subplot in range(3):
        slice_obj = 3 * [slice(None)] + [t]
        slice_obj[subplot] = coords[subplot]

        plt.sca(axes[subplot])
        axes[subplot].set_facecolor('black')
        axes[subplot].set_title(views[subplot])
        axes[subplot].tick_params(
            axis='both', which='both', bottom='off', top='off',
            labelbottom='off', right='off', left='off', labelleft='off'
            )
        # fix the axis limits
        axis_limits = [limit for i, limit in enumerate(data.shape)
                       if i != subplot]
        axes[subplot].set_xlim(0, axis_limits[0])
        axes[subplot].set_ylim(0, axis_limits[1])

        # plot the actual slice
        if subplot == 0:
            plt.imshow(np.flipud(np.rot90(data[slice_obj], k=1)),
                       cmap=colormap)
        else:
            plt.imshow(np.rot90(data[slice_obj], k=3), cmap=colormap)
        # draw guides to show where the other two slices are
        guide_positions = [val for i, val in enumerate(coords)
                           if i != subplot]
        plt.axvline(x=guide_positions[0], color='gray', alpha=0.8)
        plt.axhline(y=guide_positions[1], color='gray', alpha=0.8)

    #plt.sca(axes[-1])
    axes[-1].plot(range(data.shape[3]),data[x,y,z,:],'o-')
    axes[-1].plot(t,data[x,y,z,t],'ro')
    axes[-1].set_xlabel('Time point')
    axes[-1].set_ylabel('Intensity')
    
    # show the plot
    plt.show()
    # print the value at that point in case people need to know
    print('Value at point {x}, {y}, {z}, {t}: {intensity}'.format(
        x=x, y=y, z=z, t=t, intensity=data[x, y, z, t]
    ))


# In[9]:

my_4D_widget = NiftiWidget(filename_4D)
my_4D_widget.nifti_plotter(plotting_func=plot_timepoint_slices, 
                           x=IntSlider(90, min=0, max=181, continuous_update=False),
                           y=IntSlider(100, min=0, max=217),
                           z=IntSlider(90, min=0, max=181),
                           t=IntSlider(min=0, max=3))

# there is a problem here with figures begin regenerated(?)..
# colormap options are not working either


# In[ ]:




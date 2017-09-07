
# coding: utf-8

# In[11]:

from niwidgets import NiftiWidget
get_ipython().magic('matplotlib inline')

filename = './data/subjA/subjA_t0_pet_mni.nii.gz'
my_widget = NiftiWidget(filename)


# In[12]:

my_widget.nifti_plotter()


# In[13]:

import nilearn.plotting as nip
from ipywidgets import interact, fixed
my_widget.nifti_plotter(plotting_func=nip.plot_glass_brain, 
                        threshold=1., 
                        display_mode=fixed("lyrz"))


# In[15]:

from nilearn import image

filename_4D = './data/subjA/subjA_4D_pet_mni.nii.gz'

iterator = image.iter_img(filename_4D)
for volume in image.iter_img(filename_4D):
    nip.plot_glass_brain(volume)


# In[16]:

from itertools import islice

def plot_glass_brain_4D_timepoint(filename_4D, t=0, **kwargs):
    iterator = image.iter_img(filename_4D)
    nip.plot_glass_brain(next(islice(iterator, t, t+1)), **kwargs)


# In[17]:

from ipywidgets import IntSlider, FloatSlider

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


# In[ ]:




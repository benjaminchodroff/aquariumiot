#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import sys
import numpy as numpy
from PIL import Image
import gc

from core import fig_to_img

# function for generating NDVI imagery from NGB or NBG input files
def photosynscore(img,
         vmin = -1.0,
         vmax = 1.0,
         output= None
        ):
    if isinstance(img,str): #treat as a filename
        img = Image.open(img)
    #create the matplotlib figure
    img_w,img_h=img.size
         
    imgR, imgB, imgG = img.split() #get channels
    del img
    #compute the NDVI
    arrR = numpy.asarray(imgR).astype('float64')
    arrG = numpy.asarray(imgG).astype('float64') #this channel is ignored
    arrB = numpy.asarray(imgB).astype('float64')
    num   = (arrR - arrB)
    denom = (arrR + arrB)
    del arrR
    del arrB
    del arrG
    with numpy.errstate(divide='ignore', invalid='ignore'):
        arr_ndvi = numpy.true_divide(num,denom)
        arr_ndvi[arr_ndvi == numpy.inf] = 0
        arr_ndvi = numpy.nan_to_num(arr_ndvi)
    if output!=None:
        # Needs to be floating point
        colormap = plt.cm.spectral #plt.cm.gist_gray
        dpi=600.0
        fig_w=img_w/dpi/8
        fig_h=img_h/dpi/8
        fig=plt.figure(figsize=(fig_w,fig_h),dpi=dpi)
        fig.set_frameon(False)

        ax_rect = [0.0, #left
               0.0, #bottom
               1.0, #width
               1.0] #height
        ax = fig.add_axes(ax_rect)
        ax.yaxis.set_ticklabels([])
        ax.xaxis.set_ticklabels([])
        ax.set_axis_off()
        ax.axes.get_yaxis().set_visible(False)
        ax.patch.set_alpha(0.0)
        axes_img = ax.imshow(arr_ndvi,
                         cmap=colormap,
                         vmin = vmin,
                         vmax = vmax,
                         aspect = 'equal',
                         interpolation="nearest"
                        )  
        del axes_img
        fig.savefig(output,
                dpi=dpi,
                bbox_inches='tight',
                pad_inches=0.0,
                )
        del fig
 
    threshold = arr_ndvi[ numpy.where(arr_ndvi>=vmin) ]
    del arr_ndvi
    normalized = numpy.multiply(numpy.add(threshold,1.0),1/2.0)
    del threshold
    print numpy.median(normalized)*100.0
    gc.collect()


###### testing the code #######
if __name__ == "__main__":
    if len(sys.argv)<1:
        print "python photosynscore.py input.png [output.png]"
        sys.exit(1)
    output=None
    if len(sys.argv)==3:
        output=sys.argv[2]
    photosynscore(sys.argv[1],vmin=-0.75,output=output)

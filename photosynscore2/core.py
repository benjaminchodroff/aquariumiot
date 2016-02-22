import numpy
from PIL import Image

def fig_to_data(fig):
    """
    @brief  Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param  fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    
    note: this code was orginally taken from http://www.icare.univ-lille1.fr/wiki/index.php/How_to_convert_a_matplotlib_figure_to_a_numpy_array_or_a_PIL_image
    """
    # draw the renderer
    fig.canvas.draw()
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = numpy.fromstring(fig.canvas.tostring_argb(), dtype=numpy.uint8)
    buf.shape = (w,h,4)
 
    # canvas.tostring_argb gives pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = numpy.roll(buf, 3, axis = 2)
    return buf
    
def fig_to_img(fig):
    """
    @brief  Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param  fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    
    note: this code was orginally taken from http://www.icare.univ-lille1.fr/wiki/index.php/How_to_convert_a_matplotlib_figure_to_a_numpy_array_or_a_PIL_image
    """
    # put the figure pixmap into a numpy array
    buf = fig_to_data(fig)
    w, h, d = buf.shape
    return Image.fromstring("RGBA", ( w ,h ), buf.tostring())

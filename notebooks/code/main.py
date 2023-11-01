import os
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import matplotlib.pyplot as plt
import numpy as np

from code.hdf5_handler import Hdf5Handler

INTERPOLATION_METHODS = ['none', 'nearest', 'bilinear', 'bicubic', 'spline16',
                         'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
                         'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']
DEFAULT_INTERPOLATION = 'none'

CMAPS = ['viridis', 'jet']
DEFAULT_CMAPS = 'viridis'

DEFAULT_DATA_TYPE = 'lambda'
NBR_POINTS_IN_SCALE = 100


class Main:

    hdf5_filename = None

    integrated_normalized_radiographs = None
    metadata = None

    strain_mapping = None
    d = None
    lambda_hkl = None

    nbr_row = 0
    nbr_column = 0

    strain_mapping_2d = None
    d_2d = None
    lambda_hkl_2d = None

    cb0 = None
    cb1 = None
    cb2 = None

    def __init__(self, working_dir=''):
        self.working_dir = working_dir

    def load(self, filename):
        self.hdf5_filename = filename
        self.import_hdf5()
        display(HTML('<span style="font-size: 20px; color:blue">' + str(os.path.basename(filename)) + ' '
                                                                                                  'has been loaded !</span>'))

    def import_hdf5(self):
        o_import = Hdf5Handler(parent=self)
        o_import.load(filename=self.hdf5_filename)

    def process_data(self):
        # format the data to be able to display them

        [height, width] = np.shape(self.integrated_normalized_radiographs)
        self.image_height = height
        self.image_width = width

        lambda_2d = np.empty((height, width))
        lambda_2d[:] = np.nan
        compact_lambda_2d = np.empty((self.nbr_row, self.nbr_column))

        strain_mapping_2d = np.empty((height, width))
        strain_mapping_2d[:] = np.nan
        compact_strain_mapping = np.empty((self.nbr_row, self.nbr_column))

        d_2d = np.empty((height, width))
        d_2d[:] = np.nan

        top_left_corner_of_roi = [self.image_height, self.image_width]

        for _key in self.bin.keys():
            x0 = self.bin[_key]['x0']
            y0 = self.bin[_key]['y0']
            x1 = self.bin[_key]['x1']
            y1 = self.bin[_key]['y1']
            row_index = self.bin[_key]['row_index']
            column_index = self.bin[_key]['column_index']

            if x0 < top_left_corner_of_roi[1]:
                top_left_corner_of_roi[1] = x0

            if y0 < top_left_corner_of_roi[0]:
                top_left_corner_of_roi[0] = y0

            compact_lambda_2d[row_index, column_index] = self.lambda_hkl[_key]

            lambda_2d[y0: y1, x0: x1] = self.lambda_hkl[_key]
            strain_mapping_2d[y0: y1, x0: x1] = self.strain_mapping[_key]['val']  # to go to microstrain
            compact_strain_mapping[row_index, column_index] = self.strain_mapping[_key]['val']

            d_2d[y0: y1, x0: x1] = self.d[_key]

        self.compact_lambda_2d = compact_lambda_2d
        self.compact_strain_mapping = compact_strain_mapping
        self.top_left_corner_of_roi = top_left_corner_of_roi

        self.lambda_hkl_2d = lambda_2d
        self.strain_2d = strain_mapping_2d
        self.d_2d = d_2d

    def display(self):
        self.display_data()

    def display_data(self):

        fig = plt.figure(figsize=(4, 4), num=u"\u03BB (\u212B)")

        self.ax0 = fig.add_subplot(111)
        self.ax0.imshow(self.integrated_normalized_radiographs,
                                   vmin=0,
                                   vmax=1,
                                   cmap='gray')

        self.im0 = self.ax0.imshow(self.lambda_hkl_2d, cmap='jet', alpha=0.5)
        self.cb0 = plt.colorbar(self.im0, ax=self.ax0)
        self.ax0.set_title(u"\u03BB (\u212B)")

        plt.tight_layout()

        def plot_lambda(data_type, colormap, interpolation_method):

            if self.cb0:
                self.cb0.remove()

            if data_type == 'd':
                data = self.d_2d
            elif data_type == 'lambda':
                data = self.lambda_hkl_2d
            else:
                data = self.strain_2d

            self.ax0.cla()

            self.ax0.imshow(self.integrated_normalized_radiographs,
                            vmin=0,
                            vmax=1,
                            cmap='gray')
            self.im0 = self.ax0.imshow(data,
                                       interpolation=interpolation_method,
                                       cmap=colormap)
            self.cb0 = plt.colorbar(self.im0, ax=self.ax0)

        v = interactive(plot_lambda,
                        data_type=widgets.Dropdown(options=['d', 'strain', 'lambda']),
                        colormap=widgets.Dropdown(options=CMAPS,
                                                  value=DEFAULT_CMAPS,
                                                  layout=widgets.Layout(width="300px")),
                        interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
                                                              value=DEFAULT_INTERPOLATION,
                                                              description="Interpolation",
                                                              layout=widgets.Layout(width="300px")))
        display(v)

import os
from qtpy.QtWidgets import QMainWindow, QVBoxLayout
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.core.display import display, HTML
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
from matplotlib.transforms import Affine2D
from matplotlib.image import _resample

from . import load_ui
from .hdf5_handler import Hdf5Handler
from .mplcanvas import MplCanvasColorbar, MplCanvas

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
        compact_d_array = np.empty((self.nbr_row, self.nbr_column))

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
            compact_d_array[row_index, column_index] = float(self.lambda_hkl[_key])/2.

            lambda_2d[y0: y1, x0: x1] = self.lambda_hkl[_key]
            strain_mapping_2d[y0: y1, x0: x1] = self.strain_mapping[_key]['val']  # to go to microstrain
            compact_strain_mapping[row_index, column_index] = self.strain_mapping[_key]['val']

            d_2d[y0: y1, x0: x1] = self.d[_key]

        self.compact_lambda_2d = compact_lambda_2d
        self.compact_d_array = compact_d_array
        self.compact_strain_mapping = compact_strain_mapping
        self.top_left_corner_of_roi = top_left_corner_of_roi

        self.lambda_hkl_2d = lambda_2d
        self.strain_2d = strain_mapping_2d
        self.d_2d = d_2d

    # def display(self):
    #     self.display_data()
    #
    # def display_data(self):
    #
    #     fig = plt.figure(figsize=(4, 4), num=u"\u03BB (\u212B)")
    #
    #     self.ax0 = fig.add_subplot(111)
    #     self.ax0.imshow(self.integrated_normalized_radiographs,
    #                                vmin=0,
    #                                vmax=1,
    #                                cmap='gray')
    #
    #     self.im0 = self.ax0.imshow(self.lambda_hkl_2d, cmap='jet', alpha=0.5)
    #     self.cb0 = plt.colorbar(self.im0, ax=self.ax0)
    #     self.ax0.set_title(u"\u03BB (\u212B)")
    #
    #     plt.tight_layout()
    #
    #     def plot_lambda(data_type, colormap, interpolation_method):
    #
    #         if self.cb0:
    #             self.cb0.remove()
    #
    #         if data_type == 'd':
    #             data = self.d_2d
    #         elif data_type == 'lambda':
    #             data = self.lambda_hkl_2d
    #         else:
    #             data = self.strain_2d
    #
    #         self.ax0.cla()
    #
    #         self.ax0.imshow(self.integrated_normalized_radiographs,
    #                         vmin=0,
    #                         vmax=1,
    #                         cmap='gray')
    #         self.im0 = self.ax0.imshow(data,
    #                                    interpolation=interpolation_method,
    #                                    cmap=colormap)
    #         self.cb0 = plt.colorbar(self.im0, ax=self.ax0)
    #
    #     v = interactive(plot_lambda,
    #                     data_type=widgets.Dropdown(options=['d', 'strain', 'lambda']),
    #                     colormap=widgets.Dropdown(options=CMAPS,
    #                                               value=DEFAULT_CMAPS,
    #                                               layout=widgets.Layout(width="300px")),
    #                     interpolation_method=widgets.Dropdown(options=INTERPOLATION_METHODS,
    #                                                           value=DEFAULT_INTERPOLATION,
    #                                                           description="Interpolation",
    #                                                           layout=widgets.Layout(width="300px")))
    #     display(v)


class Interface(QMainWindow):

    o_strain = None
    colorbar = None

    def __init__(self, parent=None, o_strain=None):

        super(QMainWindow, self).__init__(parent)
        ui_full_path = os.path.join(os.path.dirname(__file__), "ui/ui_main_interface.ui")
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.o_strain = o_strain

        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=2, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.ui.label.setText(f"Matplotlib version {matplotlib.__version__}")

        self.ui.matplotlib_plot = _matplotlib(parent=self,
                                              widget=self.ui.widget)

        self.ui.matplotlib_interpolation_plot = _matplotlib(parent=self,
                                                            widget=self.ui.widget_2)

        self.ui.interpolation_comboBox.addItems(INTERPOLATION_METHODS)

    def _parameter_to_display(self):
        return self.ui.data_comboBox.currentText()

    def _colormap_to_use(self):
        return self.ui.colorbar_comboBox.currentText()

    def _interpolation_to_use(self):
        return self.ui.interpolation_comboBox.currentText()

    def combobox_changed(self, _):
        parameter = self._parameter_to_display()

        if parameter == 'd':
            self.d_array()
        else:
            self.strain_mapping()

    def d_array(self):
        d_array = self.o_strain.compact_d_array
        max_value = np.nanmax(d_array)
        d_array = d_array / max_value

        self.display_array(data_array=d_array,
                           post_correction_coefficient=max_value)

    def strain_mapping(self):
        strain_mapping_array = self.o_strain.compact_strain_mapping
        max_value = np.nanmax(strain_mapping_array)
        strain_mapping_array = strain_mapping_array / max_value

        self.display_array(data_array=strain_mapping_array,
                           post_correction_coefficient=1)

    def display_array(self, data_array=None, post_correction_coefficient=1):
        cmap = self._colormap_to_use()
        interpolation = self._interpolation_to_use()

        integrated_image = self.o_strain.integrated_normalized_radiographs
        scale_factor = self.o_strain.bin_size
        out_dimensions = (data_array.shape[0] * scale_factor,
                          data_array.shape[1] * scale_factor)
        transform = Affine2D().scale(scale_factor, scale_factor)

        self.ui.matplotlib_plot.axes.cla()
        img = self.ui.matplotlib_interpolation_plot.axes.imshow(data_array,
                                                                cmap=cmap,
                                                                interpolation=interpolation)
        self.ui.matplotlib_interpolation_plot.draw()

        interpolated = _resample(img, data_array, out_dimensions, transform=transform)

        self.ui.matplotlib_interpolation_plot.axes.cla()
        self.ui.matplotlib_interpolation_plot.axes.imshow(interpolated, cmap=cmap)
        self.ui.matplotlib_interpolation_plot.draw()

        interpolated *= post_correction_coefficient

        # with overlap
        interpolated_d_array_2d = np.empty((self.o_strain.image_height,
                                            self.o_strain.image_width))
        interpolated_d_array_2d[:] = np.nan

        [y0, x0] = self.o_strain.top_left_corner_of_roi
        inter_height, inter_width = np.shape(interpolated)
        interpolated_d_array_2d[y0: y0 + inter_height, x0: x0 + inter_width] = interpolated

        self.ui.matplotlib_plot.axes.cla()
        self.ui.matplotlib_plot.axes.imshow(integrated_image, cmap='gray', vmin=0, vmax=1)
        self.ui.matplotlib_plot.draw()

        im = self.ui.matplotlib_plot.axes.imshow(interpolated_d_array_2d,
                                                 interpolation=interpolation,
                                                 cmap=cmap,
                                                 alpha=0.5)
        if self.colorbar:
            self.colorbar.remove()

        self.colorbar = self.ui.matplotlib_plot.fig.colorbar(im,
                                                             ax=self.ui.matplotlib_plot.axes)
        self.ui.matplotlib_plot.draw()

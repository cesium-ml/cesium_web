import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import plotly
import plotly.offline as py
from plotly.tools import FigureFactory as FF

from cesium import featurize
from .config import cfg

# Testing bokeh
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components, file_html
from bokeh.io import curdoc
from bokeh.resources import CDN
from bokeh.document import Document

from .json_util import to_json


def feature_scatterplot(fset_path, features_to_plot):
    """Create scatter plot of feature set.

    Parameters
    ----------
    fset_path : str
        Path to feature set to be plotted.
    features_to_plot : list of str
        List of feature names to be plotted.

    Returns
    -------
    (fig.data, fig.layout)
        Returns (fig.data, fig.layout) where `fig` is an instance of
        `plotly.tools.FigureFactory`.
    """
    # fset, data = featurize.load_featureset(fset_path)
    # fset = fset[features_to_plot]
    #
    # if 'label' in data:
    #     fset['label'] = data['label']
    #     index = 'label'
    # else:
    #     index = None
    #
    # # TODO replace 'trace {i}' with class labels
    # fig = FF.create_scatterplotmatrix(fset, diag='box', index=index,
    #                                   height=800, width=800)
    #
    # py.plot(fig, auto_open=False, output_type='div')
    #
    #
    # return fig.data, fig.layout

    # Try to return a Bokeh plot first

    # create some data
    x1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y1 = [0, 8, 2, 4, 6, 9, 5, 6, 25, 28, 4, 7]
    x2 = [2, 5, 7, 15, 18, 19, 25, 28, 9, 10, 4]
    y2 = [2, 4, 6, 9, 15, 18, 0, 8, 2, 25, 28]
    x3 = [0, 1, 0, 8, 2, 4, 6, 9, 7, 8, 9]
    y3 = [0, 8, 4, 6, 9, 15, 18, 19, 19, 25, 28]

    # select the tools we want
    TOOLS="pan,wheel_zoom,box_zoom,reset,save"

    # the red and blue graphs will share this data range
    xr1 = Range1d(start=0, end=30)
    yr1 = Range1d(start=0, end=30)

    # only the green will use this data range
    xr2 = Range1d(start=0, end=30)
    yr2 = Range1d(start=0, end=30)

    # build our figures
    p1 = figure(x_range=xr1, y_range=yr1, tools=TOOLS, plot_width=300, plot_height=300)
    p1.scatter(x1, y1, size=12, color="red", alpha=0.5)

    js, div = components(p1, wrap_script=False)

    return js, div


#def prediction_heatmap(pred_path):
#    with xr.open_dataset(pred_path) as pset:
#        pred_df = pd.DataFrame(pset.prediction.values, index=pset.name,
#                               columns=pset.class_label.values)
#    pred_labels = pred_df.idxmax(axis=1)
#    C = confusion_matrix(pset.label, pred_labels)
#    row_sums = C.sum(axis=1)
#    C = C / row_sums[:, np.newaxis]
#    fig = FF.create_annotated_heatmap(C, x=[str(el) for el in
#                                            pset.class_label.values],
#                                      y=[str(el) for el in
#                                         pset.class_label.values],
#                                      colorscale='Viridis')
#
#    py.plot(fig, auto_open=False, output_type='div')
#
#    return fig.data, fig.layout

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import xarray as xr
import plotly
import plotly.offline as py
from plotly.tools import FigureFactory as FF

from cesium import build_model
from .config import cfg


def feature_scatterplot(fset_path, features_to_plot):
    with xr.open_dataset(fset_path, engine=cfg['xr_engine']) as fset:
        fset_data = fset.load()
        feat_df = build_model.rectangularize_featureset(fset_data)

        feat_df = feat_df[features_to_plot]

        if 'target' in fset_data:
            feat_df['target'] = fset_data.target.values
            index = 'target'
        else:
            index = None

    # TODO replace 'trace {i}' with class labels
    fig = FF.create_scatterplotmatrix(feat_df, diag='box', index=index,
                                      height=800, width=800)

    py.plot(fig, auto_open=False, output_type='div')

    return fig.data, fig.layout


#def prediction_heatmap(pred_path):
#    with xr.open_dataset(pred_path, engine=cfg['xr_engine']) as pset:
#        pred_df = pd.DataFrame(pset.prediction.values, index=pset.name,
#                               columns=pset.class_label.values)
#    pred_labels = pred_df.idxmax(axis=1)
#    C = confusion_matrix(pset.target, pred_labels)
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

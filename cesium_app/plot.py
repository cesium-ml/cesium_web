from itertools import cycle, islice
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.palettes import PuBu as palette
from cesium import featurize
from .config import cfg

# Testing bokeh
from bokeh.plotting import figure
from bokeh.embed import components, file_html, _standalone_docs_json_and_render_items, _ModelInDocument
from bokeh.core.json_encoder import serialize_json


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
    (str, str)
        Returns (script, div) tags for the desired plot as output by
        `bokeh.embed.components`.
    """
    fset, data = featurize.load_featureset(fset_path)
    X = fset[features_to_plot]
    if 'target' in fset and fset.target.values.dtype != np.float:
        y = fset.target.values
        labels = np.unique(y)
    else:
        y = [None] * len(X)
        labels = [None]

    if len(labels) in palette:
        colors = palette[len(labels)]
    else:
        all_colors = sorted(palette.items(), key=lambda x: x[0],
                            reverse=True)[0][1]
        colors = list(islice(cycle(all_colors), len(labels)))

    plots = np.array([[figure(width=300, height=200)
                       for j in range(len(features_to_plot))]
                      for i in range(len(features_to_plot))])
    for (i, j), p in np.ndenumerate(plots):
        for l, c in zip(labels, colors):
            if l is not None:
                inds = np.where(y == l)[0]
            else:
                inds = np.arange(len(X))
            p.circle(X.values[inds, i], X.values[inds, j], color=c,
                     legend=(l if (i == j and l is not None) else None))
            p.legend.location = 'bottom_right'
            p.legend.label_text_font_size = '6pt'
            p.legend.spacing = 0
            p.legend.padding = 0
            p.xaxis.axis_label = features_to_plot[i]
            p.yaxis.axis_label = features_to_plot[j]

    plot = gridplot(plots.tolist(), ncol=len(features_to_plot), mergetools=True)

    with _ModelInDocument(plot):
        (docs_json, render_items) = _standalone_docs_json_and_render_items(plot)

    docs_json = serialize_json(docs_json)
    render_items = serialize_json(render_items)

    return docs_json, render_items

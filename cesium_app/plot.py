from itertools import cycle, islice
import numpy as np
from cesium import featurize
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.palettes import PuBu as palette
from bokeh.core.json_encoder import serialize_json
from bokeh.document import Document
from bokeh.util.serialization import make_id


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

    # Convert plot to json objects necessary for rendering with bokeh on the
    # frontend
    render_items = [{'docid': plot._id, 'elementid': make_id()}]

    doc = Document()
    doc.add_root(plot)
    docs_json_inner = doc.to_json()
    docs_json = {render_items[0]['docid']: docs_json_inner}

    docs_json = serialize_json(docs_json)
    render_items = serialize_json(render_items)

    return docs_json, render_items

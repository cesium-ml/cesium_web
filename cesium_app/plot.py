from itertools import cycle
import numpy as np
from cesium import featurize
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.palettes import Viridis as palette
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
        Returns (docs_json, render_items) json for the desired plot.
    """
    fset, data = featurize.load_featureset(fset_path)
    fset = fset[features_to_plot]
    colors = cycle(palette[5])
    plots = np.array([[figure(width=300, height=200)
                       for j in range(len(features_to_plot))]
                      for i in range(len(features_to_plot))])

    for (j, i), p in np.ndenumerate(plots):
        if (j == i == 0):
            p.title.text = "Scatterplot matrix"
        p.circle(fset.values[:,i], fset.values[:,j], color=next(colors))
        p.xaxis.minor_tick_line_color = None
        p.yaxis.minor_tick_line_color = None
        p.ygrid[0].ticker.desired_num_ticks = 2
        p.xgrid[0].ticker.desired_num_ticks = 4
        p.outline_line_color = None
        p.axis.visible = None

    plot = gridplot(plots.tolist(), ncol=len(features_to_plot), mergetools=True, responsive=True, title="Test")

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

from itertools import cycle
import numpy as np
from cesium import featurize
from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.palettes import Viridis as palette
from bokeh.core.json_encoder import serialize_json
from bokeh.document import Document
from bokeh.util.serialization import make_id
from bokeh.models import Legend, Div
from bokeh.models.widgets import MultiSelect, Button
from bokeh.layouts import widgetbox, column


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
    plots = np.array([[figure(width=300, height=300)
                       for j in range(len(features_to_plot))]
                      for i in range(len(features_to_plot))])

    unique_labels = np.unique(data['labels'])
    fset_label = {}
    color = {}
    if unique_labels.size <= 0:
        fset_label[''] = fset
        color[''] = next(colors)
    else:
        for label in unique_labels:
            fset_label[label] = fset[data['labels'] == label]
            color[label] = next(colors)  # TODO make sure there are enough colors

    circles = []
    for (j, i), p in np.ndenumerate(plots):
        # Plot by label
        for label in unique_labels:
            if i == j == 0:
                c = p.circle(fset_label[label].values[:,i], fset_label[label].values[:,j], color=color[label])
                circles.append([c])
            else:
                p.circle(fset_label[label].values[:,i], fset_label[label].values[:,j], color=color[label])

        # Add legend
        if i == j == 0:
            items = list(zip(unique_labels, circles))
            vertical_offset = len(unique_labels) * 10
            legend = Legend(items=items, location=(vertical_offset, 0))
            p.add_layout(legend, 'above')
        if j == 0:
            # Compensate for legend height
            p.height = 300 + vertical_offset + 100

        # Graph styling
        p.xaxis.minor_tick_line_color = None
        p.yaxis.minor_tick_line_color = None
        p.ygrid[0].ticker.desired_num_ticks = 2
        p.xgrid[0].ticker.desired_num_ticks = 4
        p.outline_line_color = None
        p.axis.visible = None

        # Axis labels
        p.xaxis.axis_label = fset.columns[i][0]
        if i == 0:
            p.yaxis.axis_label = fset.columns[j][0]
        else:
            p.yaxis.axis_label = ' ' # Fixes a spacing issue

    plot = gridplot(plots.tolist(), ncol=len(features_to_plot), mergetools=True, responsive=True, toolbar_location='below')


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

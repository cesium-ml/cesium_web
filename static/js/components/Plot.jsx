import React, { Component } from 'react';
import { connect } from 'react-redux';
import { showNotification } from 'baselayer/components/Notifications';
/* eslint-disable */
import "../../../node_modules/bokehjs/build/js/bokeh.js";
import "../../../node_modules/bokehjs/build/css/bokeh.css";
/* eslint-enable */


function bokeh_render_plot(node, docs_json, render_items) {
  // Create bokeh div element
  const bokeh_div = document.createElement("div");
  const inner_div = document.createElement("div");
  bokeh_div.setAttribute("class", "bk-root");
  inner_div.setAttribute("class", "bk-plotdiv");
  inner_div.setAttribute("id", render_items[0].elementid);
  bokeh_div.appendChild(inner_div);
  node.appendChild(bokeh_div);

  // Generate plot
  /* eslint-disable */
  Bokeh.safely(() => {
    Bokeh.embed.embed_items(docs_json, render_items);
  });
  /* eslint-enable */
}

class Plot extends Component {
  constructor(props) {
    super(props);
    this.state = {
      plotData: null
    };
  }

  componentDidMount() {
    fetch(this.props.url, {
      credentials: 'same-origin'
    })
      .then(response => response.json())
      .then((json) => {
        if (json.status == 'success') {
          this.setState({ plotData: json.data });
        } else {
          console.log('dispatching error notification', json.message);
          this.props.dispatch(
            showNotification(json.message, 'error')
          );
        }
      });
  }

  render() {
    const { plotData } = this.state;
    if (!plotData) {
      return <b>Please wait while we load your plotting data...</b>;
    }
    const docs_json = JSON.parse(plotData.docs_json);
    const render_items = JSON.parse(plotData.render_items);

    return (
      plotData &&
        <div
          ref={
            (node) => {
              node && bokeh_render_plot(node, docs_json, render_items);
              }
            }
        />
    );
  }
}
Plot.propTypes = {
  url: React.PropTypes.string.isRequired,
  dispatch: React.PropTypes.func.isRequired
};

Plot = connect()(Plot);

export default Plot;

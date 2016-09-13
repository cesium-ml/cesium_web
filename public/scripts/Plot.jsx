import React, { Component } from 'react';
import { connect } from 'react-redux';
import Plotly from './custom-plotly';
import { showNotification } from './Notifications';


class Plot extends Component {
  constructor(props) {
    super(props);
    this.state = {
      plotData: null
    };
  }

  componentDidMount() {
    fetch(this.props.url)
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

    let { data, layout } = plotData;

    return (
      plotData &&
        <div
          ref={
            (node) => {
              node && Plotly.plot(node, data, layout);
            }}
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

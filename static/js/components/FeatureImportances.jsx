import React from 'react';
import PropTypes from 'prop-types';
import { HorizontalBar } from 'react-chartjs-2';


const FeatureImportancesBarchart = props => {
  const sorted_features = Object.keys(props.data).sort(
    (a, b) => props.data[b] - props.data[a]
  ).slice(0, 15);
  const values = sorted_features.map(feature => props.data[feature]);
  const data = {
    labels: sorted_features,
    datasets: [
      {
        label: 'Feature Importance',
        backgroundColor: '#2222ff',
        hoverBackgroundColor: '#5555ff',
        data: values
      }
    ]
  };
  const options = {
    scales: {
      xAxes: [{
        ticks: {
          min: 0.0
        }
      }]
    }
  };

  return (
    <div style={{ height: 300, width: 600 }}>
      <HorizontalBar data={data} options={options} />
    </div>
  );
};
FeatureImportancesBarchart.propTypes = {
  data: PropTypes.array.isRequired
};

export default FeatureImportancesBarchart;

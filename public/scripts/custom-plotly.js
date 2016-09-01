// in custom-plotly.js
import Plotly from 'plotly.js/lib/core';

// extra module, for example
import Choropleth from 'plotly.js/lib/choropleth';


// Load in the trace types for pie, and choropleth
Plotly.register([
  Choropleth
]);

export default Plotly;

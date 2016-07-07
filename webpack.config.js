var webpack = require('webpack');
var path = require('path');

var config = {
  entry: path.resolve(__dirname, 'public/scripts/main.js'),
  output: {
    path: path.resolve(__dirname, 'public/build'),
    filename: 'bundle.js'
  },
  module: {
    loaders: [
      { test: /\.js?$/,
        exclude: /node_modules/,
        loader: 'babel',
        query:
        {
          presets:['es2015', 'react', 'stage-2'],
          compact: false
        }
      },
      { test: /\.css$/, loader: 'style!css' },
      { test: /node_modules/, loader: 'ify'}
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      'fetch': 'imports?this=>global!exports?global.fetch!whatwg-fetch'
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
  ]
};

module.exports = config;

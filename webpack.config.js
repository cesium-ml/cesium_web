const webpack = require('webpack');
const path = require('path');

const config = {
  entry: path.resolve(__dirname, 'public/scripts/main.jsx'),
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
          presets: ['es2015', 'react', 'stage-2'],
          compact: false
        }
      },
      { test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel',
        query:
        {
          presets: ['es2015', 'react', 'stage-2'],
          compact: false
        }
      },
      { test: /\.css$/, loader: 'style!css' },
      { test: /node_modules/, loader: 'ify' }
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch'
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
  ],
  resolve: {
    extensions: ['', '.js', '.jsx']
  }
};

module.exports = config;

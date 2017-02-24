const webpack = require('webpack');
const path = require('path');

const config = {
  entry: path.resolve(__dirname, 'public/scripts/main.jsx'),
  output: {
    path: path.resolve(__dirname, 'public/build'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      { test: /\.js?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options:
        {
          presets: ['es2015', 'react', 'stage-2'],
          compact: false
        }
      },
      { test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options:
        {
          presets: ['es2015', 'react', 'stage-2'],
          compact: false
        }
      },
      { test: /\.css$/,
        use: [
          'style-loader',
          'css-loader'
        ]
      },
      { test: /node_modules/, loader: 'ify-loader' }
    ],
  },
  plugins: [
    new webpack.ProvidePlugin({
      fetch: 'imports-loader?this=>global!exports-loader?global.fetch!whatwg-fetch'
    }),

    // We do not use JQuery for anything in this project; but Bootstrap
    // depends on it
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    })
  ],
  resolve: {
    extensions: ['.js', '.jsx']
  }
};

module.exports = config;

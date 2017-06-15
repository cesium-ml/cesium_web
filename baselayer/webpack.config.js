const webpack = require('webpack');
const path = require('path');

const config = {
  entry: {
      // Add one entry per main HTML page
      exampleMainPage: './example_app/static/js/components/Main.jsx'
  }

  output: {
    path: path.resolve(__dirname, 'example_app/static/build'),
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
      }
    ],
  },

  plugins: [
    new webpack.ProvidePlugin({
      fetch: 'imports-loader?this=>global!exports-loader?global.fetch!whatwg-fetch'
    }),

    new webpack.optimize.CommonsChunkPlugin({
      // See: https://webpack.js.org/plugins/commons-chunk-plugin/
      name: "commons",
      filename: "commons.js",
    })
  ],

  resolve: {
    alias: {
      baselayer: path.resolve(__dirname, 'baselayer/static/js')
    },
    extensions: ['.js', '.jsx']
  }

};

module.exports = config;

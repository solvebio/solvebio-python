var path = require('path');
var webpack = require('webpack');

module.exports = {
  devtool: 'eval',
  entry: {
    'login': './src/login-index.react.js',
    'oauth-redirect': './src/oauth-redirect-index.react.js'
  },
  output: {
    path: path.join(__dirname, '..'),
    filename: '[name].js',
  },
  module: {
    loaders: [
      {
        test: /react\.jsx?$/,
        loaders: ['babel-loader'],
        include: path.join(__dirname, 'src')
      },
      {
        test: /\.scss$/,
        loaders: ["style-loader", "css-loader", "sass-loader"]
      }
    ]
  },
  plugins: [
    new webpack.ProvidePlugin({
      // 'Promise': 'es6-promise',
      // 'fetch': 'imports?this=>global!exports?global.fetch!whatwg-fetch'
      Promise:
        'imports-loader?this=>global!exports-loader?global.Promise!es6-promise',
      fetch:
        'imports-loader?this=>global!exports-loader?global.fetch!whatwg-fetch'
    })
  ]
}

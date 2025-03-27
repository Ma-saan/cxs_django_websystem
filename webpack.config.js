const path = require('path');

module.exports = {
  entry: './schedule_manager/static/src/index.js',
  output: {
    filename: 'main.js',
    path: path.resolve(__dirname, 'schedule_manager/static/build'),
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  }
};
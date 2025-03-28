const path = require('path');

module.exports = {
  entry: {
    main: './schedule_manager/static/src/index.js',
    'production_board': './schedule_manager/static/src/components/ProductionBoard.jsx',
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'schedule_manager/static/build'),
    library: {
      name: '[name]',
      type: 'var',
      export: 'default'
    },
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
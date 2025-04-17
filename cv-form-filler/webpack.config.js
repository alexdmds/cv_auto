const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    popup: './popup/popup.js',
    background: './scripts/background.js',
    content: './scripts/content.js'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js'
  },
  resolve: {
    extensions: ['.js']
  }
}; 
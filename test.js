var Vibrant = require('node-vibrant')
// ES6
// import * as Vibrant from 'node-vibrant'
// TypeScript
// import Vibrant = require('node-vibrant')

Vibrant.from('Web_Interaction/header (1).jpg').getPalette()
  .then((palette) => console.log(palette))

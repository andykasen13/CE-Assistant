var Vibrant = require('node-vibrant')
// ES6
// import * as Vibrant from 'node-vibrant'
// TypeScript
// import Vibrant = require('node-vibrant')

var vibrant = Vibrant.from('Web_Interaction/header (1).jpg').getPalette()
  .then((palette) => console.log(palette))

var hsl = vibrant.getHSL()
  , a = hsl[0]
  , i = hsl[1]
  , s = hsl[2]
s = 1
newColor = new ie.Swatch(se.hslToRgb(a, i, s), 0)
console.log(newColor)

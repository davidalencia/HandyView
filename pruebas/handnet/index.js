const tf = require('@tensorflow/tfjs');
require('@tensorflow/tfjs-node');

const fs = require('fs');
const CsvReadableStream = require('csv-reader');

file = "/home/valencia/Documents/python/handContrast/datos.csv"
const inputStream = fs.createReadStream(file, 'utf8');

const letras=[ 'A','B','C','D','E','F','G','H','I','J','K',
  'L','M','N','O','P','Q','R','S','T','U','V','W','X',
  'Y','Z','del','nothing','space' ]

let xs=[];
let testXs=[];
let ys, testYs;


indices = [];
testIndices = [];
deph = 29;

c=0
function onData(row) {
  if(c++%300!=0){
    indices.push(letras.indexOf(row.shift()));
    xs.push(row)
  }
  else{
    testIndices.push(letras.indexOf(row.shift()));
    testXs.push(row)
  }
}

saltar=300
async function onEnd(data)  {

  xs = tf.tensor2d(xs)
  ys = tf.oneHot(tf.tensor1d(indices, 'int32'), deph)

  testXs = tf.tensor2d(testXs)
  testYs = tf.oneHot(tf.tensor1d(testIndices, 'int32'), deph)

  const model = tf.sequential();
  model.add(tf.layers.dense({
      units: 25,
      inputShape: [20],
      activation:'softsign'
    }));
  model.add(tf.layers.dense({
      units: 25,
      activation:'elu'
    }));

  model.add(tf.layers.dense({
    units: 25,
    activation:'elu'
  }));
  model.add(tf.layers.dense({
    units: deph,
    activation: 'softmax'
  }));

  const opt= tf.train.adamax(0.01)

  model.compile({
    optimizer: opt,
    loss: tf.losses.meanSquaredError
  })

  config = {
    shuffle: true,
    epochs: 20
  }
  const resp = await model.fit(xs, ys, config)

  predictedYs = await model.predict(testXs)
  xsData = await testXs.data()
  testdata = await predictedYs.data()
  data = await testYs.data()

  count=0
  correct =0
  error = 0
  for(alfa=0; alfa<(250*29); alfa+=29){
    arr=testdata.slice(alfa, alfa+29)
    let i = arr.indexOf(Math.max.apply(null, arr));
    if(i==testIndices[count++])
      correct++
    else
      error++
  }
  console.log(`errores: ${error}, correctas: ${correct}, porcentaje:${correct/2.5}`);
}

inputStream
    .pipe(CsvReadableStream(
      { parseNumbers: true,
        parseBooleans: true,
        trim: true }))
    .on('data', onData)
    .on('end', onEnd);

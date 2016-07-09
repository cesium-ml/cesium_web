import React from 'react'

export var Progress = (props) => {
  let response = ''
  switch (props.type) {
    case 'data':
      response = 'Get a dataset'
      break
    case 'features':
      response = 'Compute features on it'
      break
    case 'models':
      response = 'Train a model'
      break
    case 'predict':
      response = 'Do some predictions'
      break
    default:
      break
  }

  return (
    <b>{response}</b>
  )
}

export {Progress as default}

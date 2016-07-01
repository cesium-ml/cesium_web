import { combineReducers } from 'redux'
import {reducer as formReducer} from 'redux-form'

import {
  RECEIVE_PROJECTS,
  RECEIVE_DATASETS,
  RECEIVE_FEATURESETS,
  RECEIVE_MODELS,
  RECEIVE_PREDICTIONS,
  CLEAR_FEATURES_FORM,
} from './actions'


function projects(state = [], action) {
  switch (action.type) {
    case RECEIVE_PROJECTS:
      return action.payload
    default:
      return state
  }
}


function datasets(state = [], action) {
  switch (action.type) {
    case RECEIVE_DATASETS:
      return action.payload
    default:
      return state
  }
}


function featuresets(state = [], action) {
  switch (action.type) {
    case RECEIVE_FEATURESETS:
      return action.payload
    // case CLEAR_FEATURES_FORM:
    //  return {
    default:
      return state
  }
}


function models(state, action) {
  switch (action.type) {
  default:
      return {formFields: {}}
  }
}


const rootReducer = combineReducers({
  projects,
  datasets,
  featuresets,
  models,
  form: formReducer
})

export default rootReducer

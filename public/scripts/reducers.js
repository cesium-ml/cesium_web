
import { combineReducers } from 'redux'

import {
  RECEIVE_PROJECTS
} from './actions'


function projects(state = [], action) {
  switch (action.type) {
    case RECEIVE_PROJECTS:
      return action.payload
    default:
      return state
  }
}

const rootReducer = combineReducers({
  projects
})

export default rootReducer

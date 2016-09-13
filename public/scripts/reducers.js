import { combineReducers } from 'redux';
import { reducer as formReducer } from 'redux-form';

import * as Action from './actions';
import { reducer as notifications } from './Notifications';


function projects(state={ projectList: [] }, action) {
  switch (action.type) {
    case Action.RECEIVE_PROJECTS:
      return { ...state, projectList: action.payload };
    default:
      return state;
  }
}


function datasets(state = [], action) {
  switch (action.type) {
    case Action.RECEIVE_DATASETS:
      return action.payload;
    default:
      return state;
  }
}


function featuresets(state={ featuresetList: [],
                            featuresList: [] }, action) {
  switch (action.type) {
    case Action.RECEIVE_FEATURESETS:
      // {obs_features, sci_features}
      return { ...state, featuresetList: action.payload };
    case Action.RECEIVE_FEATURES:
      return { ...state, features: action.payload };
    default:
      return state;
  }
}


function models(state = [], action) {
  switch (action.type) {
    case Action.RECEIVE_MODELS:
      return action.payload;
    default:
      return state;
  }
}


function predictions(state = [], action) {
  switch (action.type) {
    case Action.RECEIVE_PREDICTIONS:
      return action.payload;
    default:
      return state;
  }
}


const myFormReducer = theirFormReducer => (
  function (initialState, action) {
    const state = { ...initialState };
    switch (action.type) {
      case Action.SELECT_PROJECT: {
        const { id } = action.payload;
        state.projectSelector.project.value = id ? id.toString() : "";
      }
      case Action.GROUP_TOGGLE_FEATURES: {
        const field_names = Object.keys(state.featurize).filter(
          fn => fn.startsWith(action.payload));
        const featurizeFormState = Object.assign({}, state.featurize);
        const allAreChecked = (field_names.filter(
          el => !featurizeFormState[el].value).length === 0);
        for (const idx in field_names) {
          featurizeFormState[field_names[idx]].value = !allAreChecked;
        }
        featurizeFormState[`dummy_${String(Math.random())}`] = null;
        state.featurize = featurizeFormState;
      }
    }
    return theirFormReducer(state, action);
  }
);


function expander(state={ opened: {} }, action) {
  const id = action.payload ? action.payload.id : null;
  const newState = { ...state };

  if (!id) {
    return state;
  }

  switch (action.type) {
    case Action.TOGGLE_EXPANDER:
      newState.opened[id] = !state.opened[id];
      return newState;
    case Action.HIDE_EXPANDER:
      newState.opened[id] = false;
      return newState;
    case Action.SHOW_EXPANDER:
      newState.opened[id] = true;
      return newState;
    default:
      return state;
  }
}

function sklearnModels(state={}, action) {
  switch (action.type) {
    case Action.RECEIVE_SKLEARN_MODELS:
      return { ...(action.payload) };
    default:
      return state;
  }
}


function misc(state={ logoSpinAngle: 0 }, action) {
  switch (action.type) {
    case Action.SPIN_LOGO:
      return {
        ...state,
        logoSpinAngle: (state.logoSpinAngle + 360) % 720
      };
    default:
      return state;
  }
}


const rootReducer = combineReducers({
  projects,
  datasets,
  featuresets,
  models,
  predictions,
  notifications,
  expander,
  sklearnModels,
  form: myFormReducer(formReducer),
  misc
});

export default rootReducer;

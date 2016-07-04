// Action format:
// https://github.com/acdlite/flux-standard-action

import {reset as resetForm} from 'redux-form';

export const HYDRATE = 'cesium/HYDRATE'
export const FETCH_PROJECTS = 'cesium/FETCH_PROJECTS'
export const RECEIVE_PROJECTS = 'cesium/RECEIVE_PROJECTS'
export const FETCH_DATASETS = 'cesium/FETCH_DATASETS'
export const RECEIVE_DATASETS = 'cesium/RECEIVE_DATASETS'
export const RECEIVE_FEATURESETS = 'cesium/RECEIVE_FEATURESETS'
export const RECEIVE_MODELS = 'cesium/RECEIVE_MODELS'
export const RECEIVE_PREDICTIONS = 'cesium/RECEIVE_PREDICTIONS'
export const CLEAR_FEATURES_FORM = 'cesium/CLEAR_FEATURES_FORM'
export const CREATE_MODEL = 'cesium/CREATE_MODEL'
export const ADD_PROJECT = 'cesium/ADD_PROJECT'
export const SHOW_NOTIFICATION = 'cesium/SHOW_NOTIFICATION'
export const HIDE_NOTIFICATION = 'cesium/HIDE_NOTIFICATION'

export function hydrate() {
  return dispatch => {
    dispatch(fetchProjects())
      .then(proj => {
        dispatch(fetchDatasets());
        dispatch(fetchFeaturesets());
      })
      .then(proj => {
        dispatch(showNotification('Rehydrated!'))
      }
      );
//  dispatch(fetchModels());
//  dispatch(fetchPredictions());
  }
}

function promiseAction(dispatch, action_type, promise) {
  dispatch({
    type: action_type,
    payload: {
      promise: promise
    }
  });
  return promise;
}


// Download projects
export function fetchProjects() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_PROJECTS,

      fetch('/project')
        .then(response => response.json())
        .then(json => {
          dispatch(receiveProjects(json.data))
        }
        ).catch(ex => console.log('fetchProjects', ex))
      )
}

// Add a new project
export function addProject(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      ADD_PROJECT,

      fetch('/project',
            {method: 'POST',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             })})
        .then(response => response.json())
        .then(json => {
          if (json.status == 'success') {
            dispatch(resetForm('newProject'));
            dispatch(showNotification('Successfully added new project'))
          } else {
            return Promise.reject({_error: json.message});
          }
        })
  )
}


// Receive list of projects
function receiveProjects(projects) {
  return {
    type: RECEIVE_PROJECTS,
    payload: projects
  }
}




// Download datasets
export function fetchDatasets() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_DATASETS,

      fetch('/dataset')
        .then(response => response.json())
        .then(json => {
          dispatch(receiveDatasets(json.data))
        }
        ).catch(ex => console.log('fetchDatasets', ex))
    )
}

// Receive list of projects
function receiveDatasets(datasets) {
  return {
    type: RECEIVE_DATASETS,
    payload: datasets
  }
}


// Download featuresets
export function fetchFeaturesets() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_DATASETS,
      
      fetch('/features')
        .then(response => response.json())
        .then(json => {
          dispatch(receiveFeaturesets(json.data))
        }
        ).catch(ex => console.log('fetchFeaturesets', ex))
  )
}

// Receive list of featuresets
function receiveFeaturesets(featuresets) {
  return {
    type: RECEIVE_FEATURESETS,
    payload: featuresets
  }
}


// POST new featureset form
export function submitNewFeatureset(formdata) {
  var data = new FormData();
  data.append("json", JSON.stringify(formdata));
  return dispatch => (
    fetch('/features',
          {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: data
          }
    )
     .then(response => response.json())
     .then(json => {
       dispatch(clearFeaturesForm())
     }
     ).catch(ex => console.log('submitNewFeatureset', ex))
  )

  /* return dispatch => (
     $.ajax({
     url: '/features',
     dataType: 'json',
     type: 'POST',
     data: formdata,
     success: function(data) {
     console.log(data);
     },
     error: function(xhr, status, err) {
     console.error('/features', status, err.toString(),
     xhr.repsonseText);
     }
     })
     .then(response => response.json())
     .then(json => {
     dispatch(clearFeaturesForm())
     }
     ).catch(ex => console.log(ex))
   ) */
}

// Clear features form after submit
function clearFeaturesForm() {
  return {
    type: CLEAR_FEATURES_FORM
  }
}


export function createModel(form) {
  return {
    type: CREATE_MODEL,
    payload: form
  }
}

export function showNotification(text) {
  return (dispatch) => {
    setTimeout(() => dispatch(hideNotification()), 3500);
    dispatch({
      type: SHOW_NOTIFICATION,
      payload: text
    });
  }
}

export function hideNotification() {
  return {
    type: HIDE_NOTIFICATION
  }
}

// Action format:
// https://github.com/acdlite/flux-standard-action


export const HYDRATE = 'HYDRATE'
export const FETCH_PROJECTS = 'FETCH_PROJECTS'
export const RECEIVE_PROJECTS = 'RECEIVE_PROJECTS'
export const RECEIVE_DATASETS = 'RECEIVE_DATASETS'
export const RECEIVE_FEATURESETS = 'RECEIVE_FEATURESETS'
export const RECEIVE_MODELS = 'RECEIVE_MODELS'
export const RECEIVE_PREDICTIONS = 'RECEIVE_PREDICTIONS'
export const CLEAR_FEATURES_FORM = 'CLEAR_FEATURES_FORM'

export function hydrate() {
  return dispatch => {
    dispatch(fetchProjects());
    dispatch(fetchDatasets());
    dispatch(fetchFeaturesets());
//  dispatch(fetchModels());
//  dispatch(fetchPredictions());
  }
}


// Download projects
export function fetchProjects() {
  return dispatch => (
    fetch('/project')
      .then(response => response.json())
      .then(json => {
        dispatch(receiveProjects(json.data))
      }
      ).catch(ex => console.log(ex))
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
  return dispatch => (
    fetch('/dataset')
      .then(response => response.json())
      .then(json => {
        dispatch(receiveDatasets(json.data))
      }
      ).catch(ex => console.log(ex))
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
  return dispatch => (
    fetch('/features')
      .then(response => response.json())
      .then(json => {
        dispatch(receiveFeaturesets(json.data))
      }
      ).catch(ex => console.log(ex))
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
  return dispatch => (
    fetch('/features',
          {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            body: formdata
          }
    )
      .then(response => response.json())
      .then(json => {
        dispatch(clearFeaturesForm())
      }
      ).catch(ex => console.log(ex))
  )
}

// Clear features form after submit
function clearFeaturesForm() {
  return {
    type: CLEAR_FEATURES_FORM
  }
}


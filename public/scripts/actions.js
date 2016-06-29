// Action format:
// https://github.com/acdlite/flux-standard-action


export const HYDRATE = 'HYDRATE'
export const FETCH_PROJECTS = 'FETCH_PROJECTS'
export const RECEIVE_PROJECTS = 'RECEIVE_PROJECTS'
export const RECEIVE_DATASETS = 'RECEIVE_DATASETS'
export const RECEIVE_FEATURESETS = 'RECEIVE_FEATURESETS'
export const RECEIVE_MODELS = 'RECEIVE_MODELS'
export const RECEIVE_PREDICTIONS = 'RECEIVE_PREDICTIONS'

export function hydrate() {
  return dispatch => {
    dispatch(fetchProjects());
    // dispatch anything else here needed to intialize the app state on load
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

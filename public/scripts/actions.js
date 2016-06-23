// Action format:
// https://github.com/acdlite/flux-standard-action


// Download projects
export function fetchProjects() {
  return dispatch => {
    fetch('/project')
      .then(response => response.json())
      .then(json => {
        dispatch(receiveProjects(json.data))
      }
      ).catch(ex => console.log(ex));
  }
}


// Receive list of projects
export const RECEIVE_PROJECTS = 'RECEIVE_PROJECTS'

function receiveProjects(projects) {
  return {
    type: RECEIVE_PROJECTS,
    payload: projects
  }
}

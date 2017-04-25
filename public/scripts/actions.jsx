// Action format:
// https://github.com/acdlite/flux-standard-action

import { reset as resetForm } from 'redux-form';

export const HYDRATE = 'cesium/HYDRATE';

export const FETCH_PROJECTS = 'cesium/FETCH_PROJECTS';
export const RECEIVE_PROJECTS = 'cesium/RECEIVE_PROJECTS';
export const ADD_PROJECT = 'cesium/ADD_PROJECT';
export const DELETE_PROJECT = 'cesium/DELETE_PROJECT';
export const SELECT_PROJECT = 'cesium/SELECT_PROJECT';
export const UPDATE_PROJECT = 'cesium/UPDATE_PROJECT';
export const HIDE_NEWPROJECT_FORM = 'cesium/HIDE_NEWPROJECT_FORM';

export const FETCH_DATASETS = 'cesium/FETCH_DATASETS';
export const RECEIVE_DATASETS = 'cesium/RECEIVE_DATASETS';
export const UPLOAD_DATASET = 'cesium/UPLOAD_DATASET';
export const DELETE_DATASET = 'cesium/DELETE_DATASET';
export const CREATE_EXAMPLE_DATASET = 'cesium/CREATE_EXAMPLE_DATASET';

export const FETCH_FEATURES = 'cesium/FETCH_FEATURES';
export const FETCH_FEATURESETS = 'cesium/FETCH_FEATURESETS';
export const RECEIVE_FEATURES = 'cesium/RECEIVE_FEATURES';
export const RECEIVE_FEATURESETS = 'cesium/RECEIVE_FEATURESETS';
export const COMPUTE_FEATURES = 'cesium/COMPUTE_FEATURES';
export const DELETE_FEATURESET = 'cesium/DELETE_FEATURESET';

export const FETCH_MODELS = 'cesium/FETCH_MODELS';
export const RECEIVE_MODELS = 'cesium/RECEIVE_MODELS';
export const CREATE_MODEL = 'cesium/CREATE_MODEL';
export const DELETE_MODEL = 'cesium/DELETE_MODEL';

export const FETCH_PREDICTIONS = 'cesium/FETCH_PREDICTIONS';
export const RECEIVE_PREDICTIONS = 'cesium/RECEIVE_PREDICTIONS';
export const DO_PREDICTION = 'cesium/DO_PREDICTION';
export const DELETE_PREDICTION = 'cesium/DELETE_PREDICTION';

export const TOGGLE_EXPANDER = 'cesium/TOGGLE_EXPANDER';
export const HIDE_EXPANDER = 'cesium/HIDE_EXPANDER';
export const SHOW_EXPANDER = 'cesium/SHOW_EXPANDER';

export const FETCH_SKLEARN_MODELS = 'cesium/FETCH_SKLEARN_MODELS';
export const RECEIVE_SKLEARN_MODELS = 'cesium/RECEIVE_SKLEARN_MODELS';

export const SPIN_LOGO = 'cesium/SPIN_LOGO';
export const GROUP_TOGGLE_FEATURES = 'cesium/GROUP_TOGGLE_FEATURES';
export const CLICK_FEATURE_TAG_CHECKBOX = 'cesium/CLICK_FEATURE_TAG_CHECKBOX';


import { showNotification, reduceNotifications } from './Notifications';
import promiseAction from './action_tools';
import { objectType } from './utils';

// Refactor this into a utility function
String.prototype.format = function (...args) {
  let i = 0;
  return this.replace(/{}/g, () => (
    typeof args[i] != 'undefined' ? args[i++] : ''
  ));
};


// Receive list of projects
function receiveProjects(projects) {
  return {
    type: RECEIVE_PROJECTS,
    payload: projects
  };
}


// Download projects
export function fetchProjects() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_PROJECTS,

      fetch('/project')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(receiveProjects(json.data));
          } else {
            dispatch(
              showNotification(
                'Error downloading projects ({})'.format(json.message)
              ));
          }
          return json;
        }
        ).catch(ex => console.log('fetchProjects exception:', ex))
      );
}


// Add a new project
export function addProject(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      ADD_PROJECT,

      fetch('/project',
            { method: 'POST',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             }) })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(resetForm('newProject'));
            dispatch(showNotification('Added new project'));
            dispatch(selectProject(json.data.id));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


// Update an existing project
export function updateProject(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      UPDATE_PROJECT,

      fetch('/project/{}'.format(form.projectId),
            { method: 'PUT',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             }) })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(resetForm('newProject'));
            dispatch(showNotification('Successfully updated project'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


export function deleteProject(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_PROJECT,

      fetch(`/project/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Project deleted'));
            dispatch(selectProject());
          } else {
            dispatch(
              showNotification(
                'Error deleting project ({})'.format(json.message)
              ));
          }
        })
  );
}


export function uploadDataset(form) {
  const formData = new FormData();

  for (const key in form) {
    if (form[key] && objectType(form[key][0]) === 'File') {
      formData.append(key, form[key][0]);
    } else {
      formData.append(key, form[key]);
    }
  }

  return dispatch =>
    promiseAction(
      dispatch,
      UPLOAD_DATASET,

      fetch('/dataset', { method: 'POST', body: formData })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Successfully uploaded new dataset'));
            dispatch(hideExpander('newDatasetExpander'));
            dispatch(resetForm('newDataset'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}

// Download datasets
export function fetchDatasets() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_DATASETS,

      fetch('/dataset')
        .then(response => response.json())
        .then((json) => (
          dispatch(receiveDatasets(json.data))
        )
        ).catch(ex => console.log('fetchDatasets', ex))
    );
}

// Receive list of projects
function receiveDatasets(datasets) {
  return {
    type: RECEIVE_DATASETS,
    payload: datasets
  };
}


// Create example dataset
export function createExampleDataset(projectID) {
  var form_data = new FormData();
  form_data.append('projectID', projectID);
  form_data.append('create_example', true);

  return dispatch =>
    promiseAction(
      dispatch,
      CREATE_EXAMPLE_DATASET,

      fetch('/dataset', {
        method: 'POST',
        body: form_data,
      })
        .then(response => response.json())
        .then((json) => {
            dispatch(fetchDatasets());
            dispatch(hideExpander('newDatasetExpander'));
            dispatch(resetForm('newDataset'));
          }).catch(ex => console.log('createExampleDataset', ex))
    );
}


// Download featuresets
export function fetchFeaturesets() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_FEATURESETS,

      fetch('/features')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            return dispatch(receiveFeaturesets(json.data));
          } else {
            return dispatch(
              showNotification(
                'Error downloading feature sets ({})'.format(json.message)
              ));
          }
        }
        ).catch(ex => console.log('fetchFeaturesets', ex))
  );
}

// Receive list of featuresets
function receiveFeaturesets(featuresets) {
  return {
    type: RECEIVE_FEATURESETS,
    payload: featuresets
  };
}


export function createModel(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      CREATE_MODEL,

      fetch('/models',
            { method: 'POST',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             }) })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(resetForm('newModel'));
            dispatch(hideExpander('newModelExpander'));
            dispatch(showNotification('Model training begun.'));
          } else {
            return Promise.reject({ _error: json.message });
          }
          return json;
        })
  );
}


export function hideExpander(id) {
  return {
    type: HIDE_EXPANDER,
    payload: {
      id
    }
  };
}

export function showExpander(id) {
  return {
    type: SHOW_EXPANDER,
    payload: {
      id
    }
  };
}

export function toggleExpander(id) {
  return {
    type: TOGGLE_EXPANDER,
    payload: {
      id
    }
  };
}

// Currently, used upon creation of a new project to switch to that project
export function selectProject(id=null) {
  return (dispatch) => {
    dispatch(hideExpander('newProjectExpander'));

    return dispatch({
      type: SELECT_PROJECT,
      payload: { id }
    });
  };
}


export function fetchFeatures() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_FEATURES,

      fetch('/features_list')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(receiveFeatures(json.data));
          } else {
            dispatch(
              showNotification(
                'Error downloading features ({})'.format(json.message)
              ));
          }
          return json;
        }
        ).catch(ex => console.log('fetchFeatures exception:', ex))
    );
}

// Receive list of featuresets
function receiveFeatures(features) {
  return {
    type: RECEIVE_FEATURES,
    payload: features,
  };
}


export function computeFeatures(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      COMPUTE_FEATURES,

      fetch('/features',
            { method: 'POST',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             }) }
      ).then(response => response.json()
      ).then((json) => {
        if (json.status == 'success') {
          dispatch(resetForm('featurize'));
          dispatch(showNotification('Feature computation begun.'));
          dispatch(hideExpander('featsetFormExpander'));
        } else {
          return Promise.reject({ _error: json.message });
        }
        return json;
      })
    );
}


export function deleteDataset(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_DATASET,

      fetch(`/dataset/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Dataset deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting dataset ({})'.format(json.message)
              ));
          }
        })
  );
}


export function deleteFeatureset(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_FEATURESET,

      fetch(`/features/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Feature set deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting feature set ({})'.format(json.message)
              ));
          }
        })
  );
}


export function fetchSklearnModels() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_SKLEARN_MODELS,

      fetch('/sklearn_models')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(receiveSklearnModels(json.data));
          } else {
            dispatch(
              showNotification(
                'Error downloading sklearn models ({})'.format(json.message)
              ));
          }
          return json;
        }
        ).catch(ex => console.log('fetchSklearnModels exception:', ex))
      );
}

function receiveSklearnModels(sklearn_models) {
  return {
    type: RECEIVE_SKLEARN_MODELS,
    payload: sklearn_models
  };
}


// Download models
export function fetchModels() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_MODELS,

      fetch('/models')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            return dispatch(receiveModels(json.data));
          } else {
            return dispatch(
              showNotification(
                'Error downloading models ({})'.format(json.message)
              ));
          }
        }
        ).catch(ex => console.log('fetchModels', ex))
    );
}

// Receive list of models
function receiveModels(models) {
  return {
    type: RECEIVE_MODELS,
    payload: models
  };
}


export function deleteModel(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_MODEL,

      fetch(`/models/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Model deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting model ({})'.format(json.message)
              ));
          }
        })
  );
}


export function doPrediction(form) {
  return dispatch =>
    promiseAction(
      dispatch,
      DO_PREDICTION,

      fetch('/predictions',
            { method: 'POST',
             body: JSON.stringify(form),
             headers: new Headers({
               'Content-Type': 'application/json'
             }) }
      ).then(response => response.json()
      ).then((json) => {
        if (json.status == 'success') {
          dispatch(resetForm('predict'));
          dispatch(showNotification('Model predictions begun.'));
          dispatch(hideExpander('predictFormExpander'));
        } else {
          return Promise.reject({ _error: json.message });
        }
        return json;
      })
    );
}


export function deletePrediction(id) {
  return dispatch =>
    promiseAction(
      dispatch,
      DELETE_PREDICTION,

      fetch(`/predictions/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            dispatch(showNotification('Prediction deleted'));
          } else {
            dispatch(
              showNotification(
                'Error deleting prediction ({})'.format(json.message)
              ));
          }
        })
    );
}


// Download predictions
export function fetchPredictions() {
  return dispatch =>
    promiseAction(
      dispatch,
      FETCH_PREDICTIONS,

      fetch('/predictions')
        .then(response => response.json())
        .then((json) => {
          if (json.status == 'success') {
            return dispatch(receivePredictions(json.data));
          } else {
            return dispatch(showNotification(json.message));
          }
        }
        ).catch(ex => console.log('fetchPredictions', ex))
    );
}

// Receive list of predictions
export function receivePredictions(preds) {
  return {
    type: RECEIVE_PREDICTIONS,
    payload: preds
  };
}


export function spinLogo() {
  return {
    type: SPIN_LOGO
  };
}


export function groupToggleCheckedFeatures(list_of_feats_in_category) {
  return {
    type: GROUP_TOGGLE_FEATURES,
    payload: { ctgy_list: list_of_feats_in_category }
  };
}


export function clickFeatureTagCheckbox(tag) {
  return {
    type: CLICK_FEATURE_TAG_CHECKBOX,
    payload: { tag }
  };
}


export function hydrate() {
  return (dispatch) => {
    dispatch(fetchProjects())
      .then((proj) => {
        Promise.all([
          dispatch(fetchDatasets()),
          dispatch(fetchFeaturesets()),
          dispatch(fetchFeatures()),
          dispatch(fetchModels()),
          dispatch(fetchPredictions())
        ]).then(() => {
          dispatch(spinLogo());
        });
      });
    dispatch(fetchSklearnModels());
  };
}

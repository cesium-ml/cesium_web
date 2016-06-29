import React from 'react'
import { connect } from "react-redux"
import ReactDOM from 'react-dom'
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'
import FileInput from 'react-file-input'
import ReactTabs from 'react-tabs'
import CheckboxGroup from 'react-checkbox-group'

var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;

import _ from 'underscore'
import filter from 'filter-values'

import 'bootstrap-css'
import 'bootstrap'


import { Provider } from 'react-redux'
import configureStore from './configureStore'

import * as Action from './actions';


const store = configureStore()

import WebSocket from './WebSocket'
import MessageHandler from './MessageHandler'
let messageHandler = (new MessageHandler(store.dispatch)).handle;


import ProjectList from './ProjectList'
import DatasetsTab from './Datasets'
import FeaturesTab from './Features'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'


function json_post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: body,
  });
}

var MainContent = React.createClass({
  getInitialState: function() {
    return {
      forms: {
        newProject:
        {
          'Project Name': '',
          'Description/notes': ''
        },
        newDataset:
        {
          'Select Project': '',
          'Dataset Name': '',
          'Header File': '',
          'Tarball Containing Data': ''
        },
        featurize:
        {
          'Select Project': '',
          'Select Dataset': '',
          'Feature Set Title': '',
          'Custom Features File': '',
          'Custom Features Script Tested': false,
          'Selected Features': [],
          'Custom Features List': []
        },
        model:
        {
          'Select Project': ''
        },
        predict:
        {
          'Select Project': ''
        },
        selectedProjectToEdit:
        {
          'Description/notes': '',
          'Project Name': ''
        }
      },
      available_features:
      {
        obs_features: {'feat1': 'checked'},
        sci_features: {'feat1': 'checked'}
      },
      projectsList: [],
      datasetsList: []
    };
  },
  componentWillReceiveProps: function(nextProps) {
    if (!this.state.forms.newDataset['Select Project']) {
      var first_project_id = nextProps.projects[0].id;
      var first_dataset_id = nextProps.datasets[0].id;
      this.setState(
        {forms: {...this.state.forms,
                 newDataset: { ...this.state.forms.newDataset,
                               'Select Project': first_project_id },
                 featurize: { ...this.state.forms.featurize,
                              'Select Dataset': first_dataset_id,
                              'Select Project': first_project_id },
                 model: { ...this.state.forms.model,
                          'Select Dataset': first_dataset_id,
                          'Select Project': first_project_id },
                 predict: { ...this.state.forms.predict,
                            'Select Dataset': first_dataset_id,
                            'Select Project': first_project_id }
        }}
      );
    }
  },
  componentDidMount: function() {
    store.dispatch(Action.hydrate());
  },
  updateProjectList: function() {
    $.ajax({
      url: '/project',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        var form_state = this.state.forms;
        form_state.newProject = this.getInitialState().forms.newProject;
        this.setState(
          {
            projectsList: data.data,
            forms: form_state
          });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/project', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  handleNewProjectSubmit: function(e) {
    e.preventDefault();
    $.ajax({
      url: '/project',
      dataType: 'json',
      type: 'POST',
      data: this.state.forms.newProject,
      success: function(data) {
        this.updateProjectList();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/project', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  handleClickEditProject: function(projectID, e) {
    $.ajax({
      url: '/project/' + projectID,
      dataType: 'json',
      cache: false,
      type: 'GET',
      success: function(data) {
        var projData = {};
        projData['Project Name'] = data.data['name'];
        projData['Description/notes'] = data.data['description'];
        projData['project_id'] = projectID;
        var form_state = this.state.forms;
        form_state['selectedProjectToEdit'] = projData;
        this.setState({forms: form_state});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/project', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  updateProjectInfo: function(e) {
    e.preventDefault();
    $.ajax({
      url: '/project',
      dataType: 'json',
      type: 'POST',
      data: this.state.forms.selectedProjectToEdit,
      success: function(data) {
        var form_state = this.state.forms;
        form_state.selectedProjectToEdit = this.getInitialState().forms.selectedProjectToEdit;
        this.setState({projectsList: data, forms: form_state});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/project', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  handleDeleteProject: function(projectID, e) {
    $.ajax({
      url: '/project/' + projectID,
      dataType: 'json',
      type: 'DELETE',
      success: function(data) {
        this.updateProjectList();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/project', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  handleNewDatasetSubmit: function(e){
    e.preventDefault();
    var formData = new FormData();
    for (var key in this.state.forms.newDataset) {
      formData.append(key, this.state.forms.newDataset[key]);
    }
    $.ajax({
      url: '/dataset',
      dataType: 'json',
      type: 'POST',
      contentType: false,
      processData: false,
      data: formData,
      success: function(data) {
        store.dispatch(Action.hydrate())
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/dataset', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  onFeaturesDialogMount: function() {
    $.ajax({
      url: '/features_list',
      dataType: 'json',
      cache: false,
      success: function(data) {
        var obs_features_dict = _.object(
          _.map(data.data['obs_features'], function(feat) {
            return [feat, 'checked']; }));
        var sci_features_dict = _.object(
          _.map(data.data['sci_features'], function(feat) {
            return [feat, 'checked']; }));
        this.setState(
          {
            available_features:
            {
              obs_features: obs_features_dict,
              sci_features: sci_features_dict
            }
          });
        this.updateSeldFeatsList();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('/features_list', status, err.toString(),
                xhr.repsonseText);
      }.bind(this)
    });
  },
  updateSeldFeatsList: function() {
    var seld_obs_feats = Object.keys(
      filter(this.state.available_features['obs_features'], 'checked'));
    var seld_sci_feats = Object.keys(
      filter(this.state.available_features['sci_features'], 'checked'));
    var all_seld_feats = seld_obs_feats.concat(seld_sci_feats);
    this.setState({
      forms: {...this.state.forms, featurize: {...this.state.forms.featurize,
                                    "Selected Features": all_seld_feats}
      }
    });
  },
  updateSeldObsFeats: function(sel_obs_feats) {
    var obs_feats_dict = this.state.available_features.obs_features;
    for (var k in this.state.available_features.obs_features) {
      obs_feats_dict[k] = (sel_obs_feats.indexOf(k) == -1) ? 'unchkd' : 'checked';
    }
    this.setState(
      {
        available_features:
        {
          obs_features: obs_feats_dict,
          sci_features: this.state.available_features.sci_features
        }
      });
    this.updateSeldFeatsList();
  },
  updateSeldSciFeats: function(sel_sci_feats) {
    var sci_feats_dict = this.state.available_features.sci_features;
    for (var k in this.state.available_features.sci_features) {
      sci_feats_dict[k] = (sel_sci_feats.indexOf(k) == -1) ? 'unchkd' : 'checked';
    }
    this.setState(
      {
        available_features: {
          sci_features: sci_feats_dict,
          obs_features: this.state.available_features.obs_features
        }
      });
    this.updateSeldFeatsList();
  },
  testCustomFeatScript: function (e) {
    // TODO: DO STUFF HERE
    console.log('testCustomFeatScript called... Nothing here yet.');
  },
  handleNewFeaturesetSubmit: function(e) {
    e.preventDefault();
    // store.dispatch(Action.submitNewFeatureset(this.state.forms.featurize));
    $.ajax({
      url: '/features',
      dataType: 'json',
      type: 'POST',
      data: this.state.forms.featurize,
      success: function(data) {
        console.log(data.status);
      },
      error: function(xhr, status, err) {
        console.error('/features', status, err.toString(),
                      xhr.repsonseText);
      }
    });
  },
  handleInputChange: function(inputName, inputType, formName, e) {
    var form_state = this.state.forms;
    if (inputType == 'file') {
      var newValue = e.target.files[0];
    } else {
      var newValue = e.target.value;
    }
    form_state[formName][inputName] = newValue;
    this.setState({forms: form_state});
  },
  render: function() {
    return (
      <div className='mainContent'>
        <Tabs classname='first'>
          <TabList>
            <Tab>Projects</Tab>
            <Tab>Data</Tab>
            <Tab>Features</Tab>
            <Tab>Models</Tab>
            <Tab>Predict</Tab>
            <Tab>
              <WebSocket url={'ws://' + this.props.root + 'websocket'}
                         auth_url={location.protocol + '//' + this.props.root + 'socket_auth_token'}
                         messageHandler={messageHandler}
              />
            </Tab>
          </TabList>
          <TabPanel>
            <ProjectsTabContent
              getInitialState={this.getInitialState}
              handleNewProjectSubmit={this.handleNewProjectSubmit}
              handleClickEditProject={this.handleClickEditProject}
              handleDeleteProject={this.handleDeleteProject}
              handleInputChange={this.handleInputChange}
              formFields={this.state.forms.newProject}
              projects={this.props.projects}
              projectDetails={this.state.forms.selectedProjectToEdit}
              updateProjectInfo={this.updateProjectInfo}
            />
          </TabPanel>
          <TabPanel>
            <DatasetsTab
              getInitialState={this.getInitialState}
              handleNewDatasetSubmit={this.handleNewDatasetSubmit}
              handleInputChange={this.handleInputChange}
              formFields={this.state.forms.newDataset}
              formName='newDataset'
              projects={this.props.projects}
              datasets={this.props.datasets}
            />
          </TabPanel>
          <TabPanel>
            <FeaturesTab
              getInitialState={this.getInitialState}
              handleSubmit={this.handleNewFeaturesetSubmit}
              handleInputChange={this.handleInputChange}
              formFields={this.state.forms.featurize}
              projects={this.props.projects}
              datasets={this.props.datasets}
              featuresets={this.props.featuresets}
              available_features={this.state.available_features}
              updateSeldObsFeats={this.updateSeldObsFeats}
              updateSeldSciFeats={this.updateSeldSciFeats}
              onFeaturesDialogMount={this.onFeaturesDialogMount}
              testCustomFeatScript={this.testCustomFeatScript}
            />
          </TabPanel>
          <TabPanel>
            Models...
          </TabPanel>
          <TabPanel>
            Predictions...
          </TabPanel>
          <TabPanel>
            <h3>System Status</h3>
          </TabPanel>
        </Tabs>
      </div>
    );
  }
});

var ProjectsTabContent = React.createClass({
  render: function() {
    return (
      <div className='projectsTabContent'>
        <NewProjectForm
          handleInputChange={this.props.handleInputChange}
          formFields={this.props.formFields}
          handleSubmit={this.props.handleNewProjectSubmit}
        />
        <ProjectList
          projectsList={this.props.projectsList}
          clickEditProject={this.props.handleClickEditProject}
          deleteProject={this.props.handleDeleteProject}
          projectDetails={this.props.projectDetails}
          handleInputChange={this.props.handleInputChange}
          updateProjectInfo={this.props.updateProjectInfo}
        />
      </div>
    );
  }
});

var NewProjectForm = React.createClass({
  render: function() {
    return (
      <div className='formTableDiv' data-test-name='newProjectForm'>
        <FormTitleRow formTitle='Create a new project'
        />
        <FormInputRow
          inputName='Project Name'
          inputTag='input'
          inputType='text'
          formName='newProject'
          value={this.props.formFields['Project Name']}
          handleInputChange={this.props.handleInputChange}
        />
        <FormInputRow
          inputName='Description/notes'
          inputTag='textarea'
          formName='newProject'
          value={this.props.formFields['Description/notes']}
          handleInputChange={this.props.handleInputChange}
        />
        <div className='submitButtonDiv' style={{marginTop: 15}}>
          <input
            type='submit'
            onClick={this.props.handleSubmit}
            value='Submit'
            className='submitButton'
          />
        </div>
      </div>
    );
  }
});

var mapStateToProps = function(state) {
  return {
    projects: state.projects,
    datasets: state.datasets,
    featuresets: state.featuresets
  };
}

MainContent = connect(mapStateToProps)(MainContent);


ReactDOM.render(
  <Provider store={store}>
  <MainContent root={ location.host + location.pathname }/>
  </Provider>,
  document.getElementById('content')
);

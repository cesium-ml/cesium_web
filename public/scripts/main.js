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
const store = configureStore()

import * as Action from './actions';

import WebSocket from './WebSocket'
import MessageHandler from './MessageHandler'
let messageHandler = (new MessageHandler(store.dispatch)).handle;

import { ProjectSelector, AddProject, ProjectTab } from './Projects'
import DatasetsTab from './Datasets'
import FeaturesTab from './Features'
import ModelsTab from './Models'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
import { Notifications } from './Notifications'


var MainContent = React.createClass({
  getInitialState: function() {
    return {
      forms: {
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
  componentDidMount: function() {
    store.dispatch(Action.hydrate());
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
    let style = {
      width: 800
    }
    return (
      <div className='mainContent' style={style}>
        <Notifications style={style.notifications}/>
        <ProjectSelector/>
        <AddProject folded={true} id='newProjectExpander'/>

        <Tabs classname='first'>
          <TabList>
            <Tab>Project</Tab>
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
            <ProjectTab selectedProject={this.props.selectedProject}/>
          </TabPanel>
          <TabPanel>
            <DatasetsTab selectedProject={this.props.selectedProject}/>
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
            <ModelsTab onSubmitModelClick={this.props.handleSubmitModelClick}/>
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

var mapStateToProps = function(state) {
  // This can be improved by using
  // http://redux-form.com/6.0.0-alpha.13/docs/api/FormValueSelector.md/
  let projectSelector = state.form.projectSelector;
  let selectedProjectId = projectSelector ? projectSelector.project.value : "";
  let selectedProject = state.projects.projectList.filter(
    p => (p.id == selectedProjectId)
  );

  let firstProject = state.projects[0] || {'id': '', label: '', description: ''};

  if (selectedProject.length > 0) {
    selectedProject = selectedProject[0];
  } else {
    selectedProject = firstProject;
  }

  return {
    projects: state.projects.projectList,
    datasets: state.datasets,
    featuresets: state.featuresets,
    selectedProject: selectedProject,
  };
}

var mapDispatchToProps = (dispatch) => {
  return {
    handleSubmitModelClick: (form) => {
      dispatch(Action.createModel(form));
    }
  }
}

MainContent = connect(mapStateToProps, mapDispatchToProps)(MainContent);


ReactDOM.render(
  <Provider store={store}>
  <MainContent root={ location.host + location.pathname }/>
  </Provider>,
  document.getElementById('content')
);

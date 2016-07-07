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
import PredictTab from './Predictions'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
import { Notifications } from './Notifications'


var MainContent = React.createClass({
  componentDidMount: function() {
    store.dispatch(Action.hydrate());
  },
  render: function() {
    let style = {
      main: {
        background: 'white',
        width: 800,
        marginLeft: 50,
        marginRight: 'auto',
        marginTop: 20,
        paddingLeft: '2em',
        paddingBottom: '1em',
        selectors: {
          paddingLeft: '2em',
          marginBottom: '1em',
          borderLeft: '20px solid MediumVioletRed'
        }
      },
      topbar: {
        position: 'relative',
        left: '-2em',
        background: '#eee',
        height: 50,
        paddingTop: 0,
        margin: 0,
        width: 800,
        marginBottom: '1em',
        paddingLeft: '1em',
        paddingRight: '1em',
        img: {
          float: 'right',
          height: 50,
          paddingTop: 10,
          paddingBottom: 10
        },
        text: {
          display: 'inline-block',
          fontWeight: 'bold',
          fontSize: '120%',
          lineHeight: '50px',
          verticalAlign: 'bottom'
        }
      },
      footer: {
        paddingRight: '1em',
        textAlign: 'right'
      }
    }
    let rotate = 'rotate(' + this.props.logoSpinAngle + 'deg)'
    let rotateStyle = {
      WebkitTransition: 'all 1.0s ease-in-out',
      MozTransition: 'all 1.0s ease-in-out',
      OTransition: 'all 1.0s ease-in-out',
      transition: 'all 1.0s ease-in-out',
      WebkitTransform: rotate,
      MozTransform: rotate,
      msTransform: rotate,
      OTransform: rotate,
      transform: rotate
    }
    return (
      <div className='mainContent' style={style.main}>

        <div style={style.topbar}>
          <div style={style.topbar.text}>
            Cesium :: <em>Machine Learning Time Series Platform</em>
          </div>
          <img src='images/cesium-blue-light.png'
               onClick={this.props.spinLogo}
               style={{...(style.topbar.img), ...rotateStyle}}
          />
        </div>

        <Notifications style={style.notifications}/>
        <div style={style.selectors}>
          <ProjectSelector/>
          <AddProject id='newProjectExpander'/>
        </div>

        <Tabs>
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
            <FeaturesTab selectedProject={this.props.selectedProject} />
          </TabPanel>
          <TabPanel>
            <ModelsTab selectedProject={this.props.selectedProject}/>
          </TabPanel>
          <TabPanel>
            <PredictTab selectedProject={this.props.selectedProject}/>
          </TabPanel>
          <TabPanel>
            <h3>System Status</h3>
          </TabPanel>
        </Tabs>
        <hr/>
          <div style={style.footer}>
            Follow the <a href="http://cesium.ml">Cesium project</a> on <a href="https://github.com/cesium-ml">GitHub</a>
          </div>
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
    logoSpinAngle: state.misc.logoSpinAngle
  };
}

var mapDispatchToProps = (dispatch) => {
  return {
    handleSubmitModelClick: (form) => {
      dispatch(Action.createModel(form));
    },
    spinLogo: () => {
      dispatch(Action.spinLogo());
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

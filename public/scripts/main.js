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
    let config = {
      sidebar: 300,
      main: 800,
      top: 20
    }

    let style = {
      main: {
        background: 'white',
        width: config.main,
        marginLeft: 30 + config.sidebar,
        marginRight: 'auto',
        top: config.top,
        position: 'relative',
        paddingLeft: '2em',
        paddingBottom: '1em',
        paddingTop: '1em',
        paddingRight: '1em',
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
        height: 95,
        top: 0,
        margin: 0,
        width: config.sidebar,
        borderRight: 'solid 2px #36454f',
        marginBottom: '1em',
        paddingLeft: '1em',
        paddingRight: '1em',
        paddingTop: '0em',
        logo: {
          position: 'absolute',
          right: '1em',
          top: 5,
          height: 50,
          marginBottom: '1em',
          img: {
            height: 50,
            paddingTop: 10,
            paddingBottom: 10,
          }
        },
        header: {
          float: 'right',
          fontWeight: 'bold',
          fontSize: '120%',
          lineHeight: '50px',
          verticalAlign: 'bottom'
        },
        subheader: {
          fontStyle: 'italic',
          float: 'right'
        },
        text: {
          paddingTop: '0.5em'
        }
      },
      sidebar: {
        width: config.sidebar,
        background: 'MediumAquaMarine',
        position: 'relative',
        top: '0em',
        left: '0em',
        paddingLeft: '2em',
        position: 'absolute',
        height: '100%',
        borderRight: 'solid 2px #36454f',
      },
      footer: {
        paddingRight: '1em',
        textAlign: 'right'
      },
      tabs: {
        paddingTop: '1em'
      },
      projectSelector: {
        padding: 0
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
      <div>

      <div style={style.sidebar}>
        <div style={style.topbar}>
          <div style={style.topbar.text}>
            <span style={style.topbar.header}>Cesium</span><br/>
            <span style={style.topbar.subheader}>Machine Learning Time-Series Platform</span>
          </div>
        </div>

        <div style={style.selectors}>
          <ProjectSelector/>
          <AddProject id='newProjectExpander' label='Or click here to add a new one'/>
        </div>
      </div>

      <div className='mainContent' style={style.main}>

        <Notifications style={style.notifications}/>

        <Tabs>
          <TabList style={style.tabs}>
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

               <div style={style.topbar.logo}>
                 <img src='images/cesium-blue-light.png'
                      onClick={this.props.spinLogo}
                      style={{...(style.topbar.logo.img), ...rotateStyle}}/>
               </div>

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

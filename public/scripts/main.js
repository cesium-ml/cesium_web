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
        paddingRight: '1em',
        selectors: {
          paddingLeft: '2em',
          marginBottom: '1em',
          borderLeft: '20px solid MediumVioletRed'
        }
      },
      topbar: {
        position: 'relative',
        left: 0,
        background: '#008CBA',
        color: '#EFEFEF',
        height: 95,
        top: 0,
        margin: 0,
        width: config.sidebar,
        borderRight: 'solid 2px #36454f',
        marginBottom: '1em',
        paddingLeft: '1em',
        paddingRight: '1em',
        paddingTop: '0em',
        header: {
          float: 'right',
          fontWeight: 'bold',
          fontSize: '200%',
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
      sidebar: {
        width: config.sidebar,
        background: 'MediumAquaMarine',
        position: 'relative',
        top: '0em',
        left: '0em',
        position: 'absolute',
        height: '100%',
        borderRight: 'solid 2px #36454f',
      },
      sidebarContent: {
        paddingLeft: '1em'
      },
      footer: {
        paddingRight: '1em',
        textAlign: 'right'
      },
      tabs: {
        paddingTop: '1.5em'
      },
      projectSelector: {
        padding: 0,
        paddingLeft: '1em',
        margin: 0,
        position: 'relative',
        top: '-1.2em',
      },
      topic: {
        width: config.sidebar,
        position: 'relative',
        left: 0,
        background: 'DarkMagenta',
        color: '#EFEFEF',
        height: 60,
        lineHeight: '60px',
        verticalAlign: 'middle',
        top: 0,
        margin: 0,
        padding: 0,
        fontSize: '180%',
        width: '100%',
        marginBottom: '1em',
        paddingTop: 0,
        paddingRight: '1em',
        paddingLeft: '0.5em'
      },
      moveUp: {
        position: 'relative',
        top: '-2em',
        paddingTop: 0
      },
      circleStyle: {
        display: 'inline-block',
        padding: 0,
        lineHeight: '60px',
        textAlign: 'center',
        whiteSpace: 'nowrap',
        verticalAlign: 'baseline',
        backgroundColor: 'Gold',
        borderRadius: '50%',
        border: '2px solid gray',
        position: 'relative',
        height: 60,
        width: 60,
        padding: 0,
        fontSize: '200%',
        marginRight: '0.5em'
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

        <div style={style.topic}>Project</div>

        <div style={style.sidebarContent}>
          <ProjectSelector label='Choose your project here:' style={style.projectSelector}/>
          <AddProject id='newProjectExpander' label='Or click here to add a new one' style={style.moveUp}/>
        </div>

        <div style={style.topic}>Progress</div>

        <div style={style.sidebarContent}>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>1. Do you have a dataset?</b><br/><br/>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>2. Have you computed features?</b><br/>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>2. How about training a model?</b><br/>
        </div>

      </div>

      <div className='mainContent' style={style.main}>

        <Notifications style={style.notifications}/>

        <div style={style.logo}>
          <img src='images/cesium-blue-light.png'
               onClick={this.props.spinLogo}
               style={{...(style.logo.img), ...rotateStyle}}/>
        </div>


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

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
import { colorScheme as cs } from './colorscheme'


var MainContent = React.createClass({
  componentDidMount: function() {
    store.dispatch(Action.hydrate());
  },
  render: function() {
    let config = {
      sidebar: 300,
      topbar: '4em',
      footer: '4em'
    }

    let style = {
      main: {
        background: 'white',

        position: 'absolute',
        bottom: 0,
        height: 'auto',
        overflow: 'hidden',
        top: config.topbar,
        right: 0,
        left: config.sidebar,
        width: 'auto',

        paddingLeft: '2em',
        paddingBottom: '1em',
        marginBottom: 0,
        marginRight: 'auto',

        selectors: {
          paddingLeft: '2em',
          marginBottom: '1em',
          borderLeft: '20px solid MediumVioletRed'
        }
      },
      topbar: {
        position: 'relative',
        left: 0,
        background: cs.darkBlue,
        color: '#EFEFEF',
        height: config.topbar,
        lineHeight: config.topbar,
        verticalAlign: 'middle',
        top: 0,
        margin: 0,
        right: 0,
        borderRight: 'solid 2px #36454f',
        marginBottom: '1em',
        paddingLeft: '1em',
        paddingRight: '1em',
        header: {
          float: 'right',
          fontWeight: 'bold',
          fontSize: '200%',
          lineHeight: '50px',
          verticalAlign: 'bottom'
        },
        subheader: {
          fontStyle: 'italic',
          fontSize: '100%',
          float: 'right'
        },
        text: {
          paddingTop: '0.5em'
        }
      },
      logo: {
        img: {
          height: 50,
          paddingTop: 10,
          paddingBottom: 10,
        }
      },
      sidebar: {
        width: config.sidebar,
        background: '#eee',
        position: 'absolute',
        top: config.topbar,
        bottom: 0,
        left: '0em',
        position: 'absolute',
        height: 'auto',
      },
      sidebarContent: {
        paddingLeft: '1em'
      },
      footer: {
        fontSize: '110%',
        position: 'absolute',
        bottom: 0,
        left: 0,
        width: '100%',
        textAlign: 'center',
        verticalAlign: 'middle',
        color: 'white',
        lineHeight: config.footer,
        height: config.footer,
        background: cs.darkBlue,
        a: {
          color: 'white',
          textDecoration: 'underline'
        }
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
        background: cs.blue,
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
        lineHeight: '40px',
        textAlign: 'center',
        whiteSpace: 'nowrap',
        verticalAlign: 'baseline',
        backgroundColor: cs.lightBlue,
        borderRadius: '50%',
        border: '2px solid gray',
        position: 'relative',
        height: 40,
        width: 40,
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

        <div style={style.topbar}>
          <div style={style.topbar.text}>
            <div style={style.topbar.header}>
              Cesium &nbsp;
                <img src='images/cesium-blue-dark.png'
                     onClick={this.props.spinLogo}
                     style={{...(style.logo.img), ...rotateStyle}}/>
            </div>

          </div>
        </div>

      <div style={style.sidebar}>
        <div style={style.topic}>Project</div>

        <div style={style.sidebarContent}>
          <ProjectSelector label='Choose your project here:' style={style.projectSelector}/>
          <AddProject id='newProjectExpander' label='Or click here to add a new one' style={style.moveUp}/>
        </div>

        <div style={style.topic}>Progress</div>

        <div style={style.sidebarContent}>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>1. Do you have a dataset?</b><br/><br/>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>2. Have you computed features?</b><br/>
          <div style={style.circleStyle}>&middot;&middot;&middot;</div><b>3. How about training a model?</b><br/>
        </div>

      </div>

      <div className='mainContent' style={style.main}>

        <Notifications style={style.notifications}/>

      <div style={style.footer}>
          Cesium is an open source Machine Learning Time-Series Platform
          &middot;
          Follow the <a style={style.footer.a} href="http://cesium.ml">Cesium project</a> on <a style={style.footer.a} href="https://github.com/cesium-ml">GitHub</a>
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

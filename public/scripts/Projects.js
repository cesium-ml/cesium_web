import React from 'react'
import { connect } from "react-redux"
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'
import Modal from 'react-modal'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'

import { FormComponent, Form, SelectInput, TextInput, SubmitButton } from './Form'
import {reduxForm} from 'redux-form'
import * as Validate from './validate'
import {AddExpand} from './presentation'
import * as Action from './actions.js'


var ProjectsTab = React.createClass({
  render: function() {
    return (
      <div>
        {/* <Project/> */}
      </div>
    );
  }
});


var NewProjectForm = React.createClass({
  render: function() {
    return (
      <div data-test-name='newProjectForm'>
        <FormTitleRow formTitle='Create a new project'
        />
        <FormInputRow
          inputName='Project Name'
          inputTag='input'
          inputType='text'
          formName='newProject'
          value=""
          handleInputChange={this.props.handleInputChange}
        />
        <FormInputRow
          inputName='Description/notes'
          inputTag='textarea'
          formName='newProject'
          value=""
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


class ProjectForm extends FormComponent {
  render() {
    const {fields: {projectName, projectDescription},
           error, resetForm, submitting, handleSubmit} = this.props;

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Project Name" {...projectName}/>
        <TextInput label="Project Description" {...projectDescription}/>
        <SubmitButton label="Create Project"
                      submitting={submitting} resetForm={resetForm}/>
      </Form>
    )
  }
}

const validate = Validate.createValidator({
  projectName: [Validate.required],
});

ProjectForm = reduxForm({
  form: 'newProject',
  fields: ['projectName', 'projectDescription'],
  validate
})(ProjectForm);


export var AddProject = (props) => (
  <AddExpand label="Add Project">
    <ProjectForm onSubmit={props.addProject}/>
  </AddExpand>
);

let mapDispatchToProps = (dispatch) => {
  return (
    {addProject: (form) => dispatch(Action.addProject(form)),
    }
  );
}

AddProject = connect(null, mapDispatchToProps)(AddProject)


class ProjectSelector extends FormComponent {
  render() {
    const {fields: {modelName, project, featureSet, modelType}, handleSubmit} = this.props;

    let projects = this.props.projects.map(project => (
      {id: project.id,
       label: project.name}
    ));

    let style = {
      form: {
        display: 'block-inline',
      }
    }

    return (
      <div>
        <Form onSubmit={form => null} style={style.form}>
          <SelectInput label="Select Project"
                       options={projects}
                       onChange={this.props.onChange}
                       {...project}/>
        </Form>
      </div>
    );
  }
}

let mapStateToProps = (state) => {
  let projectZero = state.projects[0];
  return {
    projects: state.projects,
    initialValues: {
      project: projectZero ? projectZero.id.toString() : ""
    }
  };
}

ProjectSelector = reduxForm({
  form: 'projectSelector',
  fields: ['project'],
}, mapStateToProps)(ProjectSelector)


export var CurrentProject = (props) => {
  let style = {
    marginBottom: '1em',
    padding: '0.5em'
  }

  let project = props.selectedProject;
  return (
    <div style={style}>
      <b>{project.name}</b><br/>
      {project.description ? <span><em>{project.description}</em><br/></span> : ""}
      <b>id:</b> {project.id}
    </div>
  );
}

//ProjectSelector = connect(mapStateToProps)(ProjectSelector);


export var ProjectList = React.createClass({
  render: function() {
    let projectNodes = this.props.projects.map(project => (
        <ProjectListRow
          project={project}
          key={project.id}
          clickEditProject={this.props.clickEditProject}
          deleteProject={this.props.deleteProject}
          projectDetails={this.props.projectDetails}
          handleInputChange={this.props.handleInputChange}
          updateProjectInfo={this.props.updateProjectInfo}
        />
    ));
    return (
      <div className="projectListDiv" style={{marginTop: 40}}>
        <h3>Existing Projects</h3>
        <div style={{width: 320, float: 'left'}}>
          <b>Name</b>
        </div>
        <div style={{marginLeft: 20, width: 320, float: 'left'}}>
          <b>Date Created</b>
        </div>
        <div style={{marginLeft: 710}}>
          <b>Edit/Delete Project</b>
        </div>
        <div>
          <ReactCSSTransitionGroup
            transitionName="projectsListItems"
            transitionEnterTimeout={200}
            transitionLeaveTimeout={200}>
            {projectNodes}
          </ReactCSSTransitionGroup>
        </div>
      </div>
    );
  }
});


var ProjectListRow = React.createClass({
  render: function() {
    return (
      <div>
        <div style={{width: 320, float: 'left'}}>
          {this.props.project.name}
        </div>
        <div style={{marginLeft: 20, width: 320, float: 'left'}}>
          {this.props.project.created}
        </div>
        <div style={{marginLeft: 710}}>
          <EditProjectForm
            clickEditProject={this.props.clickEditProject}
            project={this.props.project}
            projectDetails={this.props.projectDetails}
            handleInputChange={this.props.handleInputChange}
            handleSubmit={this.props.updateProjectInfo}
          />
          <a href="#" onClick={(e) => (console.log(e))}>
            {/* Glyphicons don't work with npm bootstrap!
            <span style={{marginLeft: 10}}
                className="glyphicon glyphicon-trash"
                title="Delete">
            </span>
            */}
          </a>
        </div>
      </div>
    );
  }
});


const modalStyles = {
  content : {
    top           : '50%',
    left          : '50%',
    right         : 'auto',
    bottom        : 'auto',
    marginRight       : '-50%',
    transform       : 'translate(-50%, -50%)'
  }
};


var EditProjectForm = React.createClass({
  getInitialState: function() {
    return {modalIsOpen: false};
  },
  clickEdit: function() {
    this.props.clickEditProject(this.props.project.id);
    this.openModal();
  },
  submit: function(e) {
    this.props.handleSubmit(e);
    this.closeModal();
  },
  openModal: function() {
    this.setState({modalIsOpen: true});
  },
  afterOpenModal: function() {
    // TODO
  },
  closeModal: function() {
    this.setState({modalIsOpen: false});
  },
  render: function() {
    return (
      <span>
        <a href="#"
           onClick={this.clickEdit}>
          [Edit]
        </a>

        <Modal
          isOpen={this.state.modalIsOpen}
          onAfterOpen={this.afterOpenModal}
          onRequestClose={this.closeModal}
          style={modalStyles} >

          <FormTitleRow formTitle="Edit Project" />
          <FormInputRow inputName="Project Name"
                  inputTag="input"
                  inputType="text"
                  formName="selectedProjectToEdit"
                  value=""
                  handleInputChange={this.props.handleInputChange}
          />
          <FormInputRow inputName="Description/notes"
                  inputTag="input"
                  inputType="text"
                  formName="selectedProjectToEdit"
                  value={this.props.projectDetails["Description/notes"]}
                  handleInputChange={this.props.handleInputChange}
          />
          <div className="submitButtonDiv" style={{marginTop: 15}}>
            <input type="submit"
                 onClick={this.submit}
                 value="Submit"
                 className="submitButton"
            />
          </div>

        </Modal>
      </span>
    );
  }
});


ProjectList = connect(state => {
  return {
    projects: state.projects
  }
})(ProjectList);

export default ProjectsTab;
export { ProjectSelector };

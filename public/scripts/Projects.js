import React from 'react'
import { connect } from "react-redux"
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'
import Modal from 'react-modal'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'

import { FormComponent, Form, SelectInput, TextInput, SubmitButton } from './Form'
import {reduxForm} from 'redux-form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions.js'
import Delete from './Delete'
import {colorScheme as cs} from './colorscheme'


class ProjectForm extends FormComponent {
  render() {
    const {fields: {projectName, projectDescription},
           error, resetForm, submitting, handleSubmit} = this.props;

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Project Name" {...projectName}/>
        <TextInput label="Project Description" {...projectDescription}/>
        <SubmitButton label={this.props.label}
                      submitting={submitting} resetForm={resetForm}/>
      </Form>
    )
  }
}

const validate = Validate.createValidator({
  projectName: [Validate.required],
});

let NewProjectForm = reduxForm({
  form: 'newProject',
  fields: ['projectName', 'projectDescription'],
  validate
})(ProjectForm);

let EditProjectForm = reduxForm({
  form: 'editProject',
  fields: ['projectName', 'projectDescription', 'projectId'],
  validate
})(ProjectForm)


export var ProjectTab = (props) => {
  let p = props.selectedProject;
  let style = {
    marginLeft: '0em',
    paddingLeft: '2em',
  }

  let newCesiumStyle = {
    marginTop: '2em',
    background: 'white',
    width: '20em',
    color: cs.darkBlue,
    padding: '1em',
    height: '100%',
    fontSize: '200%'
  }

  if (!p.id)
    return (
      <div style={newCesiumStyle}>
        <p>Welcome to Cesium!</p>
        <p>🡸 Please create a new project.</p>
     </div>
    )
  else
    return (
      <div style={style}>
        <EditProjectForm
          label="Update"
          onSubmit={props.updateProject}
          initialValues={{projectName: p.name,
                          projectDescription: p.description,
                          projectId: p.id}}
        />

        <DeleteProject ID={props.selectedProject.id} typeName="Project"/>
      </div>
    )
}

let ptMapDispatchToProps = (dispatch) => {
  return {
    updateProject: (form) => dispatch(Action.updateProject(form))
  }
}

ProjectTab = connect(null, ptMapDispatchToProps)(ProjectTab)


export var AddProject = (props) => {
  let expandBoxStyle = {
    zIndex: 1000,
    position: 'relative',
    width: 500,
    WebkitBoxShadow: '0 0 5px black',
    MozBoxShadow: '0 0 5px black',
    boxShadow: '0 0 5px black',
    color: 'black'
  }
  return (
    <Expand id={props.id} label={props.label || "Add Project"}
               expandBoxStyle={expandBoxStyle} style={props.style}>
      <NewProjectForm label="Create Project" onSubmit={props.addProject}/>
    </Expand>
  );
};

let mapDispatchToProps = (dispatch) => {
  return (
    {addProject: (form) => dispatch(Action.addProject(form)),
    }
  );
}

AddProject = connect(null, mapDispatchToProps)(AddProject)


mapDispatchToProps = (dispatch) => {
  return (
    {delete: (id) => dispatch(Action.deleteProject(id))}
  );
}

var DeleteProject = connect(null, mapDispatchToProps)(Delete);

export class ProjectSelector extends FormComponent {
  render() {
    const {fields: {modelName, project, featureSet, modelType}, handleSubmit} = this.props;

    let projects = this.props.projects.map(project => (
      {id: project.id,
       label: project.name}
    ));

    return (
      <div style={this.props.style}>
        <Form onSubmit={form => null}>
          <SelectInput label={this.props.label}
                       options={projects}
                       {...project}/>
        </Form>
      </div>
    );
  }
}

let psMapStateToProps = (state) => {
  let projectZero = state.projects.projectList[0];
  let projectZeroId = projectZero ? projectZero.id.toString() : "";

  let selectedProject = state.form.projectSelector;
  let selectedId = selectedProject ? selectedProject.project.value : "";

  return {
    projects: state.projects.projectList,
    initialValues: {
      project: selectedId || projectZeroId
    }
  };
}

ProjectSelector = reduxForm({
  form: 'projectSelector',
  fields: ['project'],
}, psMapStateToProps)(ProjectSelector)


export var CurrentProject = (props) => {
  let style = {
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

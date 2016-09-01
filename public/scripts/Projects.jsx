import React from 'react';
import { connect } from 'react-redux';
import { reduxForm } from 'redux-form';

import { FormComponent, Form, SelectInput, TextInput, SubmitButton } from './Form';
import * as Validate from './validate';
import Expand from './Expand';
import * as Action from './actions';
import Delete from './Delete';
import { colorScheme as cs } from './colorscheme';


class ProjectForm extends FormComponent {
  render() {
    const { fields: { projectName, projectDescription },
           error, resetForm, submitting, handleSubmit } = this.props;

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Project Name" {...projectName} />
        <TextInput label="Project Description" {...projectDescription} />
        <SubmitButton
          label={this.props.label}
          submitting={submitting} resetForm={resetForm}
        />
      </Form>
    );
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
})(ProjectForm);


export let ProjectTab = (props) => {
  let p = props.selectedProject;
  let style = {
    marginLeft: '0em',
    paddingLeft: '2em',
  };

  let newCesiumStyle = {
    marginTop: '2em',
    background: 'white',
    width: '20em',
    color: cs.darkBlue,
    padding: '1em',
    height: '100%',
    fontSize: '200%'
  };

  if (!p.id) {
    return (
      <div style={newCesiumStyle}>
        <p>Welcome to Cesium!</p>
        <p>🡸 Please create a new project.</p>
      </div>
    );
  } else {
    return (
      <div style={style}>
        <EditProjectForm
          label="Update"
          onSubmit={props.updateProject}
          initialValues={{ projectName: p.name,
                          projectDescription: p.description,
                          projectId: p.id }}
        />

        <DeleteProject ID={p.id} typeName="Project" />
      </div>
    );
  }
};

ProjectTab.propTypes = {
  selectedProject: React.PropTypes.object.isRequired,
  updateProject: React.PropTypes.func.isRequired
};

const ptMapDispatchToProps = (dispatch) => (
  {
    updateProject: (form) => dispatch(Action.updateProject(form))
  }
);

ProjectTab = connect(null, ptMapDispatchToProps)(ProjectTab);


export let AddProject = (props) => {
  let expandBoxStyle = {
    zIndex: 1000,
    position: 'relative',
    width: 500,
    WebkitBoxShadow: '0 0 5px black',
    MozBoxShadow: '0 0 5px black',
    boxShadow: '0 0 5px black',
    color: 'black'
  };
  return (
    <Expand
      id={props.id}
      label={props.label || "Add Project"}
      expandBoxStyle={expandBoxStyle} style={props.style}
    >
      <NewProjectForm label="Create Project" onSubmit={props.addProject} />
    </Expand>
  );
};

AddProject.propTypes = {
  id: React.PropTypes.string.isRequired,
  label: React.PropTypes.string,
  addProject: React.PropTypes.func.isRequired,
  style: React.PropTypes.object
};

let mapDispatchToProps = (dispatch) => (
  {
    addProject: (form) => dispatch(Action.addProject(form)),
  }
);

AddProject = connect(null, mapDispatchToProps)(AddProject);


mapDispatchToProps = (dispatch) => (
  { delete: (id) => dispatch(Action.deleteProject(id)) }
);

let DeleteProject = connect(null, mapDispatchToProps)(Delete);

export let ProjectSelector = (props) => {
  const { fields: { project } } = props;

  let projects = props.projects.map(proj => (
    {
      id: proj.id,
      label: proj.name
    }
  ));

  return (
    <div style={props.style}>
      <Form onSubmit={form => null}>
        <SelectInput
          label={props.label}
          options={projects}
          {...project}
        />
      </Form>
    </div>
  );
};
ProjectSelector.propTypes = {
  fields: React.PropTypes.object.isRequired,
  projects: React.PropTypes.arrayOf(React.PropTypes.object),
  style: React.PropTypes.object,
  label: React.PropTypes.string
};

const psMapStateToProps = (state) => {
  const projectZero = state.projects.projectList[0];
  const projectZeroId = projectZero ? projectZero.id.toString() : '';

  const selectedProject = state.form.projectSelector;
  const selectedId = selectedProject ? selectedProject.project.value : '';

  return {
    projects: state.projects.projectList,
    initialValues: {
      project: selectedId || projectZeroId
    }
  };
};

ProjectSelector = reduxForm({
  form: 'projectSelector',
  fields: ['project'],
}, psMapStateToProps)(ProjectSelector);


export const CurrentProject = (props) => {
  let style = {
  };

  const project = props.selectedProject;
  return (
    <div style={style}>
      <b>{project.name}</b><br />
      {project.description ? <span><em>{project.description}</em><br /></span> : ''}
      <b>id:</b> {project.id}
    </div>
  );
};

CurrentProject.propTypes = {
  selectedProject: React.PropTypes.object
};

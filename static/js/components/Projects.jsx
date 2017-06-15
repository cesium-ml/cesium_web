import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { reduxForm } from 'redux-form';

import { FormComponent, Form, SelectInput, TextInput, SubmitButton } from './Form';
import * as Validate from '../validate';
import Expand from './Expand';
import * as Action from '../actions';
import Delete from './Delete';
import colorScheme from './colorscheme';

const cs = colorScheme;

const ProjectForm = (props) => {
  const { fields: { projectName, projectDescription },
          error, resetForm, submitting, handleSubmit } = props;

  return (
    <Form onSubmit={handleSubmit} error={error}>
      <TextInput label="Project Name" {...projectName} />
      <TextInput label="Project Description (optional)" {...projectDescription} />
      <SubmitButton
        label={props.label}
        submitting={submitting} resetForm={resetForm}
      />
    </Form>
  );
};
ProjectForm.propTypes = {
  fields: React.PropTypes.object.isRequired,
  label: React.PropTypes.string.isRequired,
  error: React.PropTypes.string,
  handleSubmit: React.PropTypes.func.isRequired,
  submitting: React.PropTypes.bool.isRequired,
  resetForm: React.PropTypes.func.isRequired
};

const validate = Validate.createValidator({
  projectName: [Validate.required],
});

const NewProjectForm = reduxForm({
  form: 'newProject',
  fields: ['projectName', 'projectDescription'],
  validate
})(ProjectForm);

const EditProjectForm = reduxForm({
  form: 'editProject',
  fields: ['projectName', 'projectDescription', 'projectId'],
  validate
})(ProjectForm);


let ProjectTab = (props) => {
  const p = props.selectedProject;
  const style = {
    marginLeft: '0em',
    paddingLeft: '2em',
  };

  const newCesiumStyle = {
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
        <p>&larr; Please create a new project.</p>
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
  selectedProject: PropTypes.object.isRequired,
  updateProject: PropTypes.func.isRequired
};

const ptMapDispatchToProps = dispatch => (
  {
    updateProject: form => dispatch(Action.updateProject(form))
  }
);

ProjectTab = connect(null, ptMapDispatchToProps)(ProjectTab);

export { ProjectTab };


let AddProject = (props) => {
  const expandBoxStyle = {
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
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  addProject: PropTypes.func.isRequired,
  style: PropTypes.object
};

let mapDispatchToProps = dispatch => (
  {
    addProject: form => dispatch(Action.addProject(form)),
  }
);

AddProject = connect(null, mapDispatchToProps)(AddProject);

export { AddProject };

mapDispatchToProps = dispatch => (
  { delete: id => dispatch(Action.deleteProject(id)) }
);

const DeleteProject = connect(null, mapDispatchToProps)(Delete);

let ProjectSelector = (props) => {
  const { fields: { project } } = props;

  const projects = props.projects.map(proj => (
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
  fields: PropTypes.object,
  projects: PropTypes.arrayOf(PropTypes.object).isRequired,
  style: PropTypes.object,
  label: PropTypes.string
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

ProjectSelector = connect(psMapStateToProps)(ProjectSelector);

ProjectSelector = reduxForm({
  form: 'projectSelector',
  fields: ['project']
})(ProjectSelector);

export { ProjectSelector };

export const CurrentProject = (props) => {
  const style = {
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
  selectedProject: PropTypes.object
};

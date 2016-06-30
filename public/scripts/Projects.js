import React from 'react'
import { connect } from "react-redux"
import ReactCSSTransitionGroup from 'react-addons-css-transition-group'
import Modal from 'react-modal'
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'


var ProjectsTab = React.createClass({
  render: function() {
    return (
      <div>
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


var ProjectList = React.createClass({
  render: function() {
    console.log("this:", this);
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
            {/* Glyphicons don't work with npm bootstrap!
            <span className="glyphicon glyphicon-edit"
                title="Edit">
            </span>
            */}
          <a href="#" onClick={this.props.deleteProject.bind(null, this.props.project.id)}>
            {/* Glyphicons don't work with npm bootstrap!
            <span style={{marginLeft: 10}}
                className="glyphicon glyphicon-trash"
                title="Delete">
            </span>
            */}
            { " " }[Delete]
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
                  value={this.props.projectDetails["Project Name"]}
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


var mapStateToProps = function(state) {
  return {projects: state.projects};
}

ProjectList = connect(mapStateToProps)(ProjectList)
module.exports = ProjectsTab;

var React = require("react");
var ReactDOM = require("react-dom");
var ReactCSSTransitionGroup = require("react-addons-css-transition-group");
var Modal = require("react-modal");
var FileInput = require("react-file-input");
var ReactTabs = require('react-tabs');
var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;
var $ = require("jquery");
global.jQuery = $;
require("bootstrap-css");
require("bootstrap");

var MainContent = React.createClass({
    getInitialState: function() {
        return {
            forms: {
                newProject: {
                    "Project Name": "",
                    "Description/notes": "",
                },
                newDataset: {
                    "Select Project": "",
                    "Dataset Name": "",
                    "Header File": "",
                    "Tarball Containing Data": ""
                },
                selectedProjectToEdit: {
                    "Description/notes": "",
                    "Project Name": ""
                }
            },
            projectsList: [],
            datasetsList: []
        };
    },
    componentDidMount: function() {
        this.loadState();
    },
    loadState: function() {
        $.ajax({
            url: "/get_state",
            dataType: "json",
            cache: false,
            success: function(data) {
                this.setState({projectsList: data.projectsList,
                               datasetsList: data.datasetsList,
                               modelsList: data.modelsList,
                               featuresetList: data.featuresetList,
                               predictionsList: data.predictionsList
                });
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/get_state", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });
    },
    handleNewProjectSubmit: function(e) {
        e.preventDefault();
        $.ajax({
            url: "/newProject",
            dataType: "json",
            type: "POST",
            data: this.state.forms.newProject,
            success: function(data) {
                var form_state = this.state.forms;
                form_state.newProject = this.getInitialState().forms.newProject;
                this.setState({projectsList: data, forms: form_state});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/newProject", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });
    },
    handleClickEditProject: function(projectID, e) {
        $.ajax({
            url: "/getProjectDetails/" + projectID,
            dataType: "json",
            cache: false,
            success: function(data) {
                data["Project Name"] = data["name"];
                data["Description/notes"] = data["description"];
                data["project_id"] = projectID;
                var form_state = this.state.forms;
                form_state["selectedProjectToEdit"] = data;
                this.setState({forms: form_state});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/getProjectDetails", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });
    },
    updateProjectInfo: function(e) {
        e.preventDefault();
        $.ajax({
            url: "/updateProject",
            dataType: "json",
            type: "POST",
            data: this.state.forms.selectedProjectToEdit,
            success: function(data) {
                var form_state = this.state.forms;
                form_state.selectedProjectToEdit = this.getInitialState().forms.selectedProjectToEdit;
                this.setState({projectsList: data, forms: form_state});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/updateProject", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });
    },
    handleDeleteProject: function(projectID, e) {
        $.ajax({
            url: "/deleteProject",
            dataType: "json",
            type: "POST",
            data: {"project_key": projectID},
            success: function(data) {
                this.setState({projectsList: data});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/deleteProject", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });
    },
    handleNewDatasetSubmit: function(e){
        e.preventDefault();
        var formData = new FormData();
        for (var key in this.state.forms.newDataset) {
            formData.append(key, this.state.forms.newDataset[key]);
        }
        $.ajax({
            url: "/uploadData",
            dataType: "json",
            type: "POST",
            contentType: false,
            processData: false,
            data: formData,
            // data: this.state.forms.newDataset,
            success: function(data) {
                var form_state = this.state.forms;
                form_state.newDataset = this.getInitialState().forms.newDataset;
                this.setState({datasetsList: data.datasetsList, forms: form_state});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error("/uploadData", status, err.toString(),
                              xhr.repsonseText);
            }.bind(this)
        });

        {/*
        $("#datasetForm").ajaxSubmit({
            success: function(response) {
                console.log(response);
            },
            error: function(response) {
                console.log("error");
                console.log(response);
            }
        });
        */}
    },
    handleInputChange: function(inputName, inputType, formName, e) {
        var form_state = this.state.forms;
        if (inputType == "file") {
            var newValue = e.target.files[0];
        } else {
            var newValue = e.target.value;
        }
        form_state[formName][inputName] = newValue;
        this.setState({forms: form_state});
    },
    render: function() {
        return (
            <div className="mainContent">
                <Tabs>
                    <TabList>
                        <Tab>Projects</Tab>
                        <Tab>Data</Tab>
                        <Tab>Features</Tab>
                        <Tab>Models</Tab>
                        <Tab>Predict</Tab>
                    </TabList>
                    <TabPanel>
                        <ProjectsTabContent
                            getInitialState={this.getInitialState}
                            loadState={this.loadState}
                            handleNewProjectSubmit={this.handleNewProjectSubmit}
                            handleClickEditProject={this.handleClickEditProject}
                            handleDeleteProject={this.handleDeleteProject}
                            handleInputChange={this.handleInputChange}
                            formFields={this.state.forms.newProject}
                            projectsList={this.state.projectsList}
                            projectDetails={this.state.forms.selectedProjectToEdit}
                            updateProjectInfo={this.updateProjectInfo}
                        />
                    </TabPanel>
                    <TabPanel>
                        <DatasetsTabContent
                            getInitialState={this.getInitialState}
                            loadState={this.loadState}
                            handleNewDatasetSubmit={this.handleNewDatasetSubmit}
                            handleInputChange={this.handleInputChange}
                            formFields={this.state.forms.newDataset}
                            formName="newDataset"
                            projectsList={this.state.projectsList}
                            datasetsList={this.state.datasetsList}
                        />
                    </TabPanel>
                    <TabPanel>
                        <FeaturesTabContent
                            getInitialState={this.getInitialState}
                            loadState={this.loadState}
                            handleNewDatasetSubmit={this.handleNewDatasetSubmit}
                            handleInputChange={this.handleInputChange}
                            formFields={this.state.forms.newDataset}
                            projectsList={this.state.projectsList}
                            datasetsList={this.state.datasetsList}
                        />
                    </TabPanel>
                    <TabPanel>
                        Models...
                    </TabPanel>
                    <TabPanel>
                        Predictions...
                    </TabPanel>
                </Tabs>
            </div>
        );
    }
});

var ProjectsTabContent = React.createClass({
    render: function() {
        return (
            <div className="projectsTabContent">
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
            <div className="formTableDiv" data-test-name="newProjectForm">
                <FormTitleRow formTitle="Create a new project"
                />
                <FormInputRow inputName="Project Name"
                              inputTag="input"
                              inputType="text"
                              formName="newProject"
                              value={this.props.formFields["Project Name"]}
                              handleInputChange={this.props.handleInputChange}
                />
                <FormInputRow inputName="Description/notes"
                              inputTag="textarea"
                              formName="newProject"
                              value={this.props.formFields["Description/notes"]}
                              handleInputChange={this.props.handleInputChange}
                />
                <div className="submitButtonDiv" style={{marginTop: 15}}>
                    <input type="submit"
                           onClick={this.props.handleSubmit}
                           value="Submit"
                           className="submitButton"
                    />
                </div>
            </div>
        );
    }
});

var ProjectList = React.createClass({
    render: function() {
        var projectNodes = this.props.projectsList.map(function(project) {
            return (
                <ProjectListRow
                    project={project}
                    key={project.id}
                    clickEditProject={this.props.clickEditProject}
                    deleteProject={this.props.deleteProject}
                    projectDetails={this.props.projectDetails}
                    handleInputChange={this.props.handleInputChange}
                    updateProjectInfo={this.props.updateProjectInfo}
                />
            );
        }.bind(this));
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
        top                   : '50%',
        left                  : '50%',
        right                 : 'auto',
        bottom                : 'auto',
        marginRight           : '-50%',
        transform             : 'translate(-50%, -50%)'
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

var FormInputRow = React.createClass({
    render: function() {
        return (
            <div className="formInputRow">
                <div className="formInputTitle"
                     style={{width: 320, float: 'left', marginTop: 5}}>
                    {this.props.inputName}
                </div>
                <div className="formInputField"
                     style={{marginLeft: 340, marginTop: 5}}>
                    <this.props.inputTag
                                 type={this.props.inputType}
                                 value={this.props.value}
                                 onChange={this.props.handleInputChange.bind(
                                         null, this.props.inputName,
                                         this.props.inputType,
                                         this.props.formName)}
                    />
                </div>
            </div>
        );
    }
});

var FormSelectInput = React.createClass({
    render: function() {
        var selectOptions = this.props.projectsList.map(function(project) {
            return (
                <option value={project.id} key={project.id}>
                    {project.name}
                </option>
            );
        }.bind(this));
        return (
            <div className="formInputRow">
                <div className="formInputTitle"
                     style={{width: 320, float: 'left', marginTop: 5}}>
                    {this.props.inputName}
                </div>
                <div className="formInputField"
                     style={{marginLeft: 340, marginTop: 5}}>
                    <select
                        value={this.props.value}
                        onChange={this.props.handleInputChange.bind(
                                null, this.props.inputName,
                                this.props.inputType,
                                this.props.formName)}>
                        {selectOptions}
                    </select>
                </div>
            </div>
        );
    }
});

var FormTitleRow = React.createClass({
    render: function() {
        return (
            <div className="formTitleDiv" style={{marginTop: 30}}>
                <h3>
                    {this.props.formTitle}
                </h3>
            </div>
        );
    }
});

var DatasetsTabContent = React.createClass({
    render: function() {
        return (
            <div className="datasetsTabContent">
                <DatasetsForm
                    handleInputChange={this.props.handleInputChange}
                    formFields={this.props.formFields}
                    handleSubmit={this.props.handleNewDatasetSubmit}
                    datasetsList={this.props.datasetsList}
                    projectsList={this.props.projectsList}
                    formName={this.props.formName}
                />
            </div>
        );
    }
});

var DatasetsForm = React.createClass({
    render: function() {
        return (
            <div className="formTableDiv">
                <form id="datasetForm" name="datasetForm"
                      action="/uploadData" enctype="multipart/form-data"
                      method="post">
                    <FormTitleRow formTitle="Upload new time series data"/>
                    <FormSelectInput inputName="Select Project"
                                     inputTag="select"
                                     formName="newDataset"
                                     projectsList={this.props.projectsList}
                                     value={this.props.formFields["Select Project"]}
                                     handleInputChange={this.props.handleInputChange}
                    />
                    <FormInputRow inputName="Dataset Name"
                                  inputTag="input"
                                  inputType="text"
                                  formName="newDataset"
                                  value={this.props.formFields["Dataset Name"]}
                                  handleInputChange={this.props.handleInputChange}
                    />
                    <FileInput name="Header File"
                               placeholder="Select Header File"
                               onChange={this.props.handleInputChange.bind(
                                        null, "Header File", "file", "newDataset")}
                    />
                    <FileInput name="Tarball Containing Data"
                               placeholder="Select Data Tarball"
                               onChange={this.props.handleInputChange.bind(
                                       null, "Tarball Containing Data", "file", "newDataset")}
                    />
                    <div className="submitButtonDiv" style={{marginTop: 15}}>
                        <input type="submit"
                               onClick={this.props.handleSubmit}
                               value="Submit"
                               className="submitButton"
                        />
                    </div>
                </form>
            </div>
        );
    }
});

var FeaturesTabContent = React.createClass({
    render: function() {
        return (
            <div className="featuresTabContent">
                <FeaturizeForm
                    handleInputChange={this.props.handleInputChange}
                    formFields={this.props.formFields}
                    handleSubmit={this.props.handleNewDatasetSubmit}
                    datasetsList={this.props.datasetsList}
                    featuresetsList={this.props.featuresetsList}
                    projectsList={this.props.projectsList}
                    formName={this.props.formName}
                />
            </div>
        );
    }
});

var FeaturizeForm = React.createClass({
    render: function() {
        return (
            <div className="formTableDiv">
                <form id="featurizeForm" name="featurizeForm"
                      action="/FeaturizeData" enctype="multipart/form-data"
                      method="post">
                    <FormTitleRow formTitle="Featurize Data"/>
                    <FormSelectInput inputName="Select Project"
                                     inputTag="select"
                                     formName="featurize"
                                     projectsList={this.props.projectsList}
                                     value={this.props.formFields["Select Project"]}
                                     handleInputChange={this.props.handleInputChange}
                    />
                    <FormSelectInput inputName="Select Dataset"
                                     inputTag="select"
                                     formName="featurize"
                                     projectsList={this.props.projectsList}
                                     value={this.props.formFields["Select Dataset"]}
                                     handleInputChange={this.props.handleInputChange}
                    />
                    <FormInputRow inputName="Feature Set Title"
                                  inputTag="input"
                                  inputType="text"
                                  formName="featurize"
                                  value={this.props.formFields["Dataset Name"]}
                                  handleInputChange={this.props.handleInputChange}
                    />


                    // TODO: FEATURE SELECTION DIALOG!!


                    <div className="submitButtonDiv" style={{marginTop: 15}}>
                        <input type="submit"
                               onClick={this.props.handleSubmit}
                               value="Submit"
                               className="submitButton"
                        />
                    </div>
                </form>
            </div>
        );
    }
});

ReactDOM.render(
    <MainContent />,
    document.getElementById('content')
);

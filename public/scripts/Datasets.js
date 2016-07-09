import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'

import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
//import FileInput from 'react-file-input'

import {FormComponent, Form, TextInput, FileInput, SubmitButton } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'


var DatasetsTab = (props) => {
  return (
    <div className='datasetsTab'>

      <Expand label="Upload new dataset" id='newDatasetExpander'>
        <DatasetForm selectedProject={props.selectedProject}/>
      </Expand>

      <DatasetTable selectedProject={props.selectedProject}/>

    </div>
  )
}

class DatasetForm extends FormComponent {
  render() {
    const {fields: {datasetName, headerFile, tarFile},
           error, handleSubmit} = this.props;

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Dataset Name" {...datasetName}/>
        <FileInput label="Header File" {...headerFile}/>
        <FileInput label="Data Tarball" {...tarFile}/>
        <SubmitButton label="Upload Dataset"/>
      </Form>
    )
  }
}

let dsMapStateToProps = (state, ownProps) => {
  return {
    initialValues: {
      ...(ownProps.initialValues),
      projectID: ownProps.selectedProject.id
    }
  }
}

let dsMapDispatchToProps = (dispatch) => {
  return {
    onSubmit: form => dispatch(Action.uploadDataset(form))
  }
}

const validate = Validate.createValidator({
  datasetName: [Validate.required],
  tarFile: [Validate.oneFile],
});

DatasetForm = reduxForm({
  form: 'newDataset',
  fields: ['datasetName', 'headerFile', 'tarFile', 'projectID'],
  validate
}, dsMapStateToProps, dsMapDispatchToProps)(DatasetForm);


export var DatasetTable = (props) => {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th><th>Created</th><th>Debug (TODO remove)</th>
    </tr>


    {props.datasets.map(dataset => (
      <tr key={dataset.id}>
        <td>{dataset.name}</td>
        <td>{dataset.created}</td>
        <td>Project: {dataset.project}</td>
      </tr>
    ))}

      </thead>
    </table>
  );
}


function mapStateToProps(state, ownProps) {
  return {
    datasets: state.datasets.filter(
      dataset => {
        return (dataset.project == ownProps.selectedProject.id);
      }
    )
  }
}

DatasetTable = connect(mapStateToProps)(DatasetTable);

module.exports = DatasetsTab;

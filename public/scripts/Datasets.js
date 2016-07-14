import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'

import {FormComponent, Form, TextInput, FileInput, SubmitButton } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import {reformatDatetime} from './utils'


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

    let description = {
      fontStyle: 'italic',
      paddingBottom: '1em'
    }

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Dataset Name" {...datasetName}/>
        <FileInput label="Header File" {...headerFile}/>

        <div style={description}>
          Format: comma-separated with columns "filename" (of a time series from the uploaded archive), "target" (class label or regression target), and any metafeatures (floating point values).
        </div>

        <FileInput label="Data Tarball" {...tarFile}/>
        <div style={description}>
          Format: zipfile or tarfile containing time series files, each of which is comma-separated with columns "time", "value", "error" (optional).
        </div>

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
          <th>Name</th><th>Uploaded</th><th>Actions</th>
    </tr>


    {props.datasets.map(dataset => (
      <tr key={dataset.id}>
        <td>{dataset.name}</td>
        <td>{reformatDatetime(dataset.created)}</td>
        <td><DeleteDataset datasetID={dataset.id}/></td>
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


export var DeleteDataset = (props) => {
  let style = {
    display: 'inline-block'
  }
  return (
    <a style={style} onClick={() => {
      props.dispatch(Action.deleteDataset(props.datasetID))
    }}>Delete</a>
  )
}

DeleteDataset = connect()(DeleteDataset)

module.exports = DatasetsTab;

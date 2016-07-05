import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'

import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
//import FileInput from 'react-file-input'

import {FormComponent, Form, TextInput, FileInput, SubmitButton } from './Form'
import * as Validate from './validate'
import {AddExpand} from './presentation'

var DatasetsTab = React.createClass({
  render: function() {
    return (
      <div className='datasetsTab'>

      <AddExpand label="Upload new dataset">
        <DatasetForm onSubmit={(x) => {console.log(x)}}/>
      </AddExpand>

      <DatasetTable selectedProject={this.props.selectedProject}/>

      </div>
    );
  }
});

class DatasetForm extends FormComponent {
  render() {
    const {fields: {datasetName, headerFile, tarFile}, handleSubmit} = this.props;

    return (
      <Form onSubmit={handleSubmit}>
        <TextInput label="Dataset Name" {...datasetName}/>
        <FileInput label="Header File" {...headerFile}/>
        <FileInput label="Data Tarball" {...tarFile}/>
        <SubmitButton label="Upload Dataset"/>
      </Form>
    )
  }
}

const validate = Validate.createValidator({
  datasetName: [Validate.required],
  headerFile: [Validate.oneFile],
  tarFile: [Validate.oneFile]
});

DatasetForm = reduxForm({
  form: 'newDataset',
  fields: ['datasetName', 'headerFile', 'tarFile'],
  validate
})(DatasetForm);


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


/* var DatasetsForm = React.createClass({
 *   render: function() {
 *     return (
 *       <div>
 *         <form id='datasetForm' name='datasetForm'
 *               action='/uploadData' enctype='multipart/form-data'
 *               method='post'>
 *           <FormTitleRow formTitle='Upload new time series data'/>
 *           <FormSelectInput
 *               inputName='Select Project'
 *               inputTag='select'
 *               formName='newDataset'
 *               optionsList={this.props.projects}
 *               value={this.props.formFields['Select Project']}
 *               handleInputChange={this.props.handleInputChange}
 *           />
 *           <FormInputRow inputName='Dataset Name'
 *                         inputTag='input'
 *                         inputType='text'
 *                         formName='newDataset'
 *                         value={this.props.formFields['Dataset Name']}
 *                         handleInputChange={this.props.handleInputChange}
 *           />
 *           <FileInput name='Header File'
 *                      placeholder='Select Header File'
 *                      onChange={this.props.handleInputChange.bind(
 *                          null, 'Header File', 'file', 'newDataset')}
 *           />
 *           <FileInput name='Tarball Containing Data'
 *                      placeholder='Select Data Tarball'
 *                      onChange={this.props.handleInputChange.bind(
 *                          null, 'Tarball Containing Data', 'file', 'newDataset')}
 *           />
 *           <div className='submitButtonDiv' style={{marginTop: 15}}>
 *             <input type='submit'
 *                    onClick={this.props.handleSubmit}
 *                    value='Submit'
 *                    className='submitButton'
 *             />
 *           </div>
 *         </form>
 *       </div>
 *     );
 *   }
 * });
 * */

module.exports = DatasetsTab;

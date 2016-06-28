import React from 'react'
import { connect } from "react-redux"
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
import FileInput from 'react-file-input'


var DatasetsTab = React.createClass({
  render: function() {
    return (
      <div className='datasetsTab'>
        <DatasetsForm
            handleInputChange={this.props.handleInputChange}
            formFields={this.props.formFields}
            handleSubmit={this.props.handleNewDatasetSubmit}
            datasetsList={this.props.datasetsList}
            projectsList={this.props.projects}
            formName={this.props.formName}
        />
      </div>
    );
  }
});


var DatasetsForm = React.createClass({
  render: function() {
    return (
      <div className='formTableDiv'>
      <form id='datasetForm' name='datasetForm'
      action='/uploadData' enctype='multipart/form-data'
      method='post'>
      <FormTitleRow formTitle='Upload new time series data'/>
      <FormSelectInput
      inputName='Select Project'
      inputTag='select'
      formName='newDataset'
      optionsList={this.props.projectsList}
      value={this.props.formFields['Select Project']}
      handleInputChange={this.props.handleInputChange}
      />
      <FormInputRow inputName='Dataset Name'
      inputTag='input'
      inputType='text'
      formName='newDataset'
      value={this.props.formFields['Dataset Name']}
      handleInputChange={this.props.handleInputChange}
      />
      <FileInput name='Header File'
      placeholder='Select Header File'
      onChange={this.props.handleInputChange.bind(
        null, 'Header File', 'file', 'newDataset')}
      />
      <FileInput name='Tarball Containing Data'
      placeholder='Select Data Tarball'
      onChange={this.props.handleInputChange.bind(
        null, 'Tarball Containing Data', 'file', 'newDataset')}
      />
      <div className='submitButtonDiv' style={{marginTop: 15}}>
      <input type='submit'
      onClick={this.props.handleSubmit}
      value='Submit'
      className='submitButton'
      />
      </div>
      </form>
      </div>
    );
  }
});


var mapStateToProps = function(state) {
  return {projects: state.projects};
}


module.exports = connect(mapStateToProps, null, null, { pure: false })(DatasetsTab);

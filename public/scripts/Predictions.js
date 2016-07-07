import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'

class PredictForm extends FormComponent {
  render() {
    const {fields: {modelID, datasetID}, handleSubmit, resetForm, error} = this.props;

    return (
      <div>
        <Form onSubmit={handleSubmit} error={error}>
          <SelectInput label="Select Model"
                       key={this.props.selectedProject.id + "modelID"}
                       options={this.props.models}
                       {...modelID}/>
          <SelectInput label="Select Data Set"
                       key={this.props.selectedProject.id + "datasetID"}
                       options={this.props.datasets}
                       {...datasetID}/>
          <SubmitButton label="Predict"
                        submitting={submitting}
                        resetForm={resetForm}/>
        </Form>
      </div>
    )
  }
}

let mapStateToProps = (state, ownProps) => {
  let filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project == ownProps.selectedProject.id))
  let zerothDataset = filteredDatasets[0]

  let filteredModels = state.models.filter(model =>
    (model.project == ownProps.selectedProject.id))
  let zerothModel = filteredModels[0]
  return {
    datasets: filteredDatasets,
    models: filteredModels,
    fields: ['modelID', 'datasetID'],
    initialValues: {modelID: zerothModel ? zerothModel.id : '',
                    datasetID: zerothDataset ? zerothDataset.id : ''}
  }
}

PredictForm = reduxForm({
  form: 'predict',
  fields: ['']
}, mapStateToProps)(PredictForm);

var PredictTab = (props) {
  return (
    <div>
      <AddExpand label="Predict Targets" id="predictFormExpander">
        <PredictForm onSubmit={props.predict}
                     selectedProject={props.selectedProject}/>
      </AddExpand>
    </div>
  );
}

let mapDispatchToProps = (dispatch) => {
  return {
    predict: (form) => dispatch(Action.predict(form))
  }
}

PredictTab = connect(null, matchDispatchToProps)(PredictTab)

module.exports = PredictTab;

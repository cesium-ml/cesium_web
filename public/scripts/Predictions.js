import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'
import {AddExpand} from './presentation'
import * as Action from './actions'

class PredictForm extends FormComponent {
  render() {
    const {fields: {modelID, datasetID}, handleSubmit, submitting, resetForm,
           error} = this.props;
    let datasets = this.props.datasets.map(ds => (
      {id: ds.id,
       label: ds.name}
    ));

    let models = this.props.models.map(model => (
      {id: model.id,
       label: model.name}
    ));

    return (
      <div>
        <Form onSubmit={handleSubmit} error={error}>
          <SelectInput label="Select Model"
                       key={this.props.selectedProject.id + "modelID"}
                       options={models}
                       {...modelID}/>
          <SelectInput label="Select Data Set"
                       key={this.props.selectedProject.id + "datasetID"}
                       options={datasets}
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
    (dataset.project == ownProps.selectedProject.id));
  let zerothDataset = filteredDatasets[0];

  let filteredModels = state.models.filter(model =>
    (model.project == ownProps.selectedProject.id));
  let zerothModel = filteredModels[0];

  return {
    datasets: filteredDatasets,
    models: filteredModels,
    fields: ['modelID', 'datasetID'],
    initialValues: {modelID: zerothModel ? zerothModel.id.toString() : '',
                    datasetID: zerothDataset ? zerothDataset.id.toString() : ''}
  }
}

PredictForm = reduxForm({
  form: 'predict',
  fields: ['']
}, mapStateToProps)(PredictForm);

var PredictTab = (props) => {
  return (
    <div>
      <AddExpand label="Predict Targets" id="predictFormExpander">
        <PredictForm onSubmit={props.doPrediction}
                     selectedProject={props.selectedProject}/>
      </AddExpand>
    </div>
  );
}

let mapDispatchToProps = (dispatch) => {
  return {
    doPrediction: (form) => dispatch(Action.doPrediction(form))
  }
}

PredictTab = connect(null, mapDispatchToProps)(PredictTab)

module.exports = PredictTab;

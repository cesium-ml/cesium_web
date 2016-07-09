import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import {plot_example} from './example_plot'


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
    initialValues: {modelID: zerothModel ? zerothModel.id : '',
                    datasetID: zerothDataset ? zerothDataset.id : ''}
  }
}

const validate = Validate.createValidator({
  modelID: [Validate.required],
  datasetID: [Validate.required],
});


PredictForm = reduxForm({
  form: 'predict',
  fields: [''],
  validate
}, mapStateToProps)(PredictForm);


export var PredictionsTable = (props) => {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th><th>Created</th><th>Debug</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>

        {props.predictions.map(prediction => (
           <tr key={prediction.id}>
             <td>{prediction.name}</td>
             <td>{prediction.created}</td>
             <td>Project: {prediction.project}</td>
             <td><DeletePrediction predictionID={prediction.id}/></td>
           </tr>
         ))}

      </tbody>
    </table>
  )
}


let ptMapStateToProps = (state, ownProps) => {
  let filteredPredictions = state.predictions.filter(pred =>
    (pred.project == ownProps.selectedProject.id));
  return {
    predictions: filteredPredictions
  }
}


PredictionsTable = connect(ptMapStateToProps)(PredictionsTable);

export var DeletePrediction = (props) => {
  let style = {
    display: 'inline-block'
  }
  return (
    <a style={style} onClick={() => props.deletePrediction(props.predictionID)}>Delete</a>
  )
}

let dpMapDispatchToProps = (dispatch) => {
  return (
    {deletePrediction: (id) => dispatch(Action.deletePrediction(id))}
  );
}

DeletePrediction = connect(null, dpMapDispatchToProps)(DeletePrediction);


class PredictTab extends Component {
  render() {
    let props = this.props;

    return (
      <div>
        <Expand label="Predict Targets" id="predictFormExpander">
          <PredictForm onSubmit={props.doPrediction}
                       selectedProject={props.selectedProject}/>
        </Expand>
        <PredictionsTable selectedProject={props.selectedProject}/>
        <div id='plotly-div'></div>
      </div>
    );
  }
  componentDidMount() {
    plot_example();
  }
}


let mapDispatchToProps = (dispatch) => {
  return {
    doPrediction: (form) => dispatch(Action.doPrediction(form))
  }
}


PredictTab = connect(null, mapDispatchToProps)(PredictTab)


module.exports = PredictTab;

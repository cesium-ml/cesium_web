import React, { Component, PropTypes } from 'react'
import $ from 'jquery'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import {plot_example} from './example_plot'
import {objectType} from './utils'


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
          <th>Data Set Name</th><th>Model Name</th><th>Created</th><th>Debug</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>

        {props.predictions.map(prediction => (
           [
             <tr key={prediction.id}
                 onClick={() => $("predResultsDiv" + prediction.id).toggle()}>
               <td>{prediction.model_name}</td>
               <td>{prediction.dataset_name}</td>
               <td>{prediction.created}</td>
               <td>Project: {prediction.project}</td>
               <td><DeletePrediction predictionID={prediction.id}/></td>
             </tr>,
             <tr key={prediction.id + 'results'}>
               <td colspan="42">
                 <PredictionResults prediction={prediction} />
               </td>
             </tr>
           ]
        ))}

      </tbody>
    </table>
  )
}


let PredictionResults = (props) => {
  console.log(props);
  let defaultHiddenStyle = {display: 'inline-block'}; {/* default to 'none' */}
  let modelType = props.prediction.model_type;
  let results = props.prediction.results;
  let firstResult = results ? results[Object.keys(results)[0]] : null;

  return (
    <div id={"predResultsDiv" + props.prediction.id} style={defaultHiddenStyle}>
      <table className='table'>
        <thead>
          <tr>
            <th>Time Series</th>
            {[
              (() => {
                if(firstResult && firstResult.target)
                  return (<th>True Class/Target</th>);
              })(),
              (() => {
                switch (modelType) {
                  case "RandomForestClassifier":
                  case "RFC":
                  case "LinearSGDClassifier":
                  case "":
                    return Object.keys(firstResult.prediction).map(classLabel => (
                      [<th>Predicted Class</th>,<th>Probability</th>]
                    ));
                  case "RidgeClassifierCV":
                    return (<th>Predicted Class</th>);
                  case "RandomForestRegressor":
                  case "LinearRegressor":
                  case "BayesianARDRegressor":
                  case "BayesianRidgeRegressor":
                    return (<th>Predicted Target</th>);
                }})()
            ]}
          </tr>
        </thead>
        <tbody>
          {
            Object.keys(results).map(fname => (
              <tr><td>{fname}</td>
                {[
                (() => {
                  if (firstResult && firstResult.target)
                    return (<td>{firstResult.target}</td>);
                })(),
                (() => {
                  switch (modelType) {
                    case "RandomForestClassifier":
                    case "RFC":
                    case "LinearSGDClassifier":
                    case "":
                      return Object.keys(firstResult.prediction).map(classLabel => (
                        [<td>{classLabel}</td>,<td>{firstResult.prediction[classLabel]}</td>]
                      ));
                    case "RidgeClassifierCV":
                      return (<td>{firstResult.prediction}</td>);
                    case "RandomForestRegressor":
                    case "LinearRegressor":
                    case "BayesianARDRegressor":
                    case "BayesianRidgeRegressor":
                      return (<td>{firstResult.prediction}</td>);
                  }})()
                ]}
              </tr>))
          }
        </tbody>
      </table>
    </div>
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

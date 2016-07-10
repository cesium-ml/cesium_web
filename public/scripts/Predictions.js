import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import {plot_example} from './example_plot'
import {objectType} from './utils'
import FoldableRow from './FoldableRow'


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
    <table>
      <thead>
        <tr>
          <th style={{width: '10em'}}>Data Set Name</th>
          <th style={{width: '10em'}}>Model Name</th>
          <th style={{width: '5em'}}>Created</th>
          <th style={{width: '5em'}}>Debug</th>
          <th style={{width: '5em'}}>Actions</th>
        </tr>
      </thead>

      {props.predictions.map((prediction, idx) => (
         <FoldableRow key={idx}>
             <tr key={'row' + idx}>
               <td style={{textDecoration: 'underline'}}>{prediction.model_name}</td>
               <td>{prediction.dataset_name}</td>
               <td>{prediction.created}</td>
               <td>Project: {prediction.project}</td>
               <td><DeletePrediction predictionID={prediction.id}/></td>
             </tr>
             <tr key={'pred' + idx}>
               <td colSpan={10}>
                 <PredictionResults prediction={prediction} />
               </td>
            </tr>
        </FoldableRow>
      ))}

    </table>
  )
}


let PredictionResults = (props) => {
  let defaultHiddenStyle = {display: 'inline-block'}; {/* default to 'none' */}
  let modelType = props.prediction.model_type;
  let results = props.prediction.results;
  let firstResult = results ? results[Object.keys(results)[0]] : null;

  return (
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
                     return Object.keys(firstResult.prediction).map((classLabel, idx) => (
                       [<th key={'pred' + idx}>Predicted Class</th>,<th key={'prob' + idx}>Probability</th>]
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
            Object.keys(results).map((fname, idx) => (
              <tr key={idx}><td>{fname}</td>
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
                      return Object.keys(firstResult.prediction).map((classLabel, idx2) => (
                        [<td key={'class' + idx2}>{classLabel}</td>,<td key={'result' + idx2}>{firstResult.prediction[classLabel]}</td>]
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
        <br/>
        <PredictionsTable selectedProject={props.selectedProject}/>
        <br/>
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

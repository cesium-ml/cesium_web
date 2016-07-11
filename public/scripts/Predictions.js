import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton,
         Form, Button } from './Form'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import {plot_example} from './example_plot'
import {objectType, contains} from './utils'
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
    <table className="table">
      <thead>
        <tr>
          <th style={{width: '15em'}}>Data Set Name</th>
          <th style={{width: '15em'}}>Model Name</th>
          <th style={{width: '20em'}}>Created</th>
          <th style={{width: '10em'}}>Debug</th>
          <th style={{width: '15em'}}>Actions</th>
          <th style={{width: 'auto'}}></th>{ /* extra column, used to capture expanded space */ }
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
               <td></td>
             </tr>
             <tr key={'pred' + idx}>
               <td colSpan={6}>
                 <PredictionResults prediction={prediction} />
               </td>
            </tr>
        </FoldableRow>
      ))}

    </table>
  )
}


let PredictionResults = (props) => {
  let modelType = props.prediction.model_type;
  let results = props.prediction.results;

  let firstResult = results ? results[Object.keys(results)[0]] : null;
  let classes = Object.keys(firstResult.prediction)

  let modelHasProba = contains(['RandomForestClassifier',
                                'LinearSGDClassifier'],
                               modelType)
  let modelHasTarget = contains(['RandomForestRegressor',
                                 'LinearRegressor',
                                 'BayesianARDRegressor',
                                 'BayesianRidgeRegressor'],
                                modelType)
  let modelHasClass = contains(['RidgeClassifierCV'], modelType)

  let hasTrueTargetLabel = (p) => (p.target != null)

  return (
    <table className='table'>
      <thead>
        <tr>
          <th>Time Series</th>
          {hasTrueTargetLabel(firstResult) && <th>True Class/Target</th>}

          {modelHasProba &&
           classes.map((classLabel, idx) => ([
             <th key="0">Predicted Class</th>,
             <th key="1">Probability</th>
           ]))
          }

          {modelHasClass && <th>Predicted Class</th>}
          {modelHasTarget && <th>Predicted Target</th>}
        </tr>
      </thead>

      <tbody>
      {Object.keys(results).map((fname, idx) => {
        let result = results[fname]

        return (
          <tr key={idx}>

            <td>{fname}</td>

            {[hasTrueTargetLabel(result) &&
              <td key="pt">{result.target}</td>,

              modelHasProba &&
              classes.map((classLabel, idx) => ([
                <td key="cl0">{classLabel}</td>,
                <td key="cl1">{result.prediction[classLabel]}</td>
              ])),

              modelHasClass && <td key="rp">{result.prediction}</td>,

              modelHasTarget && <td key="rp">{result.prediction}</td>
            ]}

          </tr>
        )})}
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

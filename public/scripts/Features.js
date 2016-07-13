import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'
import { FormInputRow, FormSelectInput, SelectInput, FormTitleRow,
         FormComponent, Form, TextInput, TextareaInput, FileInput, SubmitButton,
         CheckBoxInput } from './Form'
//import FileInput from 'react-file-input'
import ReactTabs from 'react-tabs'
import CheckboxGroup from 'react-checkbox-group'
import _ from 'underscore'
import filter from 'filter-values'
import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'

var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;


class FeaturizeForm extends FormComponent {
  render() {
    const {fields, fields: {datasetID, featuresetName, customFeatsCode, isTest},
           handleSubmit, submitting, resetForm, error, checkUncheckAll} = this.props;
    let datasets = this.props.datasets.map(ds => (
      {id: ds.id,
       label: ds.name}
    ));

    return (
      <div>
        <Form onSubmit={handleSubmit} error={error}>
          <SubmitButton label="Compute Selected Features"
                        submiting={submitting}
                        resetForm={resetForm}/>
          <TextInput label="Feature Set Name" {...featuresetName}/>
          <SelectInput label="Select Dataset to Featurize"
                       key={this.props.selectedProject.id}
                       options={datasets}
                       {...datasetID}/>
          <b>Select Features to Compute</b>
          <Tabs>
            <TabList>
              <Tab>Observation Features</Tab>
              <Tab>Science Features</Tab>
              <Tab>Custom Features</Tab>
            </TabList>
            <TabPanel>
              <a href="#" onClick={() => {checkUncheckAll("obs_")}}>Check/Uncheck All</a>
              <ul>
                {this.props.features.obs_features.map(feature => (
                   <CheckBoxInput key={'obs_' + feature} label={feature}
                                  {...fields['obs_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <a href="#" onClick={() => {checkUncheckAll("sci_")}}>Check/Uncheck All</a>
              <ul>
                {this.props.features.sci_features.map(feature => (
                   <CheckBoxInput key={'sci_' + feature} label={feature}
                                  {...fields['sci_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <TextareaInput label="Enter Python code defining custom features"
                             rows="10" cols="50" {...customFeatsCode}/>
            </TabPanel>
          </Tabs>
        </Form>
      </div>
    )
  }
}

let mapStateToProps = (state, ownProps) => {
  let obs_features = state.featuresets.features.obs_features;
  let sci_features = state.featuresets.features.sci_features;
  let obs_fields = obs_features.map(f => 'obs_' + f)
  let sci_fields = sci_features.map(f => 'sci_' + f)

  let initialValues = {}
  obs_fields.map((f, idx) => initialValues[f] = true)
  sci_fields.map((f, idx) => initialValues[f] = true)

  let filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project == ownProps.selectedProject.id))
  let zerothDataset = filteredDatasets[0]

  return {
    features: state.featuresets.features,
    datasets: filteredDatasets,
    fields: obs_fields.concat(sci_fields).concat(['datasetID', 'featuresetName',
                                                  'customFeatsCode']),
    initialValues: {...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                    customFeatsCode: ""}
  }
}

let ffMapDispatchToProps = (dispatch) => {
  return {
    checkUncheckAll: (prefix) => dispatch(Action.checkUncheckAll(prefix))
  }
}

const validate = Validate.createValidator({
  datasetID: [Validate.required],
  featuresetName: [Validate.required]
});

FeaturizeForm = reduxForm({
  form: 'featurize',
  fields: ['']
}, mapStateToProps, ffMapDispatchToProps)(FeaturizeForm);


var FeaturesTab = (props) => {
    return (
      <div>
        <div>
          <Expand label="Compute New Features" id="featsetFormExpander">
            <FeaturizeForm onSubmit={props.computeFeatures}
                           selectedProject={props.selectedProject}/>
          </Expand>
        </div>

        <FeatureTable selectedProject={props.selectedProject}/>

      </div>
    );
};

let ftMapDispatchToProps = (dispatch) => {
  return {
    computeFeatures: (form) => dispatch(Action.computeFeatures(form))
  }
}

FeaturesTab = connect(null, ftMapDispatchToProps)(FeaturesTab)

export var FeatureTable = (props) => {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th><th>Created</th><th>Debug</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>

        {props.featuresets.map(featureset => (
           <tr key={featureset.id}>
             <td>{featureset.name}</td>
             <td>{featureset.created}</td>
             <td>Project: {featureset.project}</td>
             <td><DeleteFeatureset featuresetID={featureset.id}/></td>
           </tr>
         ))}

      </tbody>
    </table>
  );
}


let ftMapStateToProps = (state, ownProps) => {
  return {
    featuresets: state.featuresets.featuresetList.filter(
      fs => (fs.project == ownProps.selectedProject.id)
    )
  }
}

FeatureTable = connect(ftMapStateToProps)(FeatureTable)


export var DeleteFeatureset = (props) => {
  let style = {
    display: 'inline-block'
  }
  return (
    <a style={style} onClick={() => {
      props.dispatch(Action.deleteFeatureset(props.featuresetID))
    }}>Delete</a>
  )
}

module.exports = FeaturesTab;

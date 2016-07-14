import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'
import { FormComponent, Form, TextInput, TextareaInput, FileInput, SubmitButton,
         CheckBoxInput, SelectInput } from './Form'
import ReactTabs from 'react-tabs'

import * as Validate from './validate'
import Expand from './Expand'
import * as Action from './actions'
import Plot from './Plot'
import FoldableRow from './FoldableRow'
import {reformatDatetime} from './utils'

var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;


class FeaturizeForm extends FormComponent {
  render() {
    const {fields, fields: {datasetID, featuresetName, customFeatsCode, isTest},
           handleSubmit, submitting, resetForm, error, groupToggleCheckedFeatures} = this.props;
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
              <Tab>Cadence/Error</Tab>
              <Tab>General</Tab>
              <Tab>Lomb Scargle (Periodic)</Tab>
              <Tab>Custom Features</Tab>
            </TabList>
            <TabPanel>
              <a href="#" onClick={() => {groupToggleCheckedFeatures("obs_")}}>Check/Uncheck All</a>
              <ul>
                {this.props.features.obs_features.map(feature => (
                   <CheckBoxInput key={'obs_' + feature} label={feature}
                                  {...fields['obs_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <a href="#" onClick={() => {groupToggleCheckedFeatures("sci_")}}>Check/Uncheck All</a>
              <ul>
                {this.props.features.sci_features.map(feature => (
                   <CheckBoxInput key={'sci_' + feature} label={feature}
                                  {...fields['sci_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <a href="#" onClick={() => {groupToggleCheckedFeatures("lmb_")}}>Check/Uncheck All</a>
              <ul>
                {this.props.features.lmb_features.map(feature => (
                   <CheckBoxInput key={'lmb_' + feature} label={feature}
                                  {...fields['lmb_' + feature]}/>
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
  let lmb_features = state.featuresets.features.lmb_features;
  let obs_fields = obs_features.map(f => 'obs_' + f)
  let sci_fields = sci_features.map(f => 'sci_' + f)
  let lmb_fields = lmb_features.map(f => 'lmb_' + f)

  let initialValues = {}
  obs_fields.map((f, idx) => initialValues[f] = true)
  sci_fields.map((f, idx) => initialValues[f] = true)
  lmb_fields.map((f, idx) => initialValues[f] = true)

  let filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project == ownProps.selectedProject.id))
  let zerothDataset = filteredDatasets[0]

  return {
    features: state.featuresets.features,
    datasets: filteredDatasets,
    fields: obs_fields.concat(sci_fields).concat(lmb_fields).concat(
      ['datasetID', 'featuresetName', 'customFeatsCode']),
    initialValues: {...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                    customFeatsCode: ""}
  }
}

let ffMapDispatchToProps = (dispatch) => {
  return {
    groupToggleCheckedFeatures: (prefix) => dispatch(Action.groupToggleCheckedFeatures(prefix))
  }
}

const validate = Validate.createValidator({
  datasetID: [Validate.required],
  featuresetName: [Validate.required]
});

FeaturizeForm = reduxForm({
  form: 'featurize',
  fields: [''],
  validate: validate
}, mapStateToProps, ffMapDispatchToProps)(FeaturizeForm);


var FeaturesTab = (props) => {
  let {featurePlotURL} = props;
  return (
    <div>
      <div>
        <Expand label="Compute New Features" id="featsetFormExpander">
          <FeaturizeForm onSubmit={props.computeFeatures}
                         selectedProject={props.selectedProject}/>
        </Expand>
      </div>

      <FeatureTable selectedProject={props.selectedProject}
                    featurePlotURL={featurePlotURL}
      />

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
    <div>
      <table className="table">
        <thead>
          <tr>
            <th style={{width: '15em'}}>Name</th>
            <th style={{width: '15em'}}>Created</th>
            <th style={{width: '15em'}}>Status</th>
            <th style={{width: '15em'}}>Actions</th>
            <th style={{width: 'auto'}}></th>{ /* extra column for spacing */ }
          </tr>
        </thead>

    {props.featuresets.map((featureset, idx) => {

      let done = featureset.finished
      let foldedContent = done && (
        <tr key={"plot" + featureset.id}>
          <td colSpan={4}>
            <Plot url={props.featurePlotURL + '/' + featureset.id}/>
          </td>
        </tr>)

      let status = done ? <td>Completed {reformatDatetime(featureset.finished)}</td> : <td>In progress</td>

      return (
        <FoldableRow key={idx}>
          <tr key={featureset.id}>
            <td>{featureset.name}</td>
            <td>{reformatDatetime(featureset.created)}</td>
            {status}
            <td><DeleteFeatureset featuresetID={featureset.id}/></td>
          </tr>
          {foldedContent}
        </FoldableRow>
      )})}


      </table>
    </div>
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
    <a style={style} onClick={(e) => {
      e.stopPropagation();
      props.dispatch(Action.deleteFeatureset(props.featuresetID))
    }}>Delete</a>
  )
}

DeleteFeatureset = connect()(DeleteFeatureset)

module.exports = FeaturesTab;

import React from 'react'
import { connect } from "react-redux"
import {reduxForm} from 'redux-form'
import { FormInputRow, FormSelectInput, SelectInput, FormTitleRow,
         FormComponent, Form, TextInput, FileInput, SubmitButton,
         CheckBoxInput } from './Form'
//import FileInput from 'react-file-input'
import ReactTabs from 'react-tabs'
import CheckboxGroup from 'react-checkbox-group'
import _ from 'underscore'
import filter from 'filter-values'
import * as Validate from './validate'
import {AddExpand} from './presentation'
import * as Action from './actions'

var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;


class FeaturizeForm extends FormComponent {
  render() {
    const {fields, fields: {datasetID, featuresetName, customFeatsFile, isTest},
           handleSubmit, submitting, resetForm, error} = this.props;
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
              <Tab>Obs Features</Tab>
              <Tab>Science Features</Tab>
              <Tab>Custom Features</Tab>
            </TabList>
            <TabPanel>
              <ul>
                {this.props.features.obs_features.map(feature => (
                   <CheckBoxInput key={'obs_' + feature} label={feature}
                                  {...fields['obs_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <ul>
                {this.props.features.sci_features.map(feature => (
                   <CheckBoxInput key={'sci_' + feature} label={feature}
                                  {...fields['sci_' + feature]}/>
                 ))
                }
              </ul>
            </TabPanel>
            <TabPanel>
              <textarea/>
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
                                                  'customFeatsFile', 'isTest']),
    initialValues: {...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : ""}
  }
}

FeaturizeForm = reduxForm({
  form: 'featurize',
  fields: ['']
}, mapStateToProps)(FeaturizeForm);

var FeaturesTab = (props) => {
    return (
      <div>
        <div>
          <AddExpand label="Compute New Features">
            <FeaturizeForm onSubmit={props.computeFeatures}
                           selectedProject={props.selectedProject}/>
          </AddExpand>
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
          <th>Name</th><th>Created</th><th>Debug (TODO remove)</th>
        </tr>

        {props.featuresets.map(featureset => (
           <tr key={featureset.id}>
             <td>{featureset.name}</td>
             <td>{featureset.created}</td>
             <td>Project: {featureset.project}</td>
           </tr>
         ))}

      </thead>
    </table>
  );
}

let ftMapStateToProps = (state) => {
  return {
    featuresets: state.featuresets.featuresetList
  }
}

FeatureTable = connect(ftMapStateToProps)(FeatureTable)




/* 
   class _FeaturizeForm extends FormComponent {
   render() {
   const {fields: {datasetID, featuresetName, features, customFeatsFile},
   handleSubmit} = this.props;
   return (
   <div>
   <form onSubmit={handleSubmit}>
   <FormTitleRow formTitle='Featurize Data'/>
   <FormSelectInput inputName='Select Project'
   inputTag='select'
   formName='featurize'
   optionsList={this.props.projects}
   value={this.props.formFields['Select Project']}
   handleInputChange={this.props.handleInputChange}
   />
   <FormSelectInput inputName='Select Dataset'
   inputTag='select'
   formName='featurize'
   optionsList={this.props.datasets}
   value={this.props.formFields['Select Dataset']}
   handleInputChange={this.props.handleInputChange}
   />
   <FormInputRow inputName='Feature Set Title'
   inputTag='input'
   inputType='text'
   formName='featurize'
   value={this.props.formFields['Dataset Name']}
   handleInputChange={this.props.handleInputChange}
   />

   <div className='submitButtonDiv' style={{marginTop: 15}}>
   <input type='submit'
   onClick={this.props.handleSubmit}
   value='Submit'
   className='submitButton'
   />
   </div>
   </form>
   <h4>Select Features to Compute (TODO: Make this a pop-up dialog)</h4>
   <FeatureSelectionDialog
   available_features={this.props.available_features}
   updateSeldObsFeats={this.props.updateSeldObsFeats}
   updateSeldSciFeats={this.props.updateSeldSciFeats}
   onFeaturesDialogMount={this.props.onFeaturesDialogMount}
   handleInputChange={this.props.handleInputChange}
   testCustomFeatScript={this.props.testCustomFeatScript}
   />

   </div>
   );
   }
   });
 */

var FeatureSelectionDialog = React.createClass({
  componentDidMount: function () {
    this.props.onFeaturesDialogMount();
  },
  updateObsFeats: function (seld_obs_feats) {
    this.props.updateSeldObsFeats(seld_obs_feats);
  },
  updateSciFeats: function (seld_sci_feats) {
    this.props.updateSeldSciFeats(seld_sci_feats);
  },
  render: function() {
    return (
      <Tabs classname='second'>
        <TabList>
          <Tab>Feature Set 1</Tab>
          <Tab>Feature Set 2</Tab>
          <Tab>Custom Features</Tab>
        </TabList>
        <TabPanel>
          <CheckboxGroup
              name='obs_feature_selection'
              value={Object.keys(filter(
                  this.props.available_features['obs_features'], 'checked'))}
              onChange={this.updateObsFeats}
          >
            { Checkbox => (
                <form>
                  {
                    Object.keys(this.props.available_features.obs_features).map(title =>
                      (
                        <div key={title}><Checkbox value={title}/> {title}</div>
                      )
                    )
                  }
                </form>
              )
            }
          </CheckboxGroup>
        </TabPanel>
        <TabPanel>
          <CheckboxGroup
              name='sci_feature_selection'
              value={Object.keys(filter(
                  this.props.available_features['sci_features'], 'checked'))}
              onChange={this.updateSciFeats}
          >
            { Checkbox => (
                <form>
                  {
                    Object.keys(this.props.available_features.sci_features).map(title =>
                      (
                        <div key={title}><Checkbox value={title}/> {title}</div>
                      )
                    )
                  }
                </form>
              )
            }
          </CheckboxGroup>
        </TabPanel>
        <TabPanel>
          Select Python file containing custom feature definitions:
          <br /><br />
          <div id='script_file_input_div'>
            <FileInput name='Custom Features File'
                       placeholder='Select .py file'
                       onChange={this.props.handleInputChange.bind(
                           null, 'Custom Features File',
                           'file', 'featurize')}
            />
          </div>
          <br />
          <div>
            <input type='button'
                   onClick={this.props.testCustomFeatScript}
                   value='Click to test' />
          </div>
          <div id='file_upload_message_div'></div>
        </TabPanel>
      </Tabs>
    );
  }
});


module.exports = FeaturesTab;

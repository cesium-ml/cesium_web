import React from 'react'
import { connect } from "react-redux"
import { FormInputRow, FormSelectInput, FormTitleRow } from './Form'
import FileInput from 'react-file-input'
import ReactTabs from 'react-tabs'
import CheckboxGroup from 'react-checkbox-group'
import _ from 'underscore'
import filter from 'filter-values'

var Tab = ReactTabs.Tab;
var Tabs = ReactTabs.Tabs;
var TabList = ReactTabs.TabList;
var TabPanel = ReactTabs.TabPanel;


var FeaturesTab = React.createClass({
  render: function() {
    return (
      <div className='featuresTabContent'>
      <FeaturizeForm
      handleInputChange={this.props.handleInputChange}
      formFields={this.props.formFields}
      handleSubmit={this.props.handleNewDatasetSubmit}
      datasets={this.props.datasets}
      featuresets={this.props.featuresets}
      projects={this.props.projects}
      formName={this.props.formName}
      available_features={this.props.available_features}
      updateSeldObsFeats={this.props.updateSeldObsFeats}
      updateSeldSciFeats={this.props.updateSeldSciFeats}
      onFeaturesDialogMount={this.props.onFeaturesDialogMount}
      testCustomFeatScript={this.props.testCustomFeatScript}
      />
      </div>
    );
  }
});


var FeaturizeForm = React.createClass({
  render: function() {
    return (
      <div className='formTableDiv'>
      <form id='featurizeForm' name='featurizeForm'
      action='/FeaturizeData' enctype='multipart/form-data'
      method='post'>
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

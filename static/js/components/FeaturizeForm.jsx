import React from 'react';
import PropTypes from 'prop-types';
import { reduxForm } from 'redux-form';
import ReactTabs from 'react-tabs';

import * as Validate from '../validate';
import { FormComponent, Form, TextInput, TextareaInput, SubmitButton,
         CheckBoxInput, SelectInput } from './Form';
import Expand from './Expand';
import { contains } from '../utils';
import * as Action from '../actions';


const { Tab, Tabs, TabList, TabPanel } = { ...ReactTabs };

const FeaturizeForm = (props) => {
  const { fields, fields: { datasetID, featuresetName, customFeatsCode },
          handleSubmit, submitting, resetForm, error, featuresList,
          featureDescriptions } = props;
  const datasets = props.datasets.map(ds => (
    { id: ds.id,
      label: ds.name }
  ));

  return (
    <div>
      <Form onSubmit={handleSubmit} error={error}>
        <SubmitButton
          label="Compute Selected Features"
          disabled={submitting}
          resetForm={resetForm}
        />
        <TextInput label="Feature Set Name" {...featuresetName} />
        <SelectInput
          label="Select Dataset to Featurize"
          key={props.selectedProject.id}
          options={datasets}
          {...datasetID}
        />
        <b>Select Features to Compute</b><br />
        <Expand label="Filter By Tag" id="featureTagsExpander">
          <span><i>Features associated with at least one checked tag will be shown below</i></span>
          {
            props.tagList.map(tag => (
              <CheckBoxInput
                defaultChecked
                key={tag}
                label={tag}
                divStyle={{ display: "table-cell", width: "150px" }}
                onChange={() => { props.dispatch(Action.clickFeatureTagCheckbox(tag)); }}
              />
            ))
          }
        </Expand>
        <Tabs>
          <TabList>
            {
              Object.keys(props.featuresByCategory).map(ctgy => (
                <Tab>{ctgy}</Tab>
              ))
            }
            <Tab>Custom Features</Tab>
          </TabList>
          {
            Object.keys(props.featuresByCategory).map(ctgy => (
              <TabPanel>
                <a
                  href="#"
                  onClick={
                    () => {
                      props.dispatch(Action.groupToggleCheckedFeatures(
                        props.featuresByCategory[ctgy]
                      ));
                    }
                  }
                >
                  Check/Uncheck All
                </a>
                <table style={{ overflow: "auto" }}>
                  <tbody>
                    {
                      props.featuresByCategory[ctgy].filter(feat => (
                        contains(featuresList, feat)
                      )).map((feature, idx) => (
                        <tr key={idx} style={idx % 2 == 0 ? { backgroundColor: "#f2f2f2" } : { }}>
                          <td style={{ paddingLeft: "20px" }}>
                            <CheckBoxInput
                              key={feature}
                              label={feature}
                              {...fields[feature]}
                            />
                          </td>
                          <td style={{ paddingLeft: "5px", verticalAlign: "bottom" }}>
                            {featureDescriptions[feature]}
                          </td>
                        </tr>
                      ))
                    }
                  </tbody>
                </table>
              </TabPanel>
            ))
          }
          <TabPanel>
            <TextareaInput
              label="Enter Python code defining custom features"
              rows="10"
              cols="50"
              {...customFeatsCode}
            />
          </TabPanel>
        </Tabs>
      </Form>
    </div>
  );
};
FeaturizeForm.propTypes = {
  fields: PropTypes.object.isRequired,
  datasets: PropTypes.arrayOf(PropTypes.object).isRequired,
  error: PropTypes.string,
  handleSubmit: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired,
  resetForm: PropTypes.func.isRequired,
  selectedProject: PropTypes.object.isRequired,
  featuresByCategory: PropTypes.object.isRequired,
  tagList: PropTypes.arrayOf(PropTypes.string).isRequired,
  featuresList: PropTypes.array.isRequired,
  featureDescriptions: PropTypes.object.isRequired
};
FeaturizeForm.defaultProps = {
  error: ""
};

const mapStateToProps = (state, ownProps) => {
  const featuresList = state.features.featsWithCheckedTags;

  const initialValues = { };
  featuresList.map((f, idx) => { initialValues[f] = true; return null; });

  const filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project_id === ownProps.selectedProject.id));
  const zerothDataset = filteredDatasets[0];

  return {
    featuresByCategory: state.features.features_by_category,
    tagList: state.features.tagList,
    featuresList,
    featureDescriptions: state.features.descriptions,
    datasets: filteredDatasets,
    fields: featuresList.concat(
      ['datasetID', 'featuresetName', 'customFeatsCode']
    ),
    initialValues: { ...initialValues,
                     datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                     customFeatsCode: "" }
  };
};

const validate = Validate.createValidator({
  datasetID: [Validate.required],
  featuresetName: [Validate.required]
});

export default reduxForm({
  form: 'featurize',
  fields: [''],
  validate
}, mapStateToProps)(FeaturizeForm);

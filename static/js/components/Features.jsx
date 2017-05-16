import React from 'react';
import { connect } from "react-redux";
import { reduxForm } from 'redux-form';
import ReactTabs from 'react-tabs';

import { FormComponent, Form, TextInput, TextareaInput, SubmitButton,
         CheckBoxInput, SelectInput } from './Form';
import * as Validate from '../validate';
import Expand from './Expand';
import * as Action from '../actions';
import Plot from './Plot';
import FoldableRow from './FoldableRow';
import { reformatDatetime, contains } from '../utils';
import Delete from './Delete';

const Tab = ReactTabs.Tab;
const Tabs = ReactTabs.Tabs;
const TabList = ReactTabs.TabList;
const TabPanel = ReactTabs.TabPanel;


let FeaturizeForm = (props) => {
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
          submiting={submitting}
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
                  onClick={() => {
                    props.dispatch(Action.groupToggleCheckedFeatures(
                      props.featuresByCategory[ctgy])); }}
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
              rows="10" cols="50"
              {...customFeatsCode}
            />
          </TabPanel>
        </Tabs>
      </Form>
    </div>
  );
};
FeaturizeForm.propTypes = {
  fields: React.PropTypes.object.isRequired,
  datasets: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  error: React.PropTypes.string,
  handleSubmit: React.PropTypes.func.isRequired,
  submitting: React.PropTypes.bool.isRequired,
  resetForm: React.PropTypes.func.isRequired,
  selectedProject: React.PropTypes.object,
  featuresByCategory: React.PropTypes.object,
  tagList: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  featuresList: React.PropTypes.array,
  featureDescriptions: React.PropTypes.object
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
      ['datasetID', 'featuresetName', 'customFeatsCode']),
    initialValues: { ...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                    customFeatsCode: "" }
  };
};

const validate = Validate.createValidator({
  datasetID: [Validate.required],
  featuresetName: [Validate.required]
});

FeaturizeForm = reduxForm({
  form: 'featurize',
  fields: [''],
  validate
}, mapStateToProps)(FeaturizeForm);


let FeaturesTab = (props) => {
  const { featurePlotURL } = props;
  return (
    <div>
      <div>
        <Expand label="Compute New Features" id="featsetFormExpander">
          <FeaturizeForm
            onSubmit={props.computeFeatures}
            selectedProject={props.selectedProject}
          />
        </Expand>
      </div>

      <FeatureTable
        selectedProject={props.selectedProject}
        featurePlotURL={featurePlotURL}
      />

    </div>
  );
};
FeaturesTab.propTypes = {
  featurePlotURL: React.PropTypes.string.isRequired,
  computeFeatures: React.PropTypes.func.isRequired,
  selectedProject: React.PropTypes.object
};

const ftMapDispatchToProps = dispatch => (
  {
    computeFeatures: form => dispatch(Action.computeFeatures(form))
  }
);

FeaturesTab = connect(null, ftMapDispatchToProps)(FeaturesTab);

export let FeatureTable = props => (
  <div>
    <table className="table">
      <thead>
        <tr>
          <th style={{ width: '15em' }}>Name</th>
          <th style={{ width: '15em' }}>Created</th>
          <th style={{ width: '15em' }}>Status</th>
          <th style={{ width: '15em' }}>Actions</th>
          <th style={{ width: 'auto' }} />{ /* extra column for spacing */ }
        </tr>
      </thead>

      {
        props.featuresets.map((featureset, idx) => {
          const done = featureset.finished;
          const foldedContent = done && (
            <tr key={`plot${featureset.id}`}>
              <td colSpan={4}>
                <Plot url={`${props.featurePlotURL}/${featureset.id}`} />
              </td>
            </tr>);

          const status = done ? <td>Completed {reformatDatetime(featureset.finished)}</td> : <td>In progress</td>;

          return (
            <FoldableRow key={idx}>
              <tr key={featureset.id}>
                <td>{featureset.name}</td>
                <td>{reformatDatetime(featureset.created)}</td>
                {status}
                <td><DeleteFeatureset ID={featureset.id} /></td>
              </tr>
              {foldedContent}
            </FoldableRow>
          ); })
      }

    </table>
  </div>
);
FeatureTable.propTypes = {
  featuresets: React.PropTypes.arrayOf(React.PropTypes.object),
  featurePlotURL: React.PropTypes.string
};


const ftMapStateToProps = (state, ownProps) => (
  {
    featuresets: state.featuresets.filter(
      fs => (fs.project_id === ownProps.selectedProject.id)
    )
  }
);

FeatureTable = connect(ftMapStateToProps)(FeatureTable);

const mapDispatchToProps = dispatch => (
  { delete: id => dispatch(Action.deleteFeatureset(id)) }
);

const DeleteFeatureset = connect(null, mapDispatchToProps)(Delete);

export default FeaturesTab;

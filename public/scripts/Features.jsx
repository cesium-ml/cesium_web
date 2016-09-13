import React from 'react';
import { connect } from "react-redux";
import { reduxForm } from 'redux-form';
import ReactTabs from 'react-tabs';

import { FormComponent, Form, TextInput, TextareaInput, SubmitButton,
         CheckBoxInput, SelectInput } from './Form';
import * as Validate from './validate';
import Expand from './Expand';
import * as Action from './actions';
import Plot from './Plot';
import FoldableRow from './FoldableRow';
import { reformatDatetime } from './utils';
import Delete from './Delete';

let Tab = ReactTabs.Tab;
let Tabs = ReactTabs.Tabs;
let TabList = ReactTabs.TabList;
let TabPanel = ReactTabs.TabPanel;


let FeaturizeForm = (props) => {
  const { fields, fields: { datasetID, featuresetName, customFeatsCode },
          handleSubmit, submitting, resetForm, error, groupToggleCheckedFeatures } = props;
  let datasets = props.datasets.map(ds => (
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
        <b>Select Features to Compute</b>
        <Tabs>
          <TabList>
            <Tab>General</Tab>
            <Tab>Cadence/Error</Tab>
            <Tab>Lomb Scargle (Periodic)</Tab>
            <Tab>Custom Features</Tab>
          </TabList>
          <TabPanel>
            <a
              href="#"
              onClick={() => { groupToggleCheckedFeatures("sci_"); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features.sci_features.map(feature => (
                  <CheckBoxInput
                    key={`sci_${feature}`}
                    label={feature}
                    {...fields[`sci_${feature}`]}
                  />
                ))
              }
            </ul>
          </TabPanel>
          <TabPanel>
            <a
              href="#"
              onClick={() => { groupToggleCheckedFeatures("obs_"); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features.obs_features.map(feature => (
                  <CheckBoxInput
                    key={`obs_${feature}`}
                    label={feature}
                    {...fields[`obs_${feature}`]}
                  />
                ))
              }
            </ul>
          </TabPanel>
          <TabPanel>
            <a
              href="#"
              onClick={() => { groupToggleCheckedFeatures("lmb_"); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features.lmb_features.map(feature => (
                  <CheckBoxInput
                    key={`lmb_${feature}`}
                    label={feature}
                    {...fields[`lmb_${feature}`]}
                  />
                ))
              }
            </ul>
          </TabPanel>
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
  groupToggleCheckedFeatures: React.PropTypes.func.isRequired,
  selectedProject: React.PropTypes.object,
  features: React.PropTypes.object
};


const mapStateToProps = (state, ownProps) => {
  const obs_features = state.featuresets.features.obs_features;
  const sci_features = state.featuresets.features.sci_features;
  const lmb_features = state.featuresets.features.lmb_features;
  const obs_fields = obs_features.map(f => `obs_${f}`);
  const sci_fields = sci_features.map(f => `sci_${f}`);
  const lmb_fields = lmb_features.map(f => `lmb_${f}`);

  const initialValues = {};
  obs_fields.map((f, idx) => { initialValues[f] = true; return null; });
  sci_fields.map((f, idx) => { initialValues[f] = true; return null; });
  lmb_fields.map((f, idx) => { initialValues[f] = true; return null; });

  const filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project === ownProps.selectedProject.id));
  const zerothDataset = filteredDatasets[0];

  return {
    features: state.featuresets.features,
    datasets: filteredDatasets,
    fields: obs_fields.concat(sci_fields).concat(lmb_fields).concat(
      ['datasetID', 'featuresetName', 'customFeatsCode']),
    initialValues: { ...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                    customFeatsCode: "" }
  };
};

const ffMapDispatchToProps = (dispatch) => (
  {
    groupToggleCheckedFeatures: (prefix) => dispatch(Action.groupToggleCheckedFeatures(prefix))
  }
);

const validate = Validate.createValidator({
  datasetID: [Validate.required],
  featuresetName: [Validate.required]
});

FeaturizeForm = reduxForm({
  form: 'featurize',
  fields: [''],
  validate
}, mapStateToProps, ffMapDispatchToProps)(FeaturizeForm);


let FeaturesTab = (props) => {
  let { featurePlotURL } = props;
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
  selectedProject: React.PropTypes.string
};

const ftMapDispatchToProps = (dispatch) => (
  {
    computeFeatures: (form) => dispatch(Action.computeFeatures(form))
  }
);

FeaturesTab = connect(null, ftMapDispatchToProps)(FeaturesTab);

export let FeatureTable = (props) => (
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
          let foldedContent = done && (
            <tr key={`plot${featureset.id}`}>
              <td colSpan={4}>
                <Plot url={`${props.featurePlotURL}/${featureset.id}`} />
              </td>
            </tr>);

          let status = done ? <td>Completed {reformatDatetime(featureset.finished)}</td> : <td>In progress</td>;

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
    featuresets: state.featuresets.featuresetList.filter(
      fs => (fs.project === ownProps.selectedProject.id)
    )
  }
);

FeatureTable = connect(ftMapStateToProps)(FeatureTable);

const mapDispatchToProps = (dispatch) => (
  { delete: (id) => dispatch(Action.deleteFeatureset(id)) }
);

let DeleteFeatureset = connect(null, mapDispatchToProps)(Delete);

export default FeaturesTab;

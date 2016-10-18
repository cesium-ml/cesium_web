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
import { reformatDatetime, contains } from './utils';
import Delete from './Delete';

const Tab = ReactTabs.Tab;
const Tabs = ReactTabs.Tabs;
const TabList = ReactTabs.TabList;
const TabPanel = ReactTabs.TabPanel;


let FeaturizeForm = (props) => {
  const { fields, fields: { datasetID, featuresetName, customFeatsCode },
          handleSubmit, submitting, resetForm, error, groupToggleCheckedFeatures,
          features_with_checked_tags } = props;
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
        <b>Select Features to Compute</b><br /><br />
        <span>Feature Tags (check/uncheck to show/hide)</span>

        {
          props.tag_list.map(tag => (
            <CheckBoxInput
              key={tag}
              label={tag}
              {...fields[tag]}
            />
          ))
        }
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
              onClick={() => { groupToggleCheckedFeatures(props.features_by_category.general); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features_by_category.general.filter(feat => (
                  contains(features_with_checked_tags, feat)
                )).map(feature => (
                  <CheckBoxInput
                    key={feature}
                    label={feature}
                    {...fields[feature]}
                  />
                ))
              }
            </ul>
          </TabPanel>
          <TabPanel>
            <a
              href="#"
              onClick={() => { groupToggleCheckedFeatures(props.features_by_category.cadence); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features_by_category.cadence.filter(feat => (
                  contains(features_with_checked_tags, feat)
                )).map(feature => (
                  <CheckBoxInput
                    key={feature}
                    label={feature}
                    {...fields[feature]}
                  />
                ))
              }
            </ul>
          </TabPanel>
          <TabPanel>
            <a
              href="#"
              onClick={() => { groupToggleCheckedFeatures(props.features_by_category.lomb_scargle); }}
            >
              Check/Uncheck All
            </a>
            <ul>
              {
                props.features_by_category.lomb_scargle.filter(feat => (
                  contains(features_with_checked_tags, feat)
                )).map(feature => (
                  <CheckBoxInput
                    key={feature}
                    label={feature}
                    {...fields[feature]}
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
  features_by_category: React.PropTypes.object,
  tag_list: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
  features_with_checked_tags: React.PropTypes.array
};


const mapStateToProps = (state, ownProps) => {
  let features_list = [].concat(state.features.features_by_category.cadence);
  features_list = features_list.concat(state.features.features_by_category.general);
  features_list = features_list.concat(state.features.features_by_category.lomb_scargle);

  let tag_list = [];
  for (const feat in state.features.tags) {
    if (!state.features.tags.hasOwnProperty(feat)) continue;
    for (const idx in state.features.tags[feat]) {
      if (tag_list.indexOf(state.features.tags[feat][idx]) === -1) {
        tag_list.push(state.features.tags[feat][idx]);
      }
    }
  }

  let checked_tags = [];
  if (state.form.featurize) {
    checked_tags = tag_list.filter(tag => (state.form.featurize[tag].value));
  } else {
    checked_tags = tag_list;
  }
  const features_with_checked_tags = features_list.filter(feature => (
    state.features.tags[feature].some(tag => contains(checked_tags, tag))));

  const initialValues = { };
  features_list.map((f, idx) => { initialValues[f] = true; return null; });
  tag_list.map((tag, idx) => { initialValues[tag] = true; return null; });

  const filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project === ownProps.selectedProject.id));
  const zerothDataset = filteredDatasets[0];

  return {
    features_by_category: state.features.features_by_category,
    tag_list,
    features_with_checked_tags,
    datasets: filteredDatasets,
    fields: features_list.concat(tag_list).concat(
      ['datasetID', 'featuresetName', 'customFeatsCode']),
    initialValues: { ...initialValues,
                    datasetID: zerothDataset ? zerothDataset.id.toString() : "",
                    customFeatsCode: "" }
  };
};

const ffMapDispatchToProps = dispatch => (
  {
    groupToggleCheckedFeatures: prefix => dispatch(Action.groupToggleCheckedFeatures(prefix))
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
      fs => (fs.project === ownProps.selectedProject.id)
    )
  }
);

FeatureTable = connect(ftMapStateToProps)(FeatureTable);

const mapDispatchToProps = dispatch => (
  { delete: id => dispatch(Action.deleteFeatureset(id)) }
);

const DeleteFeatureset = connect(null, mapDispatchToProps)(Delete);

export default FeaturesTab;

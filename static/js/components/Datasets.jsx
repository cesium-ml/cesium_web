import React from 'react';
import PropTypes from 'prop-types';
import { connect } from "react-redux";
import { reduxForm } from 'redux-form';

import { showNotification } from 'baselayer/components/Notifications';
import { FormComponent, Form, TextInput, FileInput, SubmitButton } from './Form';
import * as Validate from '../validate';
import Expand from './Expand';
import Delete from './Delete';
import * as Action from '../actions';
import { reformatDatetime } from '../utils';
import CesiumTooltip from './Tooltip';
import FoldableRow from './FoldableRow';


const DatasetsTab = props => (
  <div className="datasetsTab">

    <Expand label="Upload new dataset" id="newDatasetExpander">
      <DatasetForm selectedProject={props.selectedProject} />
    </Expand>

    <DatasetTable selectedProject={props.selectedProject} />

  </div>
);
DatasetsTab.propTypes = {
  selectedProject: PropTypes.object
};
DatasetsTab.defaultProps = {
  selectedProject: {}
};

let DatasetForm = (props) => {
  const { fields: { datasetName, headerFile, tarFile },
    error, handleSubmit, submitting } = props;

  const description = {
    fontStyle: 'italic',
    paddingBottom: '1em'
  };

  return (
    <div>
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Dataset Name" {...datasetName} />
        <FileInput
          label="Header File"
          {...headerFile}
          data-tip
          data-for="headerfileTooltip"
        />

        <div style={description}>
          {'Format: comma-separated with columns "filename" (of a time series from the uploaded archive), "label" (class label or numerical value), and any metafeatures (numerical).'}
        </div>

        <FileInput
          label="Data Tarball"
          {...tarFile}
          data-tip
          data-for="tarfileTooltip"
        />
        <div style={description}>
          {'Format: zipfile or tarfile containing time series files, each of which is comma-separated with columns "time", "value", "error" (optional).'}
        </div>

        <SubmitButton label="Upload Dataset" disabled={submitting} />
      </Form>

      <CesiumTooltip
        id="headerfileTooltip"
        place="right"
        text={["filename,label", <br key={1} />, "ts1.dat,class_A", <br key={2} />, "..."]}
      />
      <CesiumTooltip
        id="tarfileTooltip"
        place="right"
        text={[
          "Each file in tarball should be formatted as follows",
          <br />, "(column titles are optional)", <br />, <br />,
          "time,value,error", <br />,
          "125912.23,12.31604,0.279105", <br />,
          "..."]}
      />

    </div>
  );
};
DatasetForm.propTypes = {
  fields: PropTypes.object.isRequired,
  error: PropTypes.string,
  handleSubmit: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired
};
DatasetForm.defaultProps = {
  error: ""
};

const dsMapStateToProps = (state, ownProps) => (
  {
    initialValues: {
      ...(ownProps.initialValues),
      projectID: ownProps.selectedProject.id
    }
  }
);

const dsMapDispatchToProps = (dispatch, ownProps) => (
  {
    onSubmit: (form) => {
      dispatch(showNotification('Dataset upload has begun.'));
      return dispatch(Action.uploadDataset(form));
    }
  }
);

const validate = Validate.createValidator({
  datasetName: [Validate.required],
  tarFile: [Validate.oneFile],
});

DatasetForm = reduxForm({
  form: 'newDataset',
  fields: ['datasetName', 'headerFile', 'tarFile', 'projectID'],
  validate
}, dsMapStateToProps, dsMapDispatchToProps)(DatasetForm);


const DatasetInfo = props => (
  <table className="table">
    <thead>
      <tr>
        <th>Time Series File Names</th>
        <th>Meta Features</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          {props.dataset.files.join(', ')}
        </td>
        <td>
          {props.dataset.meta_features.join(', ')}
        </td>
      </tr>
    </tbody>
  </table>
);
DatasetInfo.propTypes = {
  dataset: PropTypes.object.isRequired
};

export let DatasetTable = props => (
  <table className="table">
    <thead>
      <tr>
        <th>Name</th><th>Uploaded</th><th>Actions</th>
      </tr>
    </thead>

    {
      props.datasets.map((dataset, idx) => {
        const foldedContent = (
          <tr key={`dsinfo_${idx}`}>
            <td colSpan={6}>
              <DatasetInfo dataset={dataset} />
            </td>
          </tr>
        );

        return (
          <FoldableRow key={`ds_${idx}`}>
            <tr key={dataset.id}>
              <td>{dataset.name}</td>
              <td>{reformatDatetime(dataset.created_at)}</td>
              <td><DeleteDataset ID={dataset.id} /></td>
            </tr>
            {foldedContent}
          </FoldableRow>
        );
      })
    }

  </table>
);
DatasetTable.propTypes = {
  datasets: PropTypes.arrayOf(PropTypes.object).isRequired
};


const mapStateToProps = (state, ownProps) => (
  {
    datasets: state.datasets.filter(dataset => (
      dataset.project_id === ownProps.selectedProject.id
    ))
  }
);

DatasetTable = connect(mapStateToProps)(DatasetTable);

const mapDispatchToProps = dispatch => (
  { delete: id => dispatch(Action.deleteDataset(id)) }
);

const DeleteDataset = connect(null, mapDispatchToProps)(Delete);

export default DatasetsTab;

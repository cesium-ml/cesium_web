import React from 'react';
import { reduxForm } from 'redux-form';

import { FormComponent, Form, TextInput, TextareaInput, SubmitButton,
         CheckBoxInput, SelectInput, FileInput } from './Form';
import * as Validate from '../validate';
import CesiumTooltip from './Tooltip';


const UploadFeaturesForm = props => {
  const { fields, fields: { datasetID, featuresetName, dataFile },
          handleSubmit, submitting, resetForm, error, featuresList,
          featureDescriptions } = props;
  const datasets = props.datasets.map(ds => (
    { id: ds.id,
      label: ds.name }
  ));

  return (
    <div>
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Feature Set Name" {...featuresetName} />
        <SelectInput
          label="Select Associated Featureset"
          key={props.selectedProject.id}
          options={[{ label: 'No associated dataset', id: 'None' }, ...datasets]}
          {...datasetID}
        />
        <FileInput
          label="Data File"
          {...dataFile}
          data-tip
          data-for="dataFileTooltip"
        />
        <SubmitButton
          label="Upload Features"
          disabled={submitting}
          resetForm={resetForm}
        />
      </Form>
      <CesiumTooltip
        id="dataFileTooltip"
        text="File format must match that of downloaded feature set"
      />
    </div>
  );
};

UploadFeaturesForm.propTypes = {
  fields: React.PropTypes.object.isRequired,
  datasets: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  error: React.PropTypes.string,
  handleSubmit: React.PropTypes.func.isRequired,
  submitting: React.PropTypes.bool.isRequired,
  resetForm: React.PropTypes.func.isRequired,
  selectedProject: React.PropTypes.object
};


const mapStateToProps = (state, ownProps) => {

  const initialValues = { };

  const filteredDatasets = state.datasets.filter(dataset =>
    (dataset.project_id === ownProps.selectedProject.id));

  return {
    datasets: filteredDatasets,
    fields: ['datasetID', 'featuresetName', 'dataFile'],
    initialValues: { ...initialValues,
                     datasetID: "No associated dataset" }
  };
};

const validate = Validate.createValidator({
  featuresetName: [Validate.required],
  dataFile: [Validate.oneFile]
});

export default reduxForm(
  {
    form: 'uploadFeatures',
    fields: [''],
    validate
  }, mapStateToProps)(UploadFeaturesForm);

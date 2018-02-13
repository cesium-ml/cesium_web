import React from 'react';
import PropTypes from 'prop-types';
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
import UploadFeaturesForm from './UploadFeaturesForm';
import FeaturizeForm from './FeaturizeForm';
import FeaturesetsTable from './FeaturesetsTable';


let FeaturesTab = (props) => {
  const { featurePlotURL } = props;
  return (
    <div>
      <div>
        <Expand label=" Compute New Features" id="featsetFormExpander">
          <FeaturizeForm
            onSubmit={props.computeFeatures}
            selectedProject={props.selectedProject}
          />
        </Expand>
      </div>

      <div>
        <Expand label=" Upload Pre-Computed Features" id="uploadFeatsFormExpander">
          <UploadFeaturesForm
            onSubmit={props.uploadFeatures}
            selectedProject={props.selectedProject}
          />
        </Expand>
      </div>

      <FeaturesetsTable
        selectedProject={props.selectedProject}
        featurePlotURL={featurePlotURL}
      />

    </div>
  );
};
FeaturesTab.propTypes = {
  featurePlotURL: PropTypes.string.isRequired,
  computeFeatures: PropTypes.func.isRequired,
  selectedProject: PropTypes.object
};
FeaturesTab.defaultProps = {
  selectedProject: {}
};

const ftMapDispatchToProps = dispatch => (
  {
    computeFeatures: form => dispatch(Action.computeFeatures(form))
  }
);

FeaturesTab = connect(null, ftMapDispatchToProps)(FeaturesTab);

export default FeaturesTab;

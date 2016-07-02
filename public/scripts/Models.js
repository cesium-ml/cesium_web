import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {reduxForm} from 'redux-form'

import { FormComponent, TextInput, SelectInput, SubmitButton, Form, Button } from './Form'
import * as Validate from './validate';

const ModelsTab = (props) => (
  <div>
    <NewModelForm onSubmit={props.onSubmitModelClick}/>
  </div>
);

const models = [
  {id: 'RandomForestClassifier', label: 'Random Forest Classifier'},
  {id: 'LinearRegression', label: 'Linear Regression'}
]

class NewModelForm extends FormComponent {
  render() {
    const {fields: {modelName, project, featureSet, modelType}, handleSubmit} = this.props;
    return (
      <Form onSubmit={handleSubmit}>
        <TextInput label="Model Name" {...modelName}/>
        <SelectInput label="Model Type"
                     options={models}
                     {...modelType}/>
        <SubmitButton label="Create Model"/>
      </Form>
    );
  }
}

const validate = Validate.createValidator({
  modelName: [Validate.required],
});

const mapStateToProps = function(state) {
  return {...state.models,
          projects: state.projects,
          featureSets: state.featuresets};
}

const mapDispatchToProps = (dispatch) => {
  return {
    onModelSubmit: (form) => {
      console.log(form);
    }
  }
}

NewModelForm = reduxForm({
  form: 'newModel',
  fields: ['modelName', 'project', 'featureSet', 'modelType'],
  initialValues: {
    modelType: models[0].id
  },
  validate
}, mapStateToProps, mapDispatchToProps)(NewModelForm);

export default ModelsTab;

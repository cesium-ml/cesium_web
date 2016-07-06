import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {reduxForm} from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton, Form, Button } from './Form'
import * as Validate from './validate';


const ModelsTab = (props) => (
  <div>
    <NewModelForm/>
  </div>
);


class NewModelForm extends FormComponent {
  render() {
    const {fields,
           fields: {modelName, project, featureSet, modelType},
           error, handleSubmit} = this.props;

    console.log(this.props);

    let skModels = this.props.models;
    let selectModels = []

    for (var key in skModels) {
      if (skModels.hasOwnProperty(key)) {
        let model = skModels[key];
        selectModels.push({
          id: key,
          label: model.name
        })
      }
    }

    let chosenModel = this.props.models[modelType.value];

    return (
      <Form onSubmit={handleSubmit} error={error}>
        <TextInput label="Model name (choose your own)" {...modelName}/>
        <SelectInput label="Model Type"
                     options={selectModels} {...modelType}/>

          <Model model={chosenModel} {...fields}/>

        <SubmitButton label="Create Model"/>
      </Form>
    );
  }
}

const validate = Validate.createValidator({
  modelName: [Validate.required],
});

const mapStateToProps = function(state) {
  let formState = state.form.newModel;
  let currentModelId = formState ? state.form.newModel.modelType.value : 0;
  let currentModel = state.sklearnModels[currentModelId];
  let modelFields = currentModel.params.map(param => param.name);

  let fields = ['modelName', 'project', 'featureSet', 'modelType']
  fields = fields.concat(modelFields)

  let paramDefaults = {}
  currentModel.params.map(param => {
    paramDefaults[param.name] = (param.default === null) ? "None" : param.default;
  })

  return {
    models: state.sklearnModels,
    projects: state.projects,
    featureSets: state.featuresets,
    fields: fields,
    initialValues: {
      modelType: currentModelId,
      ...paramDefaults
    }
  };
}

const mapDispatchToProps = (dispatch) => {
  return {
    onSubmit: (form) => {
      console.log('submitted', form);
    }
  }
}

NewModelForm = reduxForm({
  form: 'newModel',
  fields: [],
}, mapStateToProps, mapDispatchToProps)(NewModelForm);


export var Model = (props) => {
  let style = {
    border: '5px solid PowderBlue',
    padding: '2em'
  }

  let model = props.model;

  return (
    <div style={style}>
      <b>Name: {model.name}</b><br/>
    {model.params.map((param, idx) => {
      let pProps = props[param.name];
      if (param.type === 'bool') {
        return <CheckBoxInput key={idx} label={param.name} {...(pProps)}/>
      } else {
        return <TextInput key={idx} label={param.name} {...(pProps)}/>
      }
    })}
    </div>
  )
}


export default ModelsTab;

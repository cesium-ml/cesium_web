import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {reduxForm} from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton, Form, Button } from './Form'
import * as Validate from './validate'
import * as Action from './actions'
import {AddExpand} from './presentation'


const ModelsTab = (props) => (
  <div>
    <NewModelForm selectedProject={props.selectedProject}/>
  </div>
);


class NewModelForm extends FormComponent {
  render() {
    const {fields,
           fields: {modelName, project, featureSet, modelType},
           error, handleSubmit} = this.props;

    let skModels = this.props.models;
    let selectModels = []

    for (let key in skModels) {
      if (skModels.hasOwnProperty(key)) {
        let model = skModels[key];
        selectModels.push({
          id: key,
          label: model.name
        })
      }
    }

    let featureSets = this.props.featureSets.map(fs => (
      {
        id: fs.id,
        label: fs.name
      }));

    let chosenModel = this.props.models[modelType.value];

    return (
      <Form onSubmit={handleSubmit} error={error}>
      <TextInput label="Model name (choose your own)" {...modelName}/>

      <SelectInput label="Feature Set"
                   options={featureSets} {...featureSet}/>

      <SelectInput label="Model Type"
                   options={selectModels} {...modelType}/>

      <AddExpand label="Choose Model Parameters">
          <Model model={chosenModel} {...fields}/>
      </AddExpand>

        <SubmitButton label="Create Model"/>
      </Form>
    );
  }
}

const mapStateToProps = function(state, ownProps) {
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

  let firstFeatureSet = state.featuresets.featuresetList[0];
  let firstFeatureSetID = firstFeatureSet ? firstFeatureSet.id : "";

  return {
    models: state.sklearnModels,
    projects: state.projects,
    featureSets: state.featuresets.featuresetList,
    fields: fields,
    initialValues: {
      modelType: currentModelId,
      project: ownProps.selectedProject.id,
      featureSet: firstFeatureSetID,
      ...paramDefaults
    }
  };
}

const mapDispatchToProps = (dispatch) => {
  return {
    onSubmit: (form) => dispatch(Action.createModel(form))
  }
}

const validate = Validate.createValidator({
  modelName: [Validate.required],
});

NewModelForm = reduxForm({
  form: 'newModel',
  fields: [],
  validate
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

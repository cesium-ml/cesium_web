import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {reduxForm} from 'redux-form'

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton, Form, Button } from './Form'
import * as Validate from './validate'
import * as Action from './actions'
import Expand from './Expand'


const ModelsTab = (props) => (
  <div>
    <Expand label="Create New Model" id="newModelExpander">
      <NewModelForm selectedProject={props.selectedProject}/>
    </Expand>

    <ModelTable selectedProject={props.selectedProject}/>
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

      <Expand label="Choose Model Parameters" id='modelParameterExpander'>
          <Model model={chosenModel} {...fields}/>
      </Expand>

        <SubmitButton label="Create Model"/>
      </Form>
    );
  }
}

const mapStateToProps = function(state, ownProps) {
  let formState = state.form.newModel;
  let currentModelId = formState ? formState.modelType.value : 0;
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
  featureSet: [Validate.required]
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


export var ModelTable = (props) => {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Name</th><th>Created</th><th>Debug</th><th>Actions</th>
        </tr>

        {props.models.map(model => (
           <tr key={model.id}>
             <td>{model.name}</td>
             <td>{model.created}</td>
             <td>Project: {model.project}</td>
             <td><DeleteModel modelID={model.id}/></td>
           </tr>
         ))}

      </thead>
    </table>
  );
}

let mtMapStateToProps = (state) => {
  return {
    models: state.models
  }
}

ModelTable = connect(mtMapStateToProps)(ModelTable)


export var DeleteModel = (props) => {
  let style = {
    display: 'inline-block'
  }
  return (
    <a style={style} onClick={() => props.deleteModel(props.modelID)}>Delete</a>
  )
}

let dmMapDispatchToProps = (dispatch) => {
  return (
    {deleteModel: (id) => dispatch(Action.deleteModel(id))}
  );
}

DeleteModel = connect(null, dmMapDispatchToProps)(DeleteModel);


export default ModelsTab;

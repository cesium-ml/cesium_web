import React, { PropTypes } from 'react';
import { connect } from 'react-redux';
import { reduxForm } from 'redux-form';

import { FormComponent, TextInput, CheckBoxInput, SelectInput, SubmitButton, Form } from './Form';

import * as Validate from '../validate';

import * as Action from '../actions';
import Expand from './Expand';
import Delete from './Delete';
import { $try, reformatDatetime } from '../utils';
import FoldableRow from './FoldableRow';


const ModelsTab = props => (
  <div>
    <Expand label="Create New Model" id="newModelExpander">
      <NewModelForm selectedProject={props.selectedProject} />
    </Expand>

    <ModelTable selectedProject={props.selectedProject} />
  </div>
);
ModelsTab.propTypes = {
  selectedProject: React.PropTypes.object
};

let NewModelForm = (props) => {
  const { fields,
          fields: { modelName, featureset, modelType },
          error, handleSubmit } = props;

  const skModels = props.models;
  const selectModels = [];

  for (const key in skModels) {
    if ({}.hasOwnProperty.call(skModels, key)) {
      const model = skModels[key];
      selectModels.push({
        id: key,
        label: model.name
      });
    }
  }

  const featuresets = props.featuresets
                        .filter(fs => !Validate.isEmpty(fs.finished))
                        .map(fs => (
                          {
                            id: fs.id,
                            label: fs.name
                          }
                        ));

  const chosenModel = props.models[modelType.value];

  return (
    <Form onSubmit={handleSubmit} error={error}>
      <TextInput label="Model name (choose your own)" {...modelName} />

      <SelectInput
        label="Feature Set"
        key={props.selectedProject.id}
        options={featuresets} {...featureset}
      />

      <SelectInput
        label="Model Type"
        options={selectModels} {...modelType}
      />

      <Expand label="Choose Model Parameters" id="modelParameterExpander">
        {chosenModel && <Model model={chosenModel} {...fields} />}
      </Expand>

      <SubmitButton label="Create Model" />
    </Form>
  );
};
NewModelForm.propTypes = {
  fields: React.PropTypes.object.isRequired,
  error: React.PropTypes.string,
  handleSubmit: React.PropTypes.func.isRequired,
  featuresets: React.PropTypes.arrayOf(React.PropTypes.object).isRequired,
  models: React.PropTypes.object.isRequired
};

const mapStateToProps = function (state, ownProps) {
  const formState = state.form.newModel;
  const currentModelType = formState ? formState.modelType : null;
  const currentModelId = $try(() => formState.modelType.value) || 0;
  const currentModel = state.sklearnModels[currentModelId];
  const modelFields = currentModel.params.map(param => param.name);

  let fields = ['modelName', 'project', 'featureset', 'modelType'];
  fields = fields.concat(modelFields);

  const paramDefaults = {};
  currentModel.params.map((param) => {
    paramDefaults[param.name] = (param.default === null) ? "None" : param.default;
  });

  const filteredFeaturesets = state.featuresets.filter(featureset =>
    (featureset.project === ownProps.selectedProject.id));
  const firstFeatureset = filteredFeaturesets[0];
  const firstFeaturesetID = firstFeatureset ? firstFeatureset.id : "";

  return {
    models: state.sklearnModels,
    projects: state.projects,
    featuresets: filteredFeaturesets,
    fields,
    initialValues: {
      modelType: currentModelId,
      project: ownProps.selectedProject.id,
      featureset: firstFeaturesetID,
      ...paramDefaults
    }
  };
};

const mapDispatchToProps = dispatch => (
  {
    onSubmit: form => dispatch(Action.createModel(form))
  }
);

const validate = Validate.createValidator({
  modelName: [Validate.required],
  featureset: [Validate.required]
});

NewModelForm = reduxForm({
  form: 'newModel',
  fields: [],
  validate
}, mapStateToProps, mapDispatchToProps)(NewModelForm);


export const Model = (props) => {
  const style = {
  };

  const model = props.model;

  return (
    <div style={style}>
      <h3>{model.name}</h3>
    {model.params.map((param, idx) => {
      const pProps = props[param.name];
      if (param.type === 'bool') {
        return <CheckBoxInput key={idx} label={param.name} {...(pProps)} />;
      } else {
        return <TextInput key={idx} label={param.name} {...(pProps)} />;
      }
    })}
    </div>
  );
};
Model.propTypes = {
  model: React.PropTypes.object.isRequired
};


let ModelInfo = props => (
  <table className="table">
    <thead>
      <tr>
        <th>Model Type</th>
        <th>Hyperparameters</th>
        <th>Training Data Score</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          {props.model.type}
        </td>
        <td>
          <table>
            <tbody>
              {
                Object.keys(props.model.params).map(param => (
                  <tr>
                    <td>{param}</td>
                    <td style={{ paddingLeft: "5px" }}>{JSON.stringify(props.model.params[param])}</td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        </td>
        <td>
          {props.model.train_score}
        </td>
      </tr>
    </tbody>
  </table>
);
ModelInfo.propTypes = {
  model: React.PropTypes.object.isRequired
};

export let ModelTable = props => (
  <table className="table">
    <thead>
      <tr>
        <th>Name</th><th>Created</th><th>Status</th><th>Actions</th>
      </tr>
    </thead>

    {
      props.models.map((model, idx) => {
        const done = model.finished;
        const status = done ? <td>Completed {reformatDatetime(model.finished)}</td> : <td>In progress</td>;

        const foldedContent = done && (
          <tr key={`modelinfo_${idx}`}>
            <td colSpan={6}>
              <ModelInfo model={model} />
            </td>
          </tr>
        );

        return (
          <FoldableRow key={`model_${idx}`}>
            <tr key={model.id}>
              <td>{model.name}</td>
              <td>{reformatDatetime(model.created)}</td>
              {status}
              <td><DeleteModel ID={model.id} /></td>
            </tr>
            {foldedContent}
          </FoldableRow>
        );
      })
    }

  </table>
);
ModelTable.propTypes = {
  models: PropTypes.arrayOf(PropTypes.object)
};

const mtMapStateToProps = (state, ownProps) => (
  {
    models: state.models.filter(
      model => (model.project === ownProps.selectedProject.id))
  }
);

ModelTable = connect(mtMapStateToProps)(ModelTable);


const dmMapDispatchToProps = dispatch => (
  { delete: id => dispatch(Action.deleteModel(id)) }
);

const DeleteModel = connect(null, dmMapDispatchToProps)(Delete);


export default ModelsTab;

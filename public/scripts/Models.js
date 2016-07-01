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

class NewModelForm extends FormComponent {
  render() {
    const {fields: {modelName, project, featureSet, modelType}, handleSubmit} = this.props;
    return (
      <Form onSubmit={handleSubmit}>
        <TextInput label="Model Name" {...modelName}/>
        <SelectInput label="Model Type"
                     options={[{id: 1, name: 'RandomForestClassifier'},
                               {id: 2, name: 'Linear'}]}
                     {...modelType}/>
        <SubmitButton label="Create Model"/>
      </Form>
    );
  }
}

//NewModelForm.propTypes = {
//  fields: PropTypes.object.isRequired,
//  handleSubmit: PropTypes.func.isRequired,
//  resetForm: PropTypes.func.isRequired,
//  submitting: PropTypes.bool.isRequired
//}

const validate = Validate.createValidator({
  modelName: [Validate.required],
});

NewModelForm = reduxForm({
  form: 'newModel',
  fields: ['modelName', 'project', 'featureSet', 'modelType'],
  validate
})(NewModelForm);


/* var ModelForm = React.createClass({
 *   render: function() {
 *     return (
 *       <div>
 *       <form>
 *       <FormTitleRow formTitle='Create Model'/>
 *       <FormInputRow inputName='Name' inputTag='input' inputType='text'
 *                     handleInputChange={console.log}/>
 *       <FormSelectInput inputName='Model Type'
 *                        inputTag='select'
 *                        optionsList={[{id: 1, name: 'RandomForestClassifier'},
 *                                      {id: 2, name: 'Linear'}]}
 *                        handleInputChange={console.log}
 *       />
 *       <FormSelectInput inputName='Select Project'
 *                        inputTag='select'
 *                        optionsList={this.props.projects}
 *                        handleInputChange={console.log}
 *       />
 *       <FormSelectInput inputName='Select Feature Set'
 *                        inputTag='select'
 *                        optionsList={this.props.featureSets}
 *                        handleInputChange={console.log}
 *       />
 * 
 *       <input type='submit'
 *              onClick={x => console.log(x)}
 *              value='Create Model'
 *              className='submitButton'
 *       />
 * 
 *       </form>
 *       </div>
 *     )
 *   }
 * });
 * */

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

NewModelForm = connect(mapStateToProps, mapDispatchToProps)(NewModelForm);

export default ModelsTab;

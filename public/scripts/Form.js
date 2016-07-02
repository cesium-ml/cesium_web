import React, { Component, PropTypes } from 'react'

export class FormComponent extends Component {
}
FormComponent.propTypes = {
  fields: PropTypes.object.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  resetForm: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired
}


export var Error = (props) => {
  let errorStyle = {
    color: 'darkred',
    fontStyle: 'italic'
  }

  if (props.touched && props.error) {
    return <div style={errorStyle}>{props.error}</div>
  } else {
    return null;
  }
}
Error.propTypes = {
  touched: PropTypes.bool.isRequired,
  error: PropTypes.string
}

export var Form = (props) => {
  return (
    <form {...props} class="form-inline"/>
  )
}
Form.propTypes = {
  onSubmit: PropTypes.func.isRequired
}

export var TextInput = (props) => {
 let textInputStyle = {
    paddingTop: 10
  }

  return (
    <div className="form-group" style={textInputStyle}>
      <label>{props.label}</label>
      <input className="form-control"
             type="text"
      {...props}/>
      <Error {...props}/>
    </div>
  )
}
TextInput.propTypes = {
  label: PropTypes.string
}

export var SelectInput = (props) => {
  let selectInputStyle = {
    paddingTop: 10
  }

  return (
    <div className="form-group" style={selectInputStyle}>
      <label>{props.label}</label>
      <select className="form-control"
              value={props.value}
              {...props}>
        {props.options.map((option, idx) => (
           <option value={option.id} key={option.id} >
             {option.label}
           </option>
         ))}
      </select>
    </div>
  );
}
SelectInput.propTypes = {
  label: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([
      PropTypes.number,
      PropTypes.string]).isRequired,
    label: PropTypes.string.isRequired
  })),
  value: PropTypes.any  // array of individual value
}


export var SubmitButton = (props) => {
  let submitButtonStyle = {
    paddingTop: 10
  }

  return (
    <div className="form-group" style={submitButtonStyle}>
      <button type="submit"
              className="btn btn-primary">{props.label}</button>
    </div>
  )
}
SubmitButton.propTypes = {
  label: PropTypes.string
}






export var FormInputRow = React.createClass({
  render: function() {
    return (
      <div>
        <div style={{width: 320, float: 'left', marginTop: 5}}>
          {this.props.inputName}
        </div>
        <div
           style={{marginLeft: 340, marginTop: 5}}>
          <this.props.inputTag
                 type={this.props.inputType}
                 value={this.props.value}
                 onChange={this.props.handleInputChange.bind(
                     null, this.props.inputName,
                     this.props.inputType,
                     this.props.formName)}
          />
        </div>
      </div>
    );
  }
});

export var FormSelectInput = React.createClass({
  render: function() {
    var selectOptions = this.props.optionsList.map(function(option) {
      return (
        <option value={option.id} key={option.id}>
          {option.name}
        </option>
      );
    }.bind(this));
    return (
      <div>
        <div style={{width: 320, float: 'left', marginTop: 5}}>
          {this.props.inputName}
        </div>
        <div
           style={{marginLeft: 340, marginTop: 5}}>
          <select
            value={this.props.value}
            onLoad={this.props.handleInputChange.bind(
                null, this.props.inputName,
                this.props.inputType,
                this.props.formName)}
            onChange={this.props.handleInputChange.bind(
                null, this.props.inputName,
                this.props.inputType,
                this.props.formName)}>
            {selectOptions}
          </select>
        </div>
      </div>
    );
  }
});

export var FormTitleRow = React.createClass({
  render: function() {
    return (
      <div style={{marginTop: 30}}>
        <h3>
          {this.props.formTitle}
        </h3>
      </div>
    );
  }
});

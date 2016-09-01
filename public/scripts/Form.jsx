import React, { PropTypes } from 'react';

export const FormComponent = (props) => {
};

FormComponent.propTypes = {
  fields: PropTypes.object.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  resetForm: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired
};


export let Error = (props) => {
  let errorStyle = {
    color: 'darkred',
    fontStyle: 'italic'
  };

  if (props.touched && props.error) {
    return <div style={errorStyle}>{props.error}</div>;
  } else {
    return null;
  }
};

Error.propTypes = {
  error: PropTypes.string,
  touched: PropTypes.bool
};

export const Form = (props) => {
  let style = {
    paddingRight: '2em',
    error: {
      color: 'Red',
      background: 'Pink',
      fontStyle: 'italic',
      margin: '1em',
      padding: '0.5em',
      display: 'block-inline'
    }
  };
  return (
    <div style={style}>
      {props.error && <div style={style.error}>Error: {props.error}</div>}
      <form {...props} className="form-horizontal">
        {props.children}
      </form>
    </div>
  );
};
Form.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  error: PropTypes.string,
  children: PropTypes.oneOfType([
    PropTypes.element,
    PropTypes.arrayOf(PropTypes.element),
    PropTypes.arrayOf(PropTypes.node)
  ])
};

export const TextInput = (props) => {
  let textInputStyle = {
    paddingTop: 10,
  };

  return (
    <div className="form-group" style={textInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <input
        className="form-control"
        type="text"
        value={props.value || ''} {...props}
      />
      <Error {...props} />
    </div>
  );
};

TextInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.string
};

export const TextareaInput = (props) => {
  let textareaInputStyle = {
    paddingTop: 10,
  };

  return (
    <div className="form-group" style={textareaInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <textarea
        className="form-control"
        value={props.value || ''} {...props}
      />
      <Error {...props} />
    </div>
  );
};
TextareaInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.string
};

export const CheckBoxInput = (props) => (
  <div className="checkbox">
    <input type="checkbox" {...props} /> {props.label}
  </div>
);
CheckBoxInput.propTypes = {
  label: PropTypes.string
};

export const SelectInput = (props) => {
  let selectInputStyle = {
    paddingTop: 10
  };

  return (
    <div className="form-group" style={selectInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <select
        className="form-control"
        {...props}
      >
        {props.options.map((option, idx) => (
          <option
            value={option.id}
            key={option.id}
          >
            {option.label}
          </option>
         ))
        }
      </select>
      <Error {...props} />
    </div>
  );
};
SelectInput.propTypes = {
  label: PropTypes.string,
  options: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([
      PropTypes.number,
      PropTypes.string]).isRequired,
    label: PropTypes.string.isRequired
  })),
  value: PropTypes.any  // array of individual value
};


export const SubmitButton = (props) => {
  let submitButtonStyle = {
    paddingTop: 10
  };

  return (
    <div className="form-group" style={submitButtonStyle}>
      <button
        type="submit"
        className="btn btn-primary"
        disabled={props.disabled}
      >
        {props.label}
      </button>
    </div>
  );
};
SubmitButton.propTypes = {
  label: PropTypes.string,
  disabled: PropTypes.bool
};


export const FileInput = (props) => {
  let fileInputStyle = {
  };

  const { value: _, ...otherProps } = props;

  return (
    <div className="form-group" style={fileInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <input type="file" {...otherProps} />
      <Error {...props} />
    </div>
  );
};
FileInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.string
};


export const FormInputRow = (props) => (
  <div>
    <div style={{ width: 320, float: 'left', marginTop: 5 }}>
      {props.inputName}
    </div>
    <div style={{ marginLeft: 340, marginTop: 5 }}>
      <props.inputTag
        type={props.inputType}
        value={props.value}
        onChange={props.handleInputChange}
      />
    </div>
  </div>
);
FormInputRow.propTypes = {
  inputName: PropTypes.string,
  inputTag: PropTypes.string,
  inputType: PropTypes.string,
  value: PropTypes.string,
  handleInputChange: PropTypes.func
};


export const FormSelectInput = (props) => {
  let selectOptions = props.optionsList.map(option => (
    <option value={option.id} key={option.id}>
      {option.name}
    </option>
  ).bind(this));
  return (
    <div>
      <div style={{ width: 320, float: 'left', marginTop: 5 }}>
        {props.inputName}
      </div>
      <div style={{ marginLeft: 340, marginTop: 5 }}>
        <select
          value={props.value}
          onLoad={props.handleInputChange}
          onChange={props.handleInputChange}
        >
          {selectOptions}
        </select>
      </div>
    </div>
  );
};
FormSelectInput.propTypes = {
  optionsList: PropTypes.arrayOf(PropTypes.object),
  inputName: PropTypes.string,
  value: PropTypes.string,
  handleInputChange: PropTypes.func
};


export const FormTitleRow = (props) => (
  <div style={{ marginTop: 30 }}>
    <h3>
      {props.formTitle}
    </h3>
  </div>
);
FormTitleRow.propTypes = {
  formTitle: PropTypes.string
};

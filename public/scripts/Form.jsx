import React, { PropTypes } from 'react';

export const FormComponent = (props) => {
};

FormComponent.propTypes = {
  fields: PropTypes.object.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  resetForm: PropTypes.func.isRequired,
  submitting: PropTypes.bool.isRequired
};


export const Error = (props) => {
  const errorStyle = {
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
  const style = {
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
  const { error, ...formProps } = props; // eslint-disable-line
  return (
    <div style={style}>
      {props.error && <div style={style.error}>Error: {props.error}</div>}
      <form className="form-horizontal" {...formProps}>
        {props.children}
      </form>
    </div>
  );
};
Form.propTypes = {
  error: PropTypes.string,
  children: PropTypes.oneOfType([
    PropTypes.element,
    PropTypes.arrayOf(PropTypes.element),
    PropTypes.arrayOf(PropTypes.node)
  ])
};

export const TextInput = (props) => {
  const textInputStyle = {
    paddingTop: 10,
  };
  /* eslint-disable */
  const { error, initialValue, autofill, onUpdate, valid,
          invalid, dirty, pristine, active, touched, visited,
          autofilled, ...inputProps } = props;
  /* eslint-enable */

  return (
    <div className="form-group" style={textInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <input
        className="form-control"
        type="text"
        value={props.value || ''}
        {...inputProps}
      />
      <Error {...props} />
    </div>
  );
};

TextInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
};

export const TextareaInput = (props) => {
  const textareaInputStyle = {
    paddingTop: 10,
  };
  /* eslint-disable */
  const { error, initialValue, autofill, onUpdate, valid, invalid,
          dirty, pristine, active, touched, visited, autofilled,
          ...textareaProps } = props;
  /* eslint-enable */

  return (
    <div className="form-group" style={textareaInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <textarea
        className="form-control"
        value={props.value || ''}
        {...textareaProps}
      />
      <Error {...props} />
    </div>
  );
};
TextareaInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.string
};

export const CheckBoxInput = (props) => {
  /* eslint-disable */
  const { initialValue, autofill, onUpdate, valid, invalid,
          dirty, pristine, active, touched, visited, autofilled,
          divStyle, ...checkboxProps } = props;
  /* eslint-enable */

  return (
    <div className="checkbox" style={divStyle}>
      <input
        type="checkbox"
        {...checkboxProps}
      />
      {props.label}
    </div>
  );
};
CheckBoxInput.propTypes = {
  label: PropTypes.string,
  divStyle: PropTypes.object
};

export const SelectInput = (props) => {
  const selectInputStyle = {
    paddingTop: 10
  };
  /* eslint-disable */
  const { error, options, initialValue, autofill, onUpdate, valid,
          invalid, dirty, pristine, active, touched, visited, autofilled,
          ...selectProps } = props;
  /* eslint-enable */

  return (
    <div className="form-group" style={selectInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <select
        className="form-control"
        {...selectProps}
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
  /* eslint-disable react/no-unused-prop-types */
  options: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.oneOfType([
      PropTypes.number,
      PropTypes.string]),
    label: PropTypes.string.isRequired
  }))
  /* eslint-enable react/no-unused-prop-types */
};


export const SubmitButton = (props) => {
  const submitButtonStyle = {
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
  const fileInputStyle = {
  };

  /* eslint-disable */
  const { value: _, ...otherProps } = props;
  const { error, initialValue, autofill, onUpdate, valid, invalid, dirty,
          pristine, active, touched, visited, autofilled,
          ...inputProps } = otherProps;
  /* eslint-enable */

  return (
    <div className="form-group" style={fileInputStyle}>
      {props.label &&
        <label>{props.label}</label>
      }
      <input type="file" {...inputProps} />
      <Error {...props} />
    </div>
  );
};
FileInput.propTypes = {
  label: PropTypes.string,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.object
  ])
};

import React from 'react';
import PropTypes from 'prop-types';

const Delete = (props) => {
  const style = {
    display: 'inline-block'
  };
  return (
    <a
      style={style}
      onClick={
        (e) => {
          e.stopPropagation();
          props.delete(props.ID);
        }
              }
    >
      Delete {props.typeName}
    </a>
  );
};
Delete.propTypes = {
  ID: PropTypes.oneOfType([
    PropTypes.number,
    PropTypes.string]).isRequired,
  delete: PropTypes.func.isRequired,
  typeName: PropTypes.string
};
Delete.defaultProps = {
  typeName: ""
};

export default Delete;

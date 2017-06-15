import React from 'react';

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
  ID: React.PropTypes.oneOfType([
    React.PropTypes.number,
    React.PropTypes.string]).isRequired,
  delete: React.PropTypes.func.isRequired,
  typeName: React.PropTypes.string
};

export default Delete;

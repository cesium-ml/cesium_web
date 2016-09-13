import React from 'react';
import colorScheme from './colorscheme';

const cs = colorScheme;

const Dot = (props) => {
  let value = props.value;
  if (value === undefined) {
    value = '···';
  }

  let height = props.height;
  if (height === undefined) {
    height = '1em';
  }

  const style = {
    display: 'inline-block',
    padding: 0,
    margin: 0,
    textAlign: 'center',
    verticalAlign: 'middle',
    whiteSpace: 'nowrap',
    backgroundColor: cs.lightBlue,
    borderRadius: '50%',
    border: '2px solid gray',
    position: 'relative',
    height,
    width: height,
    lineHeight: height,
    fontSize: '150%',
    ...(props.style)
  };

  return (
    <div style={style}>{value}</div>
  );
};
Dot.propTypes = {
  value: React.PropTypes.string.isRequired,
  style: React.PropTypes.object,
  height: React.PropTypes.string
};

export default Dot;

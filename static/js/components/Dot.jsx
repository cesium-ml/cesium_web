import React from 'react';
import PropTypes from 'prop-types';
import colorScheme from './colorscheme';

const cs = colorScheme;

const Dot = (props) => {
  let { value, height } = { ...props };
  if (value === undefined) {
    value = '···';
  }

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
  /* eslint-disable react/no-unused-prop-types */
  value: PropTypes.string.isRequired,
  style: PropTypes.object,
  height: PropTypes.string
  /* eslint-enable react/no-unused-prop-types */
};
Dot.defaultProps = {
  style: {},
  height: ""
};

export default Dot;

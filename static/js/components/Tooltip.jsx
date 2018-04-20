import React from 'react';
import PropTypes from 'prop-types';
import ReactTooltip from 'react-tooltip';

const CesiumTooltip = props => (
  <ReactTooltip place={props.place} delayShow={props.delay} id={props.id}>
    <span>
      {props.text}
    </span>
  </ReactTooltip>
);
CesiumTooltip.propTypes = {
  id: PropTypes.string.isRequired,
  text: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.array
  ]).isRequired,
  place: PropTypes.string,
  delay: PropTypes.number
};
CesiumTooltip.defaultProps = {
  place: 'top',
  delay: 700
};
export default CesiumTooltip;

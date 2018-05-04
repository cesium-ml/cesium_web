import React from 'react';
import PropTypes from 'prop-types';


const Download = (props) => {
  const style = {
    display: 'inline-block'
  };
  return (
    <a
      href={props.url}
      style={style}
      onClick={
        (e) => {
          e.stopPropagation();
        }
      }
    >
      Download
    </a>
  );
};
Download.propTypes = {
  url: PropTypes.string.isRequired
};

export default Download;

import React from 'react';

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
  ID: React.PropTypes.oneOfType([
    React.PropTypes.number,
    React.PropTypes.string]).isRequired,
  url: React.PropTypes.string.isRequired
};

export default Download;

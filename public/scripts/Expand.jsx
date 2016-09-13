import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { toggleExpander } from './actions';
import Dot from './Dot';


let Expand = (props) => {
  const style = {
    a: { textDecoration: 'none' },
    sign: {
      fontSize: '200%',
      fontWeight: 'bold'
    },
    children: {
      position: 'relative',
      width: '100%',
      zIndex: 1000,
      background: 'white',
      border: '1px solid LightGray',
      paddingLeft: '2em',
      marginTop: '0.5em',
      marginBottom: '1em',
      ...(props.expandBoxStyle)
    },
    ...(props.style)
  };

  const add = (
    <span>
      <span style={style.sign}>
        <Dot height="0.7em" value="+" style={style.dot} />
      </span>
      {props.label}
    </span>);

  const shrink = (
    <span>
      <span style={style.sign}>
        <Dot height="0.7em" value="-" style={style.dot} />
      </span>
      {props.label}
    </span>);

  return (
    <div style={{ ...style, ...(props.style) }}>

      <a style={style.a} onClick={props.toggle}>
        { props.opened ? shrink : add }
      </a>

      {
        (props.opened) &&
          <div style={style.children}>
            {props.opened ? props.children : null}
          </div>
      }

    </div>
  );
};
Expand.propTypes = {
  expandBoxStyle: PropTypes.object,
  style: PropTypes.object,
  label: PropTypes.string,
  toggle: PropTypes.func,
  opened: PropTypes.bool,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.oneOfType([
      PropTypes.node, PropTypes.element])),
    PropTypes.node, PropTypes.element])
};

const mapStateToProps = (state, ownProps) => (
  {
    opened: state.expander.opened[ownProps.id]
  }
);

const mapDispatchToProps = (dispatch, ownProps) => (
  {
    toggle: () => { dispatch(toggleExpander(ownProps.id)); }
  }
);

Expand = connect(mapStateToProps, mapDispatchToProps)(Expand);

export default Expand;

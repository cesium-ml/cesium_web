import React from 'react'
import {connect} from 'react-redux'

export var Notifications = (props) => {
  let style = {
    background: 'MediumSeaGreen',
    color: 'white',
    fontWeight: 'bold',
    paddingTop: '0.8em',
    paddingBottom: '0.2em',

    position: 'absolute',
    zIndex: 3,
    top: 10,
    width: 750,
    textAlign: 'center',
    lineHeight: props.notifications.length,
    overflow: 'hidden',
    WebkitBoxShadow: '0 0 5px black',
    MozBoxShadow: '0 0 5px black',
    boxShadow: '0 0 5px black'
  }

  return (
    (props.notifications.length > 0) &&
      <div style={style}>
        <ul>
          {props.notifications.map((note, idx) => (
            <li>{note}</li>
          ))}
        </ul>
      </div>
  );
}

var mapStateToProps = (state) => {
  return {
    notifications: state.notifications.notes
  }
}

Notifications = connect(mapStateToProps)(Notifications);

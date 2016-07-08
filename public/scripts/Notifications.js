import React from 'react'
import {connect} from 'react-redux'

export var Notifications = (props) => {
  let style = {
    position: 'fixed',
    zIndex: 3,
    top: 10,
    width: 300,
    left: 850,
    overflow: 'hidden',

    note: {
      color: 'white',
      fontWeight: 'bold',
      paddingTop: '0.8em',
      paddingBottom: '0.8em',
      paddingLeft: '1em',
      marginBottom: 5,
      background: 'MediumAquaMarine',
      width: '100%',
      display: 'inline-block',
      WebkitBoxShadow: '0 0 5px black',
      MozBoxShadow: '0 0 5px black',
      boxShadow: '0 0 5px black'
    }
  }

  return (
    (props.notifications.length > 0) &&
      <div style={style}>
        {props.notifications.map((note, idx) => (
          <div key={idx} style={style.note}>{note}</div>
        ))}
      </div>
  );
}

var mapStateToProps = (state) => {
  return {
    notifications: state.notifications.notes
  }
}

Notifications = connect(mapStateToProps)(Notifications);

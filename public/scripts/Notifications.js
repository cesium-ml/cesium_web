import React from 'react'
import {connect} from 'react-redux'
import {promiseAction} from './action_tools'


export var Notifications = (props) => {
  let style = {
    position: 'fixed',
    zIndex: 20000,
    top: '4.5em',
    width: '30em',
    right: '1em',
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
        {props.notifications.map((notification, idx) => (
          <div key={notification.id} style={style.note}
               onClick={() => props.dispatch(hideNotification(notification.id))}>
            {notification.note}
          </div>
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


export const SHOW_NOTIFICATION = 'cesium/SHOW_NOTIFICATION'
export const HIDE_NOTIFICATION = 'cesium/HIDE_NOTIFICATION'

let nextNotificationId = 0
export function showNotification(note) {
  let thisId = nextNotificationId++;
  return (dispatch) => {
    dispatch({
      type: SHOW_NOTIFICATION,
      payload: {
        id: thisId,
        note
      }
    })
    setTimeout(() => dispatch(hideNotification(thisId)), 2000);
  }
}

export function hideNotification(id) {
  return {
    type: HIDE_NOTIFICATION,
    payload: {id}
  }
}

export function reducer(state={notes: []}, action) {
  switch (action.type) {
    case SHOW_NOTIFICATION:
      let {id, note} = action.payload;
      return {
        notes: state.notes.concat({id, note})
      }
    case HIDE_NOTIFICATION:
      return {
        notes: state.notes.filter(n => (n.id != action.payload.id))
      }
    default:
      return state
  }
}

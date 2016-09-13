import React from 'react';
import { connect } from 'react-redux';


export const SHOW_NOTIFICATION = 'cesium/SHOW_NOTIFICATION';
export const HIDE_NOTIFICATION = 'cesium/HIDE_NOTIFICATION';

export function hideNotification(id) {
  return {
    type: HIDE_NOTIFICATION,
    payload: { id }
  };
}

export let Notifications = (props) => {
  const style = {
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
      width: '100%',
      display: 'inline-block',
      WebkitBoxShadow: '0 0 5px black',
      MozBoxShadow: '0 0 5px black',
      boxShadow: '0 0 5px black'
    }
  };


  const noteColor = {
    error: 'Crimson',
    info: 'MediumAquaMarine'
  };

  return (
    (props.notifications.length > 0) &&
      <div style={style}>
        {
          props.notifications.map((notification, idx) => (
            <div
              key={notification.id}
              style={{ ...style.note, background: noteColor[notification.type] }}
              onClick={() => props.dispatch(hideNotification(notification.id))}
            >
              {notification.note}
            </div>
          ))
        }
      </div>
  );
};

const mapStateToProps = state => (
  {
    notifications: state.notifications.notes
  }
);

Notifications = connect(mapStateToProps)(Notifications);


let nextNotificationId = 0;
export function showNotification(note, type='info') {
  const thisId = nextNotificationId++;

  if (type === 'error') {
    console.error(note);
  }

  return (dispatch) => {
    dispatch({
      type: SHOW_NOTIFICATION,
      payload: {
        id: thisId,
        note,
        type
      }
    });
    setTimeout(() => dispatch(hideNotification(thisId)), 3000);
  };
}

export function reducer(state={ notes: [] }, action) {
  switch (action.type) {
    case SHOW_NOTIFICATION: {
      let { id, note, type } = action.payload;
      return {
        notes: state.notes.concat({ id, note, type })
      };
    }
    case HIDE_NOTIFICATION:
      return {
        notes: state.notes.filter(n => (n.id !== action.payload.id))
      };
    default:
      return state;
  }
}

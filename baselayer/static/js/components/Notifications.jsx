import React from 'react';
import { connect } from 'react-redux';


export const SHOW_NOTIFICATION = 'baselayer/SHOW_NOTIFICATION';
export const HIDE_NOTIFICATION = 'baselayer/HIDE_NOTIFICATION';
export const HIDE_NOTIFICATION_BY_TAG = 'baselayer/HIDE_NOTIFICATION_BY_TAG';

export const MS_PER_YEAR = 31540000000;


export function hideNotification(id) {
  return {
    type: HIDE_NOTIFICATION,
    payload: { id }
  };
}

export function hideNotificationByTag(tag) {
  return (dispatch) => {
    dispatch(
      {
        type: HIDE_NOTIFICATION_BY_TAG,
        payload: { tag }
      }
    );
    return Promise.resolve();
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
    warning: 'Orange',
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
export function showNotification(note, type='info', duration=3000, tag='default') {
  const thisId = nextNotificationId++;

  if (type === 'error') {
    console.error(note);
  }

  return (dispatch) => {
    dispatch({
      type: SHOW_NOTIFICATION,
      payload: {
        id: thisId,
        note: note,
        type: type,
        tag: tag
      }
    });
    setTimeout(() => dispatch(hideNotification(thisId)), duration);
  };
}

export function reducer(state={ notes: [] }, action) {
  switch (action.type) {
    case SHOW_NOTIFICATION: {
      let { id, note, type, tag } = action.payload;
      return {
        notes: state.notes.concat({ id, note, type, tag })
      };
    }
    case HIDE_NOTIFICATION:
      return {
        notes: state.notes.filter(n => (n.id !== action.payload.id))
      };
    case HIDE_NOTIFICATION_BY_TAG:
      return {
        notes: state.notes.filter(n => (n.tag !== action.payload.tag))
      }
    default:
      return state;
  }
}

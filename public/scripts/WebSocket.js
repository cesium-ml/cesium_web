import React from 'react'
import { connect } from 'react-redux'
import { createCookie, readCookie, eraseCookie} from './cookies'
import ReconnectingWebSocket from './reconnecting-websocket'


function getTime() {
  var date = new Date();
  var n = date.toDateString();
  return date.toLocaleTimeString();
};


function checkStatus(response) {
  if (response.status >= 200 && response.status < 300) {
    return response
  } else {
    var error = new Error(response.statusText)
    error.response = response
    throw error
  }
}

function parseJSON(response) {
  return response.json()
}


function getAuthToken(auth_url) {
  return new Promise(
    (resolve, reject) => {
      // First, try and read the authentication token from a cookie
      let cookie_token = readCookie('auth_token');

      if (cookie_token) {
        resolve(cookie_token);
      } else {
        fetch(auth_url)
          .then(checkStatus)
          .then(parseJSON)
          .then(json => {
            let token = json['data']['token'];
            createCookie('auth_token', token);
            resolve(token);
          }
          ).catch( error => {
            // If we get a gateway error, it probably means nginx is
            // being restarted. Not much we can do, other than wait a
            // bit and continue with a fake token.
            let no_token = "no_auth_token_user bad_token";
            setTimeout(function() { resolve(no_token); }, 1000);
          });
      }
    }
  );
};


class WebSocket extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      connected: false,
      authenticated: false
    }

    var ws = new ReconnectingWebSocket(props.url);

    ws.onopen = event => {
      this.setState({connected: true});
    };

    ws.onmessage = event => {
      var message = event.data;

      // Ignore heartbeat signals
      if (message === '<3') {
        return;
      }

      var data = JSON.parse(message);
      var action = data["action"];

      switch (action) {
        case "AUTH REQUEST":
          getAuthToken(this.props.auth_url)
            .then(token => ws.send(token));
          break;
        case "AUTH FAILED":
          this.setState({authenticated: false});
          eraseCookie('auth_token');
          break;
        case "AUTH OK":
          this.setState({authenticated: true});
          break;
        default:
          this.props.messageHandler(data);
      }
    };

    ws.onclose = event => {
      this.setState({connected: false,
                     authenticated: false});
    };

  }

  render() {
    let statusColor;
    if (!this.state.connected) {
      statusColor = 'red';
    } else {
      statusColor = this.state.authenticated ? 'lightgreen' : 'orange';
    }

    let statusSize = 12;

    let statusStyle = {
      display: 'inline-block',
      padding: 0,
      lineHeight: statusSize,
      textAlign: 'center',
      whiteSpace: 'nowrap',
      verticalAlign: 'baseline',
      backgroundColor: statusColor,
      borderRadius: '50%',
      border: '2px solid gray',
      position: 'relative',
      height: statusSize,
      width: statusSize,
      padding: 0
    }

    let connected_desc = ('WebSocket is ' +
      (this.state.connected ? 'connected' : 'disconnected') + ' & ' +
      (this.state.authenticated ? 'authenticated' : 'unauthenticated') + '.');
    return (
      <div id="websocketStatus"
           title={connected_desc}
      style={statusStyle}>
      </div>
    );
  }

}

WebSocket.propTypes = {
  url: React.PropTypes.string.isRequired,
  auth_url: React.PropTypes.string.isRequired
};

module.exports = WebSocket;

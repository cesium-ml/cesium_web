import { SHOW_NOTIFICATION, showNotification } from './components/Notifications';

class MessageHandler {
  constructor(dispatch, handler) {
    this.dispatch = dispatch;
    this.handle = message => {
      switch (message.action) {
        case SHOW_NOTIFICATION:
          this.dispatch(showNotification(message.payload.note,
                                         message.payload.type));
          break;
        default:
          handler(message);
      }
    }
  }
}

export default MessageHandler;

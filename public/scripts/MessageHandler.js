import * as Action from './actions';

export class MessageHandler {
  constructor(dispatch) {
    this.dispatch = dispatch;
    this.handle = this.handle.bind(this);
  }

  handle(message) {
    switch (message.action) {
      case Action.FETCH_PROJECTS:
        this.dispatch(Action.fetchProjects());
    }
  }
}

module.exports = MessageHandler;

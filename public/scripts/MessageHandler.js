import * as Action from './actions';

export class MessageHandler {
  constructor(dispatch) {
    this.dispatch = dispatch;
    this.handle = this.handle.bind(this);
  }

  handle(message) {
    console.log('Message received:', message);
    switch (message.action) {
      case Action.FETCH_PROJECTS:
        this.dispatch(Action.fetchProjects());
      case Action.FETCH_FEATURESETS:
        this.dispatch(Action.fetchFeaturesets());
    }
  }
}

module.exports = MessageHandler;

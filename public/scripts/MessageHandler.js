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
      case Action.FETCH_FEATURESETS:
        this.dispatch(Action.fetchFeaturesets());
      case Action.FETCH_DATASETS:
        this.dispatch(Action.fetchDatasets());
      case Action.FETCH_FEATURESETS:
        this.dispatch(Action.fetchFeaturesets());
      case Action.FETCH_MODELS:
        this.dispatch(Action.fetchModels());
      case Action.FETCH_PREDICTIONS:
        this.dispatch(Action.fetchPredictions());
      default:
        console.log('Unknown message received through flow:',
                    message)
    }
  }
}

module.exports = MessageHandler;

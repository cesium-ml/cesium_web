import * as Action from './actions';
import { SHOW_NOTIFICATION, showNotification } from './Notifications';

class MessageHandler {
  constructor(dispatch) {
    this.dispatch = dispatch;
    this.handle = this.handle.bind(this);
  }

  handle(message) {
    switch (message.action) {
      case Action.FETCH_PROJECTS:
        this.dispatch(Action.fetchProjects());
        break;
      case Action.FETCH_FEATURES:
        this.dispatch(Action.fetchFeatures());
        break;
      case Action.FETCH_DATASETS:
        this.dispatch(Action.fetchDatasets());
        break;
      case Action.FETCH_FEATURESETS:
        this.dispatch(Action.fetchFeaturesets());
        break;
      case Action.FETCH_MODELS:
        this.dispatch(Action.fetchModels());
        break;
      case Action.FETCH_PREDICTIONS:
        this.dispatch(Action.fetchPredictions());
        break;
      case SHOW_NOTIFICATION:
        this.dispatch(showNotification(message.payload.note,
                                       message.payload.type));
        break;
      default:
        console.log('Unknown message received through flow:',
                    message);
    }
  }
}

export default MessageHandler;

import { SHOW_NOTIFICATION, showNotification } from 'baselayer/components/Notifications';
import MessageHandler from 'baselayer/MessageHandler';
import * as Action from './actions';

const CesiumMessageHandler = (dispatch) => new MessageHandler(dispatch, (message) => {
  switch (message.action) {
    case Action.FETCH_PROJECTS:
      dispatch(Action.fetchProjects());
      break;
    case Action.FETCH_FEATURES:
      dispatch(Action.fetchFeatures());
      break;
    case Action.FETCH_DATASETS:
      dispatch(Action.fetchDatasets());
      break;
    case Action.FETCH_FEATURESETS:
      dispatch(Action.fetchFeaturesets());
      break;
    case Action.FETCH_MODELS:
      dispatch(Action.fetchModels());
      break;
    case Action.FETCH_PREDICTIONS:
      dispatch(Action.fetchPredictions());
      break;
    case Action.FEATURIZE_PROGRESS: {
      const time_update = message.payload;
      dispatch(Action.featurizeUpdateProgress(time_update));
      break;
    }
    default:
      console.log('Unknown message received through flow:',
        message);
  }
});

export default CesiumMessageHandler;

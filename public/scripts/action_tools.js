export default function promiseAction(dispatch, action_type, promise) {
  dispatch({
    type: action_type,
    payload: {
      promise
    }
  });
  return promise;
}

export function promiseAction(dispatch, action_type, promise) {
  dispatch({
    type: action_type,
    payload: {
      promise: promise
    }
  });
  return promise;
}

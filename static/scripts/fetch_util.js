/* TODO: looks like this is currently unused */

function post(url, data) {
  return fetch(url, {
    credentials: 'same-origin',
    method: 'POST',
    mode: 'cors',
    headers: {
      'Accept': 'Application/JSON, text/plain',
      'Content-Type': 'x-www-urlencoded'
    },
    data,
  });
}

export default post;

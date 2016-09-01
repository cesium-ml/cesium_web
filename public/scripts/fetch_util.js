function post(url, data) {
  return fetch(url, {
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

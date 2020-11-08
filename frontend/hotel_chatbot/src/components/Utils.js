const SERVER_HOSTNAME = 'http://localhost';
const SERVER_PORT = '5005';

export const post = async (url, body, { getResult = true } = {}) => {
  let response = await fetch(`${SERVER_HOSTNAME}:${SERVER_PORT}${url}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-cache',
    body: JSON.stringify(body)
  });
  if (response.ok) {
    if (getResult) {
      let result = await response.json();
      return result;
    }
  } else {
    throw new Error('POST error: ' + response.status);
  }
}

export const get = async (url, type = 'json') => {
  let response = await fetch(`${SERVER_HOSTNAME}:${SERVER_PORT}${url}`, {
    method: 'GET',
    headers: {
      'Content-Type': `application/${type}`,
    },
    cache: 'no-cache'
  });
  if (response.ok && type === 'json') {
    let result = await response.json();
    return result;
  } else if (response.ok && type !== 'json') {
    return response;
  } else {
    throw new Error('GET error: ' + response.status);
  }
}

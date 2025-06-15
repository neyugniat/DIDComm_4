import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 16,
  duration: '60s',
};

export default function () {
  const url = 'http://localhost:5000/presentations/send-request';

  const payload = JSON.stringify({});

  const params = {
    headers: {
      'Content-Type': 'application/json'
    }
  };

  let res = http.post(url, payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response is not empty': (r) => r.body && r.body.length > 0,
  });
}

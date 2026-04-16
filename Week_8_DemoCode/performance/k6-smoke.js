import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '20s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:5000';

export default function () {
  const healthRes = http.get(`${baseUrl}/health`);
  check(healthRes, {
    'health status 200': (r) => r.status === 200,
  });

  const payload = JSON.stringify({ message: 'k6-load-test' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const echoRes = http.post(`${baseUrl}/api/echo`, payload, params);

  check(echoRes, {
    'echo status 200': (r) => r.status === 200,
    'echo returns message': (r) => r.json('message') === 'k6-load-test',
  });

  sleep(1);
}

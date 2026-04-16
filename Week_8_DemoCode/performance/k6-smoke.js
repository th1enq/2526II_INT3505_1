import http from 'k6/http';
import { check, group, sleep } from 'k6';

export const options = {
  scenarios: {
    smoke_api: {
      executor: 'constant-vus',
      vus: 10,
      duration: '20s',
      exec: 'smokeScenario',
    },
    functional_crud: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 3,
      exec: 'crudScenario',
      startTime: '1s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<500'],
    checks: ['rate>0.99'],
  },
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:5000';
const jsonParams = {
  headers: {
    'Content-Type': 'application/json',
  },
};

http.setResponseCallback(http.expectedStatuses(200, 201, 204, 400, 404));

function parseJson(response) {
  try {
    return response.json();
  } catch (error) {
    return null;
  }
}

export function smokeScenario() {
  group('stateless endpoints', () => {
    const healthRes = http.get(`${baseUrl}/health`);
    check(healthRes, {
      'health status is 200': (response) => response.status === 200,
      'health body is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.status === 'ok' && body.service === 'flask-demo';
      },
    });

    const infoRes = http.get(`${baseUrl}/api/info`);
    check(infoRes, {
      'info status is 200': (response) => response.status === 200,
      'info body is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.name === 'flask-demo' && body.version === '1.0.0';
      },
    });

    const echoPayload = JSON.stringify({ message: 'k6-load-test' });
    const echoRes = http.post(`${baseUrl}/api/echo`, echoPayload, jsonParams);
    check(echoRes, {
      'echo status is 200': (response) => response.status === 200,
      'echo returns message': (response) => {
        const body = parseJson(response);
        return body !== null && body.message === 'k6-load-test';
      },
      'echo returns timestamp': (response) => {
        const body = parseJson(response);
        return body !== null && typeof body.received_at === 'string' && body.received_at.length > 0;
      },
    });

    const sumPayload = JSON.stringify({ numbers: [1, 2.5, 3] });
    const sumRes = http.post(`${baseUrl}/api/math/sum`, sumPayload, jsonParams);
    check(sumRes, {
      'sum status is 200': (response) => response.status === 200,
      'sum response is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.count === 3 && body.sum === 6.5;
      },
    });
  });

  sleep(1);
}

export function crudScenario() {
  group('validation checks', () => {
    const echoInvalidRes = http.post(`${baseUrl}/api/echo`, JSON.stringify({}), jsonParams);
    check(echoInvalidRes, {
      'echo invalid status is 400': (response) => response.status === 400,
      'echo invalid error is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.error === "Field 'message' is required";
      },
    });

    const sumEmptyRes = http.post(
      `${baseUrl}/api/math/sum`,
      JSON.stringify({ numbers: [] }),
      jsonParams
    );
    check(sumEmptyRes, {
      'sum empty status is 400': (response) => response.status === 400,
      'sum empty error is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.error === "Field 'numbers' must be a non-empty list";
      },
    });

    const sumInvalidTypeRes = http.post(
      `${baseUrl}/api/math/sum`,
      JSON.stringify({ numbers: [1, '2', 3] }),
      jsonParams
    );
    check(sumInvalidTypeRes, {
      'sum non numeric status is 400': (response) => response.status === 400,
      'sum non numeric error is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.error === "All elements in 'numbers' must be numeric";
      },
    });

    const missingItemRes = http.get(`${baseUrl}/api/items/999999`);
    check(missingItemRes, {
      'missing item status is 404': (response) => response.status === 404,
      'missing item error is correct': (response) => {
        const body = parseJson(response);
        return body !== null && body.error === 'Item not found';
      },
    });
  });

  group('stateful CRUD checks', () => {
    const uniqueName = `k6-item-${__VU}-${__ITER}`;

    const createRes = http.post(
      `${baseUrl}/api/items`,
      JSON.stringify({ name: `  ${uniqueName}  ` }),
      jsonParams
    );
    const createdBody = parseJson(createRes);
    const createdId = createdBody !== null ? createdBody.id : null;

    check(createRes, {
      'create item status is 201': (response) => response.status === 201,
      'create item trims name': () =>
        createdBody !== null &&
        createdBody.name === uniqueName &&
        typeof createdBody.created_at === 'string' &&
        createdBody.created_at.length > 0,
    });

    const listRes = http.get(`${baseUrl}/api/items`);
    check(listRes, {
      'list items status is 200': (response) => response.status === 200,
      'list contains created item': (response) => {
        const items = parseJson(response);
        return (
          Array.isArray(items) &&
          createdId !== null &&
          items.some((item) => item.id === createdId && item.name === uniqueName)
        );
      },
    });

    const getRes = http.get(`${baseUrl}/api/items/${createdId}`);
    check(getRes, {
      'get item status is 200': (response) => response.status === 200,
      'get item returns created data': (response) => {
        const body = parseJson(response);
        return body !== null && body.id === createdId && body.name === uniqueName;
      },
    });

    const deleteRes = http.del(`${baseUrl}/api/items/${createdId}`);
    check(deleteRes, {
      'delete item status is 204': (response) => response.status === 204,
      'delete item body is empty': (response) => response.body === '' || response.body === null,
    });

    const deletedGetRes = http.get(`${baseUrl}/api/items/${createdId}`);
    check(deletedGetRes, {
      'deleted item get status is 404': (response) => response.status === 404,
      'deleted item is not found': (response) => {
        const body = parseJson(response);
        return body !== null && body.error === 'Item not found';
      },
    });
  });
}

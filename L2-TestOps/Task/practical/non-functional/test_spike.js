import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '10s', target: 10 },  // Ramp up to 10 users
        { duration: '30s', target: 200 }, // Spike to 200 users
        { duration: '10s', target: 10 },  // Ramp down to 10 users
        { duration: '10s', target: 0 },   // Ramp down to 0 users
    ],
};

export default function () {
    const url = 'https://www.xenonstack.com/';
    let res = http.get(url);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'transaction time OK': (r) => r.timings.duration < 2000,
    });

    sleep(1);
}

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 100 }, // Ramp up to 100 users over 2 minutes
        { duration: '3m', target: 200 }, // Stay at 200 users for 3 minutes
        { duration: '1m', target: 0 },   // Ramp down to 0 users
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

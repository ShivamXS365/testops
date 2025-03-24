import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 50, // Number of virtual users
    duration: '1m', // Duration of the test
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

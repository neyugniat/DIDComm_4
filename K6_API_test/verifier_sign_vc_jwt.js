import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 16,
  duration: '60s',
};

export default function () {
  const url = 'http://localhost:5000/jwt-credentials/sign-vc-jwt';

  const payload = JSON.stringify({
    did: "did:sov:FtTjFwhSg9fowokNhfYfWV",
    payload: {
      iss: "did:sov:FtTjFwhSg9fowokNhfYfWV",
      sub: "did:key:z6Mkgq7Jb9384WwDV7hVyKMerSJn64KGkSnjfBsJ7q52ZHiM",
      vc: {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        type: ["VerifiableCredential", "UniversityDegreeCredential"],
        credentialSubject: {
          id: "did:key:z6Mkgq7Jb9384WwDV7hVyKMerSJn64KGkSnjfBsJ7q52ZHiM",
          name: "Nguyễn Tài Nguyên",
          degree: "Bachelor of Information Security",
          status: "graduated",
          graduationDate: "2025-07-16"
        }
      },
      exp: 1749029648,
      iat: 1749026048
    }
  });

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

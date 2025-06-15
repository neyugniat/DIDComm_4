import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 16,
  duration: '60s',
};

export default function () {
  const url = 'http://localhost:5000/issue-credentials/proposal';

  const payload = JSON.stringify({
    comment: "Hello testing-Issuer, I want the VC to have these information",
    connection_id: "e4754789-ff00-457f-bebe-eca5a6585be2",
    credential_preview: {
      "@type": "https://didcomm.org/issue-credential/2.0/credential-preview",
      attributes: [
        { name: "ten", value: "Nguyễn Tài Nguyên" },
        { name: "chuyen_khoa", value: "Đa khoa" },
        { name: "benh_vien", value: "Thủ Đức" }
      ]
    },
    filter: {
      indy: {
        cred_def_id: "FtTjFwhSg9fowokNhfYfWV:3:CL:20:default"
      }
    },
    auto_remove: false
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

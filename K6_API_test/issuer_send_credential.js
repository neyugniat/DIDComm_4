import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 16,
  duration: '60s',
};

export default function () {
  const url = 'http://localhost:5000/issue-credentials/send_credential';

  const payload = JSON.stringify({
    auto_remove: true,
    comment: "Cấp bằng bác sĩ cho Nguyễn Tài Nguyên",
    connection_id: "2c3424dd-01b4-4d74-962a-6052561a24b9",
    credential_preview: {
      "@type": "issue-credential/2.0/credential-preview",
      attributes: [
        { name: "ten", value: "Nguyễn Tài Nguyên" },
        { name: "chuyen_khoa", value: "Đa Khoa" },
        { name: "benh_vien", value: "Thủ Đức" }
      ]
    },
    filter: {
      indy: {
        cred_def_id: "FtTjFwhSg9fowokNhfYfWV:3:CL:20:default",
        issuer_did: "FtTjFwhSg9fowokNhfYfWV",
        schema_id: "FtTjFwhSg9fowokNhfYfWV:2:Bang_bac_si:1.0",
        schema_issuer_did: "FtTjFwhSg9fowokNhfYfWV",
        schema_name: "Bang_bac_si",
        schema_version: "1.0"
      }
    },
    trace: false
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

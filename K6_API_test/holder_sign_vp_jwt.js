import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 16,
  duration: '60s',
};

export default function () {
  const url = 'http://localhost:5000/jwt-credentials/sign-vp-jwt';

  const payload = JSON.stringify({
    did: "did:key:z6MkweAETmHifZXBPYCniY6Q7E1qw3UAzEwT32LAM8QucBnj",
    verkey: "JBuBsX3HL22iH3N62y8ZG8Tr7UCKaMh6M1REWrStgy1M",
    payload: {
      iss: "did:key:z6MkweAETmHifZXBPYCniY6Q7E1qw3UAzEwT32LAM8QucBnj",
      aud: "did:sov:F7nqeXQyXSefUNGS88USEd",
      vp: {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        type: ["VerifiablePresentation"],
        verifiableCredential: [
          "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJFZERTQSIsICJraWQiOiAiZGlkOnNvdjpGdFRqRndoU2c5Zm93b2tOaGZZZldWI2tleS0xIn0.eyJpc3MiOiAiZGlkOnNvdjpGdFRqRndoU2c5Zm93b2tOaGZZZldWIiwgInN1YiI6ICJkaWQ6a2V5Ono2TWtncTdKYjkzODRXd0RWN2hWeUtNZXJTSm42NEtHa1NuamZCc0o3cTUyWkhpTSIsICJ2YyI6IHsiY29udGV4dCI6IFsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3JlZGVudGlhbHMvdjEiXSwgInR5cGUiOiBbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwgIlVuaXZlcnNpdHlEZWdyZWVDcmVkZW50aWFsIl0sICJjcmVkZW50aWFsU3ViamVjdCI6IHsiaWQiOiAiZGlkOmtleTp6Nk1rZ3E3SmI5Mzg0V3dEVjdoVnlLTWVyU0puNjRLR2tYmpmQnNKN3E1MlpIaU0iLCAibmFtZSI6ICJOZ3V5XHUxZWM1biBUXHUwMGVhIG5cXHUwMGVhbiIsICJkZWdyZWUiOiAiQmFjaGVsb3Igb2YgSW5mb3JtYXRpb24gU2VjdXJpdHkiLCAic3RhdHVzIjogImdyYWR1YXRlZCIsICJncmFkdWF0aW9uRGF0ZSI6ICIyMDI1LTA3LTE2In19LCAiZXhwIjogMTc0OTAyOTY0OCwgImlhdCI6IDE3NDkwMjYwNDh9.7gVc28C3P4RC_ufDu9YV3J8VUF3L4KXbhTmNihmnfhMVbetvpXb9hVcNbXY0KaCYF8GRNx-Ru01hgMptIrA-BQ"
        ]
      },
      exp: 1749651728,
      iat: 1749551728,
      cnf: {}
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

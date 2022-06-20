export class Session {
  auth = ['', ''];
  verify = false;

  async request(method, url, data = {}) {
    const [username, password] = this.auth;
    const body = JSON.stringify(data);

    const resp = await new Promise((resolve) => {
      Window.this.xcall(
        'fetch',
        url,
        method,
        username,
        password,
        body,
        this.verify,
        resolve
      );
    });

    const result = resp === '{}' || resp === '' ? null : JSON.parse(resp);
    return result;
  }
}

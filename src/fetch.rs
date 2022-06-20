use http::Method;

pub fn fetch(
    url: String,
    method: String,
    username: String,
    password: String,
    body: String,
    verify: bool
) -> String {
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(5)) // not sure if this is bugged or what
        .danger_accept_invalid_certs(!verify)
        .build()
        .unwrap();

    let resp = client
        .request(Method::from_bytes(method.to_uppercase().as_bytes()).unwrap(), url)
        .basic_auth(username, Some(password))
        .body(body)
        .send();

    match resp {
      Ok(resp) => resp.text().unwrap(),
      Err(e) => {
        println!("{}", e);
        return String::from("{}");
      }
    }
}

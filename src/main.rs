#![windows_subsystem = "windows"]
#[macro_use]
extern crate sciter;
use sciter::Value;
mod fetch;
mod proc_utils;

struct EventHandler;
impl EventHandler {
    fn fetch(
        &self,
        url: String,
        method: String,
        username: String,
        password: String,
        body: String,
        verify: bool,
        callback: Value,
    ) -> () {
        std::thread::spawn(move || {
            let resp = fetch::fetch(url, method, username, password, body, verify);
            callback.call(None, &make_args!(resp), None).unwrap();
        });
    }
    fn find_lcu_process(&self, callback: Value) -> () {
        match proc_utils::find_lcu_process() {
            Some(league_process) => {
                let parsed_cmdline_args = proc_utils::parse_cmdline_args(league_process.cmd);

                let mut cmd_map = Value::map();
                for parsed_cmdline_arg in parsed_cmdline_args {
                    cmd_map.set_item(parsed_cmdline_arg.0, parsed_cmdline_arg.1);
                }

                let mut process = Value::map();
                process.set_item("cmd", cmd_map);

                callback.call(None, &make_args!(process), None).unwrap();
            }
            None => {
                callback.call(None, &make_args!(false), None).unwrap();
            }
        };
    }
}

impl sciter::EventHandler for EventHandler {
    fn document_complete(&mut self, _root: sciter::HELEMENT, _source: sciter::HELEMENT) {}
    fn get_subscription(&mut self) -> Option<sciter::dom::event::EVENT_GROUPS> {
        Some(
            sciter::dom::event::default_events()
                | sciter::dom::event::EVENT_GROUPS::HANDLE_METHOD_CALL,
        )
    }
    dispatch_script_call!(
        fn fetch(String, String, String, String, String, bool, Value);
        fn find_lcu_process(Value);
    );
}

fn main() {
    sciter::set_options(sciter::RuntimeOptions::DebugMode(false)).unwrap();
    let archived = include_bytes!("../target/assets.rc");
    sciter::set_options(sciter::RuntimeOptions::ScriptFeatures(
        sciter::SCRIPT_RUNTIME_FEATURES::ALLOW_SYSINFO as u8
            | sciter::SCRIPT_RUNTIME_FEATURES::ALLOW_FILE_IO as u8
            | sciter::SCRIPT_RUNTIME_FEATURES::ALLOW_EVAL as u8,
    ))
    .unwrap();
    let mut frame = sciter::Window::new();
    frame.event_handler(EventHandler {});
    frame.archive_handler(archived).unwrap();
    frame.load_file("this://app/html/main.html");
    frame.run_app();
}

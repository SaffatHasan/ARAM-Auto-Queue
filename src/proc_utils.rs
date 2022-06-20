use sysinfo::{ProcessExt, System, SystemExt};

pub struct LeagueProcess {
    pub cmd: Vec<String>,
}

pub fn find_lcu_process() -> Option<LeagueProcess> {
    let mut sys = System::new_all();

    sys.refresh_all();

    for (pid, process) in sys.processes() {
        let name = process.name();
        match name {
            "LeagueClientUx.exe" | "LeagueClientUx" => {
                // DOESN'T WORK!
                // let cmd = process.cmd().to_vec();
                // HAVE TO USE A WHOLE NEW CRATE JUST TO GET CMD!?
                use sysinfo::PidExt;
                let cmd = remoteprocess::Process::new(pid.as_u32())
                    .unwrap()
                    .cmdline()
                    .unwrap()[0]
                    .split("\" \"")
                    .map(|string| String::from(string))
                    .collect::<Vec<String>>();

                let league_process = LeagueProcess {
                    cmd,
                };
                return Some(league_process);
            }
            _ => continue,
        }
    }

    None
}

use std::collections::HashMap;

pub fn parse_cmdline_args(cmdline_args: Vec<String>) -> HashMap<String, String> {
    let mut cmdline_args_parsed = HashMap::new();
    for cmdline_arg in cmdline_args {
        if cmdline_arg.len() > 0 && cmdline_arg.contains("=") {
            let mut split = cmdline_arg[2..].split("=");
            let key = split.next().unwrap().to_owned();
            let value = split.next().unwrap().to_owned();
            cmdline_args_parsed.insert(key, value);
        }
    }
    cmdline_args_parsed
}

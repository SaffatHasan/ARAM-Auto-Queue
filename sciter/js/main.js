import { $, $$ } from '@sciter';
import { findLcuProcess } from './proc_utils.js';
import { LeagueAPI } from './lcu_api.js';
import { Config } from './config.js';
import { QUEUE_TYPE, ROLES, queueHasRoles } from './constants.js';
import { adjustWindow } from './adjust_window.js';

main();

async function launchGUI(leagueAPI) {
  adjustWindow();
  $('#about').on('click', () => Window.this.modal({ url: 'this://app/html/about.html' }));

  $('#status').textContent = 'Running';
  $('#status').style.color = 'green';

  $('#AUTO_LOBBY').state.checked = cfg.AUTO_LOBBY;

  $('#QUEUE_ID').value = String(cfg.QUEUE_ID);
  $('#QUEUE_ID').state.disabled = !cfg.AUTO_LOBBY;

  $('#PRIMARY_ROLE').value = cfg.PRIMARY_ROLE;
  $('#PRIMARY_ROLE').state.disabled = !queueHasRoles(cfg.QUEUE_ID);

  $('#SECONDARY_ROLE').value = cfg.SECONDARY_ROLE;
  $('#SECONDARY_ROLE').state.disabled = !queueHasRoles(cfg.QUEUE_ID);

  $('#AUTO_QUEUE').state.checked = cfg.AUTO_QUEUE;

  $('#AUTO_ACCEPT').state.checked = cfg.AUTO_ACCEPT;

  $('#AUTO_SKIP_POSTGAME').state.checked = cfg.AUTO_SKIP_POSTGAME;

  $('#toggle').textContent = 'Stop';

  await leagueAPI.init();
  let backgroundProc = await toggleProcess(null, leagueAPI);

  $('#toggle').on('click', async () => {
    $('#toggle').state.disabled = true;
    backgroundProc = await toggleProcess(backgroundProc, leagueAPI);
    $('#status').textContent = backgroundProc ? 'Running' : 'Not running';
    $('#status').style.color = backgroundProc ? 'green' : 'red';
    $('#toggle').textContent = backgroundProc ? 'Stop' : 'Start';
    $('#AUTO_LOBBY').state.disabled = Boolean(backgroundProc);
    $('#QUEUE_ID').state.disabled = !cfg.AUTO_LOBBY || Boolean(backgroundProc);
    $('#PRIMARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    $('#SECONDARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    $('#AUTO_QUEUE').state.disabled = Boolean(backgroundProc);
    $('#AUTO_ACCEPT').state.disabled = Boolean(backgroundProc);
    $('#AUTO_SKIP_POSTGAME').state.disabled = Boolean(backgroundProc);
    leagueAPI.updateConfig(cfg);
    $('#toggle').state.disabled = false;
  });

  $('#QUEUE_ID').on('change', (evt, el) => {
    cfg.QUEUE_ID = el.value;
    $('#PRIMARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    $('#SECONDARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    leagueAPI.updateConfig(cfg);
  });

  $('#AUTO_LOBBY').on('change', () => {
    cfg.AUTO_LOBBY = !cfg.AUTO_LOBBY;
    // Cannot select a queue ID if we are not creating a lobby anyways
    $('#QUEUE_ID').state.disabled = !cfg.AUTO_LOBBY || Boolean(backgroundProc);
    $('#PRIMARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    $('#SECONDARY_ROLE').state.disabled =
      !shouldDisplayRoleSelection(cfg) || Boolean(backgroundProc);
    leagueAPI.updateConfig(cfg);
  });

  $('#PRIMARY_ROLE').on('change', (evt, el) => {
    cfg.PRIMARY_ROLE = el.value;
    leagueAPI.updateConfig(cfg);
  });

  $('#SECONDARY_ROLE').on('change', (evt, el) => {
    cfg.SECONDARY_ROLE = el.value;
    leagueAPI.updateConfig(cfg);
  });

  document.on(
    'change',
    '#AUTO_QUEUE, #AUTO_ACCEPT, #AUTO_SKIP_POSTGAME, #AUTO_PLAY_AGAIN',
    (evt, el) => {
      cfg[el.id] = !cfg[el.id];
      leagueAPI.updateConfig(cfg);
    }
  );

  Window.this.on('close', () => {
    if (backgroundProc) {
      backgroundProc.terminate();
    }
  });
}

function shouldDisplayRoleSelection(config) {
  if (!config.AUTO_LOBBY) return false;
  if (!queueHasRoles(config.QUEUE_ID)) return false;
  return true;
}

async function toggleProcess(proc, leagueAPI) {
  if (proc !== null) {
    await leagueAPI.stopQueue();
    proc.terminate();
    return null;
  }

  proc = leagueAPI.loop();
  return proc;
}

async function main() {
  globalThis.cfg = Config.load();
  try {
    await launchGUI(new LeagueAPI(cfg));
  } catch (e) {
    Window.this.modal(
      <error caption="Failed to start">
        Have you logged into League of Legends?
      </error>
    );
    Window.this.close();
  }
}
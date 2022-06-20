import { Session } from './session.js';
import { lcuProcessArgs } from './proc_utils.js';
import { Config } from './config.js';
import { QUEUE_TYPE, ROLES, queueHasRoles } from './constants.js';

export class LeagueAPI {
  #session = null;

  constructor(config) {
    this.config = config;
  }

  async init() {
    const processArgs = await lcuProcessArgs();
    this.baseURL = `https://127.0.0.1:${processArgs['app-port']}`;
    this.#session = new Session();
    this.#session.auth = ['riot', processArgs['remoting-auth-token']];
    this.#session.verify = false;
    return this;
  }

  async loop() {
    let terminated = false;

    const proc = {
      terminate: () => (terminated = true),
    };

    const lambda = async () => {
      while (!terminated) {
        await this.run();
        await new Promise((resolve) => setTimeout(resolve, 1));
      }
    };

    lambda();
    return proc;
  }

  async run() {
    const phase = await this.sessionPhase();

    if (phase === null) {
      if (!this.config.AUTO_LOBBY) {
        return;
      }
      await this.createLobby(this.config.QUEUE_ID);
      if (!queueHasRoles(this.config.QUEUE_ID)) {
        return;
      }
      await this.selectPositionPreferences(
        this.config.PRIMARY_ROLE,
        this.config.SECONDARY_ROLE
      );
    } else if (phase === 'Lobby') {
      if (this.config.AUTO_QUEUE) {
        await this.queue();
      }
    } else if (phase === 'Matchmaking') {
      // pass
    } else if (phase === 'ReadyCheck') {
      if (this.config.AUTO_ACCEPT) {
        await this.accept();
      }
    } else if (['ChampSelect', 'InProgress'].includes(phase)) {
      // pass
    } else if (phase === 'PreEndOfGame') {
      if (this.config.AUTO_SKIP_POSTGAME) {
        await this.levelChangeAck();
        await this.rewardGrantedAck();
        await this.mutualHonorAck();
        await this.honorPlayer();
      }
    } else if (phase == 'EndOfGame') {
      if (this.config.AUTO_PLAY_AGAIN) {
        await this.playAgain();
      }
    }
  }

  updateConfig(config) {
    this.config = config;
    config.save();
  }

  async request(method, endpoint, data = {}) {
    return await this.#session.request(
      method,
      `${this.baseURL}${endpoint}`,
      data
    );
  }

  async sessionPhase() {
    const resp = await this.request('get', '/lol-gameflow/v1/session');
    return resp?.phase || null;
  }

  async createLobby(queueType) {
    await this.request('post', '/lol-lobby/v2/lobby', {
      queueId: queueType,
    });
  }

  async queue() {
    await this.request('post', '/lol-lobby/v2/lobby/matchmaking/search');
  }

  async stopQueue() {
    await this.request('delete', '/lol-lobby/v2/lobby/matchmaking/search');
  }

  async selectPositionPreferences(primary, secondary) {
    return await this.request(
      'put',
      '/lol-lobby/v2/lobby/members/localMember/position-preferences',
      {
        firstPreference: primary,
        secondPreference: secondary,
      }
    );
  }

  async accept() {
    await this.request('post', '/lol-matchmaking/v1/ready-check/accept');
  }

  async honorPlayer(playerID = 1) {
    await this.request('post', '/lol-honor-v2/v1/honor-player', {
      honorPlayerRequest: playerID,
    });
  }

  async levelChangeAck() {
    await this.request('post', '/lol-honor-v2/v1/level-change/ack');
  }

  async rewardGrantedAck() {
    await this.request('post', '/lol-honor-v2/v1/reward-granted/ack');
  }

  async mutualHonorAck() {
    await this.request('post', '/lol-honor-v2/v1/mutual-honor/ack');
  }

  async playAgain() {
    await this.request('post', '/lol-lobby/v2/play-again');
  }
}

import { QUEUE_TYPE, ROLES } from './constants.js';
import { fs } from '@sys';
import { decode } from '@sciter';

export class Config {
  constructor({
    AUTO_ACCEPT = true,
    AUTO_LOBBY = true,
    AUTO_PLAY_AGAIN = true,
    AUTO_SKIP_POSTGAME = true,
    AUTO_QUEUE = true,
    QUEUE_ID = QUEUE_TYPE.RANKED,
    PRIMARY_ROLE = ROLES.MID,
    SECONDARY_ROLE = ROLES.JG,
  }) {
    this.AUTO_ACCEPT = AUTO_ACCEPT;
    this.AUTO_LOBBY = AUTO_LOBBY;
    this.AUTO_PLAY_AGAIN = AUTO_PLAY_AGAIN;
    this.AUTO_SKIP_POSTGAME = AUTO_SKIP_POSTGAME;
    this.AUTO_QUEUE = AUTO_QUEUE;
    this.QUEUE_ID = QUEUE_ID;
    this.PRIMARY_ROLE = PRIMARY_ROLE;
    this.SECONDARY_ROLE = SECONDARY_ROLE;
  }

  static load() {
    try {
      const file = fs.$readfile('config.json');
      const json = decode(file, 'utf-8');
      const cfg = JSON.parse(json);
      return new Config(cfg);
    } catch (e) {
      return Config.default();
    }
  }

  static default() {
    return new Config({});
  }

  save() {
    const json = JSON.stringify(this, null, 2);
    const file = fs.$open('config.json', 'w', 0o666);
    file.write(json);
    file.close();
  }
}

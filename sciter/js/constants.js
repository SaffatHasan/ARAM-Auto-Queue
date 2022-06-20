export const QUEUE_TYPE = {
  ARAM: 450,
  ARURF: 900,
  DRAFT: 400,
  RANKED: 420,
  BLIND: 430,
  FLEX: 440,
};

export function queueHasRoles(queue) {
  return [QUEUE_TYPE.DRAFT, QUEUE_TYPE.FLEX, QUEUE_TYPE.RANKED].includes(
    Number(queue)
  );
}

export const ROLES = {
  TOP: 'TOP',
  JG: 'JUNGLE',
  MID: 'MIDDLE',
  BOT: 'BOTTOM',
  SUPP: 'SUPPORT',
  FILL: 'FILL',
};

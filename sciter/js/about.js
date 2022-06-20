import { $, $$ } from '@sciter';
import { launch } from '@env';

$('#sciter').on('click', () => {
  launch('https://sciter.com/?ref=qr');
});

$('#terra-informatica').on('click', () => {
  launch('https://terrainformatica.com/?ref=qr');
});

$('#girkov-arpa').on('click', () => {
  launch('https://girkovarpa.itch.io/?ref=qr');
});

$('#license').on('click', () => {
  launch('https://github.com/GirkovArpa/qr?ref=qr');
});

$('button').on('click', () => Window.this.close());

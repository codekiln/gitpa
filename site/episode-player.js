import { createSitePlayer } from './player.js';

export const manifest = {
  "id": "episode-player",
  "apiVersion": 1,
  "version": "1.0.0",
  "module": "episode-player.js",
  "styles": ["player.css"],
  "activation": "after-load",
  "pageProperties": []
};

/**
 * The persistent recording player. It is created on the first page adoption
 * (`createSitePlayer` already shows that page), moves its footer into a
 * persistent region, and shows each later page through the same player so
 * playback continues across navigation. Disposing the site pauses the recording
 * and puts it back in its page.
 */
export function episodePlayerPlugin(createPlayer) {
  return {
    ...manifest,
    setup(host) {
      const region = host.persistentRegion('recording');
      let player, disposed = false;
      const unsubscribe = host.onPageAdopted(() => {
        if (disposed) return;
        if (player) player.showPage();
        else player = createPlayer(host.document);
        if (player.footer && player.footer.parentElement !== region.element) region.element.append(player.footer);
      });
      return () => {
        if (disposed) return;
        disposed = true;
        unsubscribe();
        player?.audio?.pause();
        // The recording returns to its page, so a retried start can find it.
        player?.dispose({ restoreOriginal: true });
        player?.footer?.remove();
        player = undefined;
        host.document.body.classList.remove('has-episode-player');
        region.dispose();
      };
    },
  };
}

export default episodePlayerPlugin(createSitePlayer);

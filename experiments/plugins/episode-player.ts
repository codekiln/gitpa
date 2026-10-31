/** Unshipped consumer experiment for the proposed Gardener runtime contract. */
import type { Dispose, RuntimeHost, RuntimePlugin } from '../../contracts/gardener-plugin';

/** Structural port matching the existing site player's public manager. */
export interface EpisodePlayer {
  showPage(): void;
  readonly audio: HTMLAudioElement | null;
  readonly footer: HTMLElement | null;
  dispose(): void;
}

export function episodePlayerPlugin(createPlayer: (document: Document) => EpisodePlayer): RuntimePlugin {
  return {
    id: 'gitpa-episode-player',
    apiVersion: 1,
    setup(host: RuntimeHost): Dispose {
      const region = host.persistentRegion('recording');
      let player: EpisodePlayer | undefined;
      let disposed = false;
      // The existing factory already shows the initial page; do not adopt it twice.
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
        const audio = player?.audio;
        audio?.pause();
        player?.dispose();
        if (audio) {
          audio.removeAttribute('src');
          for (const source of audio.querySelectorAll('source')) source.remove();
          audio.load();
        }
        player?.footer?.remove();
        player = undefined;
        host.document.body.classList.remove('has-episode-player');
        region.dispose();
      };
    },
  };
}

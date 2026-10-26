import type { PublicationView, RuntimeHost, RuntimeManifest, RuntimePlugin } from './gardener-plugin';
import { episodePlayerPlugin } from '../experiments/plugins/episode-player';

declare const view: PublicationView;
declare const plugin: RuntimePlugin;
declare const host: RuntimeHost;
const id: string = plugin.id;
void id;
void episodePlayerPlugin;
// @ts-expect-error Plugins receive a read-only publication projection.
view.pages.push({ id: 'new', title: 'new', url: '/new/' });
// @ts-expect-error The projection exposes no raw graph/filesystem path.
view.sourceRoot;
// @ts-expect-error An unsupported API major cannot satisfy the proposed manifest.
const wrongVersion: RuntimeManifest = { id: 'test', apiVersion: 2, module: 'test.js', activation: 'after-load' };
void wrongVersion;
// @ts-expect-error Page adoption must complete before fragment focus, rather than await plugin work.
host.onPageAdopted(async () => {});

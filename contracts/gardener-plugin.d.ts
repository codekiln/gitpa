/** Proposed contract for Gardener195 / Gitpa93. No runtime currently exports this API. */
export type Dispose = () => void;
export type PageId = string;
export type BlockId = string;

export interface PublishedPage {
  readonly id: PageId;
  readonly title: string;
  /** Final same-site URL, supplied by the publisher rather than inferred from the title. */
  readonly url: string;
}

export interface PageAdoption {
  readonly page: PublishedPage;
  readonly main: HTMLElement;
  readonly revision: string;
  /** Published property values for this plugin. The plugin validates its payload. */
  readonly metadata: Readonly<Record<string, unknown>>;
  /** Aborted before this page is removed. Persistent player state belongs to the site. */
  readonly signal: AbortSignal;
}

export interface PersistentRegion {
  readonly element: HTMLElement;
  dispose(): void;
}

export interface RuntimeHost {
  readonly apiVersion: 1;
  readonly document: Document;
  readonly baseURL: string;
  /** Runs synchronously after core adoption and before fragment focus, including the current page. */
  onPageAdopted(listener: (page: PageAdoption) => undefined): Dispose;
  /** Local id is automatically scoped by the host to the active plugin. */
  persistentRegion(localId: string): PersistentRegion;
}

export interface RuntimePlugin {
  readonly id: string;
  readonly apiVersion: 1;
  /** Called once for this plugin in a document; the returned cleanup runs on site disposal. */
  setup(host: RuntimeHost): Dispose;
}

export interface RuntimeManifest {
  readonly id: string;
  readonly apiVersion: 1;
  readonly version: string;
  /** Asset paths relative to the manifest. */
  readonly module: string;
  readonly styles?: readonly string[];
  readonly activation: 'after-load' | 'on-demand';
  readonly pageProperties?: readonly string[];
}

/** Candidate build boundary: selected, redacted originals, never the raw source graph. */
export interface PublicBlock {
  readonly id: BlockId;
  readonly pageId: PageId;
  readonly text: string;
  readonly children: readonly BlockId[];
}

export interface PublicationView {
  readonly apiVersion: 1;
  readonly revision: string;
  readonly pages: readonly PublishedPage[];
  readonly blocks: readonly PublicBlock[];
}

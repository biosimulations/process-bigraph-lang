# Stage two plan: manifests per environment, and authoring in compose-api

Status: approved 2026-10-12. Follows the [registry and authoring design](registry-and-authoring.md) and the
[v2 implementation plan](plan.md); stage one (the read-only composite viewer in compose-api's web app) shipped in
compose-api 0.7.12 and 0.7.13.

## Context

Stage one shipped: compose-api 0.7.13 shows a submitted `.pbg` as `.pblang` text and a wiring graph. Every process
shows as "not in the registry" because the browser has no manifests. Stage two (authoring) needs manifests in two
places: the main-thread `Pblang` session (check, compile, graph) and the language-server worker (hover, completion,
diagnostics as you type).

Jim asked two things: where manifests are produced (from the registered entries or when environments are built), and
where the webapp gets them. Decided 2026-10-12:

- **A manifest is a fact about an environment, not about a package.** `describe` must import the classes inside the
  image that runs the document. The images differ: `registry_env` has process-bigraph 1.0.5 (via pbest), while the
  viva-pde-particle image has 1.8.x and its own core.
- **Producer: compose-api CI, inside each image.** A workflow runs a dependency-free describe script in every
  environment the deployment offers and opens a PR with `compose_api/registry/manifests/<env>.json`. Each manifest is
  reviewed like `catalog.yaml`, works without image owners' cooperation, and is strategy decision 5's phase B first
  output.
- **viva-pde-particle becomes a registry entry** in `manifest.yaml`, at level `tested`, with bundle `viva-pde-particle`.
  The evidence is its `compose-image.yml` job-contract and smoke tests. This closes the gap strategy.md records.
- **The webapp gets manifests from the API, same origin**: `GET /registry/environments` and
  `GET /registry/environments/{name}/manifest`, through the typed `useApi()` client. In dev they come from the
  production API through `NUXT_PUBLIC_API_BASE`, as today. They are not baked into the static build. Manifests ship
  in the API image with the other registry files, so a refreshed manifest goes live with the next compose-api release.

## Facts this rests on (from exploration)

- **Environments today:**
  - `registry_env`: a pbest-generated definition, identified by md5. Its image is `ghcr.io/biosimulations/registry_env:<hash>`. That org package exists but the cluster's pull falls back to a SLURM build.
  - Prebuilt images: `PREBUILT_SIMULATORS` in `kustomize/config/compose-api-rke/api.env`, today only `viva-pde-particle` pinned by digest. Its entrypoint is a bash script that sources `/app/docker/shell-hook.sh`.
- **Registry of record:** `compose_api/registry/manifest.yaml` plus the generated `catalog.yaml`. `RegistryEntry` has `module_roots`, `level` and `bundles`, but no ports. No HTTP route exposes any of it. The legacy `/core/processes|steps/list` (Postgres, string ports, no write path) stays untouched.
- **The run endpoint:** `POST /simulation/run?simulator=<name>` takes one `.pbg` file. `simulator` absent means `registry_env`.
- **PBL `describe`** (`process_bigraph_lang/v2/interfaces.py`):
  - It scans only a module's own members, not submodules.
  - It needs `bigraph_schema.parse` for defaults.
  - `_describe` in `__main__.py` always renders headers through the CLI binary.
  - None of that can run inside an arbitrary image.
- **PBL `Registry`** (`dsl/src/language/v2/headers.ts`) only appends: a second `addManifest` makes short names ambiguous.
- **PBL worker** (`dsl/src/language/main-browser.ts`) discards the services and registers no custom notifications.
  `WorkspaceRegistry` extends `Registry`, so filling `services.validation.HeaderRegistry` serves the checker, hover
  and completion at once.

## Part 1: process-bigraph-lang (one PR, then release 0.2.0)

1. **A standalone describe script.**
   - New file `process_bigraph_lang/v2/describe_env.py`, standard library only and runnable as a plain file: `python describe_env.py <module_root>... [--env-name N --image REF] > manifest.json`.
   - It walks submodules (`pkgutil.walk_packages`) and keeps Edge subclasses (MRO name check, as `_is_edge_class` does) defined under the given roots. Import errors per submodule are recorded, never fatal.
   - Output is the shared interface manifest (`pbg-interfaces/1`, see the registry design, section 1.7) plus `environment {name, image, python, process_bigraph, bigraph_schema, generated_by}` and `errors[]`.
   - Config defaults are taken only from dict specs with `_default`; types stay raw, and the TypeScript side parses them.
   - `describe_module` delegates its per-class work to the same functions, so there is one implementation. `describe` gains `--manifest-only`, which skips header rendering and needs no CLI.
   - Tests: the script's output on `tests/fixtures/test_registry` matches `describe_module`'s manifest for the same classes, run in a subprocess with `-I`.
2. **Replaceable registry.** In `Registry` (`headers.ts`):
   - `setManifests(manifests[])` clears and refills.
   - Declarations are keyed by address, so a duplicate replaces rather than appends.
   - A `schema_version` other than `pbg-interfaces/1` (or the earlier `pblang-manifest/0`) is rejected with a clear error.
   - `Pblang.setManifests` mirrors it in `dsl/src/api.ts`.
   - Tests go in `api.test.ts`.
3. **Worker channel.**
   - `main-browser.ts` keeps the services and handles the notification `pblang/setManifests` (`{ manifests: object[] }`): it calls `HeaderRegistry.setManifests`, then rebuilds every open document (`DocumentBuilder.update(allUris, [])`) so markers refresh.
   - The notification name is exported as a constant from `process-bigraph-lang`.
   - Tests: a unit test drives the handler through an in-memory connection, or the services directly if that is simpler.
4. **Docs.**
   - `docs/v2/registry-and-authoring.md`: a new section, "Manifests per environment", records today's decision and the compose-api flow. It notes that `/0` is what ships, with `/1` as the target, and replaces §4.4's stale "LSP shells out to Python" paragraph.
   - `docs/architecture.md`: the worker now has a channel.
   - `dsl/README.md`: the worker usage.
   - `CLAUDE.md`: the describe script.
5. **Iterate before releasing.** Use the local loop (npm link plus `nuxt dev` on port 4200 against the production API), then cut release 0.2.0 when compose-api's editor works locally. The release recipe is unchanged.

## Part 2: compose-api backend (PR A)

1. **A registry entry** for viva-pde-particle in `compose_api/registry/manifest.yaml`:
   - `module_roots: [viva_pde_particle]`, `level: tested`, `bundles: [viva-pde-particle]`.
   - Pinned to the commit behind the pinned digest: read the image's `org.opencontainers.image.revision` label or the `sha-<short>` tag.
   - The evidence names `compose-image.yml`.
   - Prebuilt submissions still skip `validate_submission`; that gap is unchanged here.
2. **Environments file** `compose_api/registry/environments.yaml`. It holds per environment:

   - `name`;
   - `kind: shared | prebuilt`;
   - how to enter it (`python` for registry_env; `bash -c 'source /app/docker/shell-hook.sh && python …'` for viva-pde-particle).

   Modules come from entries whose `bundles` include the environment's name. Images are not duplicated: registry_env's comes from the definition hash, and prebuilt ones come from the setting parsed out of `api.env`.

3. **Workflow** `.github/workflows/registry-manifests.yml`:
   - Triggers: `workflow_dispatch`, weekly, and on changes to the registry files, `simulator_registry.json` or `api.env`.
   - For each environment it pulls the image: registry_env from `ghcr.io/biosimulations/registry_env:<hash>` with `packages: read`, falling back to `docker build` of pbest's Docker definition; prebuilt ones by their pinned digest.
   - It runs `describe_env.py`, taken from the pinned PBL release's source, mounted read-only, with `--entrypoint`.
   - It writes `compose_api/registry/manifests/<env>.json` and opens a PR (`peter-evans/create-pull-request`) when anything changed.
   - The same logic is a script (`scripts/registry_manifests.py`), so it can be run locally with Docker.
4. **API** `compose_api/api/routers/registry.py`, prefix `/registry`, added to `APP_ROUTERS`, with Pydantic models:
   - `GET /registry/environments` returns, per environment: `[{name, kind, image, simulator (the run-endpoint value or null), components, entries: [{id, level}], generated_at, stale}]`. `stale` is true when the manifest's recorded image differs from the deployed pin.
   - `GET /registry/environments/{name}/manifest` returns the manifest JSON, with each component annotated with its entry id and level, and an ETag.
   - `make clients` regenerates the Python client and the webapp types.
5. **Tests** (`tests/registry/`):
   - Every manifest parses.
   - Every component's module lies under a root of an entry in that bundle.
   - The routes answer.
   - The stale flag works.
   - Local first manifests come from running the script once, through Docker on this Mac or by dispatching the workflow on the branch.
6. **Docs:**
   - `docs/strategy.md`: a decision 5 progress note.
   - `docs/webapp.md`: where manifests come from.
   - A new `docs/plan-authoring.md`: this plan's compose-api half, covering stage two of the editor.

## Part 3: compose-api webapp

**PR B, the viewer resolves processes** (quick win, small):

- A `useRegistry()` composable lists environments and fetches one manifest, cached per name.
- `CompositeViewer.vue` chooses the environment from the dataset's simulation: `simulator`, else `registry_env`. If the simulation summary lacks the simulator name, add it to the API model in PR A. It then calls `pblang.addManifest` before check and graph, so the findings and the graph's interface names resolve.

**PR C, the editor:**

- A page `/ui/composites/new`, plus "Edit a copy" from the viewer. It has an environment picker, from `/registry/environments`, which drives both the session and the worker.
- Monaco is editable, and the language worker runs as `new Worker(new URL('process-bigraph-lang/worker', import.meta.url), {type:'module'})`.
- A thin client in `viewers/composite/languageClient.ts`, over `vscode-jsonrpc/browser`:

  - sends `didOpen`/`didChange`;
  - maps `publishDiagnostics` to markers through the existing `toMarkers`;
  - registers Monaco hover and completion providers that forward to the server.

  `monaco-languageclient` stays out: it pulls in the `@codingame` stack and pins Monaco.

- Compile: `pblang.compile(text)`, with `CompileError.diagnostics` shown as markers. Then submit as `File([json], '<name>.pbg')` to `POST /simulation/run` with `simulator` set from the environment. The submit is shared with `simulations/new.vue` through a `useSubmitRun` composable, and success navigates to `/simulations/<id>`.
- Open sites and params: list `?` sites and params in a side form, then compile with them filled (`compile` already reports `G300` for unfilled ones). Keep this minimal in PR C and extend later.

## Order and releases

1. PBL PR (parts 1.1–1.4), CI green, merged on Jim's word. No release yet.
2. compose-api PR A: generate the first manifests, review their contents with Jim, merge on his word.
3. PR B and PR C, developed through the local loop against the production API. PR A's routes must be deployed for the production API to serve manifests; until then, point dev at `make run` locally.
4. Release PBL 0.2.0. compose-api bumps to `^0.2.0` and cuts its release (recipe as for 0.7.13), which deploys A, B and C together.

## Verification

- **PBL:**
  - `make check`, `make test`, `npm test` and `npx tsc --noEmit` all pass.
  - `describe_env.py` matches `describe_module` on the fixtures.
  - The worker test shows a diagnostic disappearing after `pblang/setManifests`.
- **compose-api:**
  - `make check`, `make test` and `make webapp-check` all pass.
  - The workflow, dispatched on the branch, produces `registry_env.json` and `viva-pde-particle.json`. The latter includes `FVReactionDiffusion` and matches PBL's fixture `viva_pde_particle.manifest.json` modulo version drift.
  - `curl /registry/environments` answers locally.
- **End to end:** headless Chrome through the scratchpad `pw/` scripts.
  - Simulation 4571's viewer shows no "not in the registry" findings, and its graph nodes carry interface names.
  - The editor shows hover over a process, completion of port names, and a marker that clears when fixed.
  - Compile and submit of a small composite to `registry_env` creates a simulation, which is then deleted or left as a test run per Jim's preference.

## Out of scope

- Server-side port checking at submission, and validation of prebuilt submissions.
- Manifests for catalog entries at level `listed`, which have no built environment.
- Later versions of the manifest (contracts, port semantics, adapters).
- The per-composite resolver (phase C).
- Retiring `/core/processes|steps/list`.

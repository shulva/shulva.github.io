# Shulva · 知识花园

Selective Obsidian publication for https://shulva.github.io/ . All notes default private. The private vault is never part of this checkout or CI.

The migration pins official Quartz **v4.5.2**, commit `4923affa7722dfc751f1074348e6dad214fe0c08`. Quartz v5.0.0 is a verified newer release; v4.5.2 is deliberately chosen for bundled plugins and a smaller acquisition scope. Preserve its MIT license when importing the official framework. Do not fabricate or substitute framework files if acquisition is blocked.

## Local update

Use Node 24, Python 3.12 and PyYAML 6.0.2. Dependencies are task-local (`npm ci --ignore-scripts --no-audit --no-fund`); no global installation is needed. The verified official framework and unchanged lockfile are now included in this checkout; UPSTREAM.json records provenance. Review migration evidence outside this checkout for acquisition receipts.

Only a top-level literal YAML boolean `publish: true` opts a note in. Quoted strings, missing/false/null values, `feed: show`, `published: true`, YAML yes/on, and the old public manifest never grant consent. The migration does not change any vault note. A user must review and opt notes in individually. Frontmatter must have unique scalar keys; YAML merges/tags and unsupported structures fail safely.

Run from this checkout, substituting your authorized read-only vault path:

```sh
python3 scripts/selective_export.py /absolute/path/to/vault --output "$PWD/content" --dry-run
python3 scripts/selective_export.py /absolute/path/to/vault --output "$PWD/content"
python3 scripts/check_stage.py content
# Optional: first-party synthetic feature demo, clearly labeled as non-user content
python3 scripts/add_demo.py content
python3 scripts/site-build.py
python3 scripts/check_resources.py public
python3 scripts/check_http_routes.py public
python3 scripts/serve_preview.py --bind 127.0.0.1 --port 8080 --directory public
```

Open http://127.0.0.1:8080/ . Ctrl-C stops the server. This custom Python handler maps extensionless Quartz paths to existing `.html` files, while unknown paths remain HTTP 404. Plain `python -m http.server` does not implement that mapping: direct `.html` URLs work, but the generated extensionless links can return HTTP 404. Do not use it as route acceptance evidence. Starting/replacing a server requires its own scoped sandbox approval when binding is denied; the previous server approval does not authorize a switch. `check_http_routes.py` exercises actual HTTP handler responses with in-memory sockets and no bind; it complements, and does not replace, a live-server/browser check. `site-build.py` deletes its old output before validating/building, so a failed build cannot leave a stale successful artifact. After an export failure, do not serve any previous generated directory: stop the server and delete/rebuild that generated directory before previewing. Export removes old managed staging at the start (except dry-run), so revocation and failures remove stale exported notes/assets. It refuses to delete unmanaged destinations. Dry-run writes nothing, reports only counts and hashes of approved content, and does not revoke old output; perform the real export/build for revocation.

Privacy boundary: only explicitly selected notes and their directly referenced local PNG attachments enter `content/`. No recursion through note links/embeds. Public links to private/missing/ambiguous notes fail with generic diagnostics. Note embeds require manual rewriting, even for selected notes. Selected Chinese/spaced paths are supported; private filenames/titles/aliases are never placed in diagnostics/manifests. Images receive content-hash filenames, generic alt text and stripped ancillary PNG metadata. Only PNG is currently supported; rewrite/convert other attachment formats after review. Raw HTML, reference-style Markdown links, link title syntax, traversal, dot/config paths and symlinks fail safely. Use simple inline Markdown links or wikilinks. Literal fenced/inline/indented code examples do not cause exports. Approved text and images must still be reviewed for content the author intentionally includes.

`content/publication.json` records counts and approved file hashes; no private inventory. CI validates this exact staging inventory and never reads a vault. Do not put test fixtures, runtime logs, vault configuration, `.obsidian` or bulk media in `content/`. Test fixture sources are generated outside the checkout; only sanitized selections reach real Quartz builds.

## Verification

Set a task-owned `TEST_SCRATCH` outside this public checkout:

```sh
mkdir -p /absolute/task/path/private-fixtures
TEST_SCRATCH=/absolute/task/path/private-fixtures python3 tests/test_selective_export.py
TEST_SCRATCH=/absolute/task/path/private-fixtures python3 tests/real_build_acceptance.py
```

The second command invokes real Quartz and scans both staging and every generated file (HTML, search/graph JSON, names and binary assets) for synthetic private canaries. It also checks local links/images/CSS resources. It fails if framework/dependencies are absent; it does not simulate a successful build. The actual vault remains unselected; an empty selection yields an app-owned blank Shulva CV at `/` and the existing Chinese Notes landing/help page at `/notes/`. Any authored public demonstration is explicitly labeled synthetic and does not represent user-selected notes.

CI builds/tests only the sanitized checkout. The validation workflow has no Pages actions, uploads, deployment job, remote writes or vault secrets. Branch-based deployment preparation is described below; commit/push remains gated on coordinator review. Do not run Quartz sync. Removing old notes from the current tree does **not** erase notes already present in earlier public Git history; this migration does not rewrite history.

## CV / NOTES

The exporter always generates the app-owned blank CV (`content/index.md`) and Notes landing (`content/notes/index.md`), with integrity hashes in the publication manifest. These pages do not count as selected user notes. `add_demo.py` updates only the Notes landing and synthetic demos; rerunning the export/demo/build sequence preserves the split. Shared top navigation appears on all generated pages; Notes, demos and lists retain Quartz tools. Edit the public `CV` template in `scripts/selective_export.py` to customize future exports.

Run `TEST_SCRATCH=/absolute/task/path/private-fixtures python3 tests/test_cv_notes.py` for the real build routing/navigation persistence regression. Preview startup is a separate approval step; the commands above are reference commands, not authorization to bind a socket.

A selected vault-root `index.md` conflicts with the app-owned Notes landing and fails closed with a generic route diagnostic. Rename that selected source before exporting; no user data can replace either landing.

## Branch-based production preparation

After a clean verified build, `python3 scripts/prepare_pages.py /absolute/new/outside-checkout/candidate` prepares a new sanitized source plus static-output tree for the existing `main` / root Pages source. It never stages, commits, pushes or changes Pages settings. The candidate contains `.nojekyll`; the root CV is `index.html` and exact `/notes/` has `notes/index.html` with the correct relative resource depth, so no `notes.html` alias or SPA catch-all is needed. Unknown routes must retain real HTTP 404 status.

The explicit source allowlist is in `scripts/prepare_pages.py`; generated `public/` files are copied to the candidate root. Dependencies, compiler caches, Python caches, all outside reports/fixtures and the Git directory are excluded. This preparation refuses any real selected user notes/assets. The approved synthetic demo remains labeled as synthetic. Never copy the whole checkout into a Pages artifact. With `.nojekyll`, allowlisted source is also publicly accessible alongside static output; no private source belongs there. Public history is unchanged.

Existing Pages source settings must be confirmed as branch `main`, folder `/` before a deployment is claimed. No authenticated REST access is assumed. After review, reconcile only the approved candidate manifest with the migration branch, verify the new commit descends from freshly fetched `origin/main`, then use a normal explicit refspec push. If the remote advances or settings differ, stop for a revised plan. Current preparation does not authorize that push.

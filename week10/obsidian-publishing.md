# Publishing Pipeline: Obsidian → Your Website

A guide to connecting an Obsidian vault to a static website via GitHub, so
that writing a note in Obsidian and pushing to GitHub publishes it to your
live site automatically.

This guide assumes you have:

- An Obsidian vault on your local machine
- A GitHub account
- A website (we'll use [Astro](https://astro.build/) as the example, but the
  pipeline is framework-agnostic)
- A web host you can SSH into (any VPS, e.g. DigitalOcean, Hetzner, Linode)

We'll use the following placeholders throughout. Replace them with your own
values:

| Placeholder            | Example                       |
|------------------------|-------------------------------|
| `<your-username>`      | your GitHub username or org   |
| `<your-vault-repo>`    | e.g. `obsidian-vault`         |
| `<your-site-repo>`     | e.g. `my-website`             |
| `<your-domain>.com`    | e.g. `example.com`            |

## High-level flow

```
+-------------------+     git push      +-------------------+
|  Obsidian vault   |  ───────────────► |  GitHub repo:     |
|  (local machine)  |                   |  vault repo       |
|                   |                   |  (branch: main)   |
+-------------------+                   +---------+---------+
                                                  │
                                  GitHub Action:  │  export-to-site.yml
                                  triggered when  │  (push to main, paths:
                                  posts change    │   posts/**)
                                                  ▼
                                        +---------+---------+
                                        | Static site repo  |
                                        | (e.g. Astro)      |
                                        | (branch: main)    |
                                        +---------+---------+
                                                  │
                                  GitHub Action:  │  deploy.yml
                                  triggered on    │  (push to main)
                                  any push        │
                                                  ▼
                                        +---------+---------+
                                        |  Your VPS         |
                                        |  /var/www/        |
                                        |  yoursite/        |
                                        |  served as        |
                                        |  https://         |
                                        |  yoursite.com     |
                                        +-------------------+
```

There are three locations and two GitHub Actions in the chain:

1. **Vault repo** — your Obsidian vault, pushed to GitHub.
2. **Site repo** — the source code of your website.
3. **Web host (VPS)** — the server that actually serves your site.

---

## The repos

### 1. Vault repo (Obsidian)

- **What it is:** your Obsidian vault, version-controlled in git.
- **Default branch:** `main`
- **Purpose:** authoring environment. You write and edit notes in Obsidian,
  then commit and push.

Suggested layout:

```
your-vault/
├── .github/workflows/
│   └── export-to-site.yml       ← Action that pushes posts to the site repo
├── .obsidian/                   ← Obsidian config (ignored by git)
├── Templates/
│   └── Post.md                  ← Template for a new post
├── posts/                       ← All posts intended for the site
│   ├── attachments/             ← Images, video, audio referenced from posts
│   ├── My-First-Post.md
│   └── ...
└── .gitignore                   ← At minimum: .obsidian/, .trash/, .DS_Store
```

Only files inside `posts/` (or whatever folder you choose) are exported. The
vault can contain other notes; they are ignored by the export pipeline.

A reasonable `.gitignore`:

```
.obsidian/
.trash/
.DS_Store
```

### 2. Site repo (static website)

- **What it is:** the source code of your website. The example uses Astro,
  but the same pattern works for Hugo, Eleventy, Jekyll, Next.js, etc.
- **Default branch:** `main`
- **Purpose:** receives exported posts from the vault and builds them into
  static HTML for deployment.

Relevant paths (Astro example):

```
your-site/
├── .github/workflows/
│   └── deploy.yml                       ← Build + rsync to the VPS
├── astro.config.mjs
├── package.json
├── src/
│   ├── content.config.ts                ← Collection schemas (zod)
│   ├── content/
│   │   └── posts/                       ← Posts land here from the vault
│   └── pages/
│       └── posts/
│           ├── [...id].astro            ← Renders individual posts
│           └── index.astro              ← Renders the post index
└── public/
    └── attachments/                     ← Images/video copied from the vault
```

### 3. Web host (VPS)

- **Document root:** `/var/www/<your-domain>/` (or wherever your web server
  is configured to serve from).
- **SSH access:** key-based, ideally on a non-default port for hygiene.
- **What gets deployed:** the contents of your build output directory
  (Astro: `dist/`), synced via `rsync --delete`.

Web server software (nginx, Caddy, Apache) is configured outside this
pipeline; it just needs to serve the document root.

---

## Stage 1: Writing a post in Obsidian

1. Open your vault in Obsidian.
2. Create a new note inside `posts/`. Use a template (or the
   [Templater](https://github.com/SilentVoid13/Templater) plugin) so each new
   post starts with consistent frontmatter:

   ```yaml
   ---
   title:
   description:
   tags: []
   draft: true
   date: 2026-04-30
   ---
   ```

3. Fill in the frontmatter and write the body in Markdown.

### Frontmatter rules

Whatever schema your site uses, your frontmatter must match it. The example
Astro site validates posts with [zod](https://zod.dev/) in
`src/content.config.ts`:

| Field         | Type         | Required | Notes                                                  |
|---------------|--------------|----------|--------------------------------------------------------|
| `title`       | string       | yes      | Build fails if missing.                                |
| `description` | string       | no       | Shown on indexes and as meta description.              |
| `date`        | date (ISO)   | no       | Coerced to a `Date`. Used for sorting.                 |
| `draft`       | boolean      | no       | If `true`, the post is **not** exported to the site.   |
| `tags`        | string[]     | no       | Useful for tag pages.                                  |

### Drafts

- `draft: true` → the export workflow skips the file. It stays in the vault
  but does not reach the site.
- `draft: false` (or omitted) → the post is exported and published.

To publish a draft, set `draft: false`, save, commit, and push.

### Attachments (images, video, audio)

- Drop attachments anywhere Obsidian saves them; by convention this guide
  uses `posts/attachments/`.
- Reference them with **either** Obsidian wiki-link syntax or standard
  Markdown:

  ```markdown
  ![[my-photo.jpg]]
  ![A caption](attachments/my-photo.jpg)
  ```

- During export, the path is rewritten so the deployed site loads the file
  from `/attachments/<filename>` (see Stage 2). You don't manage the
  rewrite manually.

---

## Stage 2: Vault → site repo (GitHub Action `export-to-site.yml`)

Place this file at `.github/workflows/export-to-site.yml` in your **vault**
repo.

### What it does

1. Runs whenever you push changes under `posts/` to `main`.
2. Checks out both the vault and the site repo.
3. Installs [`obsidian-export`](https://github.com/zoni/obsidian-export), a
   Rust CLI that converts Obsidian-flavoured Markdown (wiki-links, embeds)
   into standard Markdown.
4. Runs a small Node script to:
   - Filter out drafts.
   - Copy attachments into the site's `public/attachments/` folder.
   - Rewrite image/link paths in Markdown bodies to absolute
     `/attachments/<file>` URLs.
   - Write the cleaned Markdown into `src/content/posts/` in the site repo.
5. Commits and pushes the result to the site repo as a bot identity.

### The full workflow file

```yaml
name: Export vault → site
on:
  push:
    branches: [ main ]
    paths:
      - 'posts/**'
      - '.github/workflows/export-to-site.yml'
jobs:
  export:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout vault
        uses: actions/checkout@v4

      - name: Checkout site repo
        uses: actions/checkout@v4
        with:
          repository: <your-username>/<your-site-repo>
          token: ${{ secrets.SITE_REPO_PAT }}
          path: site

      - name: Install obsidian-export
        run: |
          set -eux
          curl --proto '=https' --tlsv1.2 -LsSf \
            https://github.com/zoni/obsidian-export/releases/download/v25.3.0/obsidian-export-installer.sh \
            | sh
          source $HOME/.cargo/env
          obsidian-export --version

      - name: Export from /posts
        run: |
          rm -rf export && mkdir -p export
          obsidian-export "$GITHUB_WORKSPACE" \
            --start-at "$GITHUB_WORKSPACE/posts" export

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install filter deps
        run: npm i gray-matter fast-glob fs-extra

      - name: Filter drafts, rewrite asset links, stage into site repo
        run: |
          node --input-type=module - <<'NODE'
          import fg from 'fast-glob';
          import fs from 'fs/promises';
          import fse from 'fs-extra';
          import matter from 'gray-matter';
          import path from 'path';

          const exportDir = 'export';
          const siteDir = 'site';
          const notesOut = path.join(siteDir, 'src/content/posts');
          const assetsOut = path.join(siteDir, 'public/attachments');

          await fse.remove(notesOut);
          await fse.remove(assetsOut);
          await fse.ensureDir(notesOut);
          await fse.ensureDir(assetsOut);

          // Copy non-Markdown files (attachments) and flatten 'attachments/' prefix.
          const nonMd = await fg(['**/*', '!**/*.md'], {
            cwd: exportDir, onlyFiles: true,
          });
          for (const p of nonMd) {
            let flatPath = p.startsWith('attachments/')
              ? p.replace(/^attachments\//, '')
              : p;
            const flatDir = path.dirname(flatPath);
            if (flatDir && flatDir !== '.') {
              await fse.ensureDir(path.join(assetsOut, flatDir));
            }
            await fse.copy(
              path.join(exportDir, p),
              path.join(assetsOut, flatPath),
            );
          }

          // Filter Markdown by draft status, rewrite relative asset paths.
          const mds = await fg(['**/*.md'], { cwd: exportDir, onlyFiles: true });
          for (const p of mds) {
            const full = path.join(exportDir, p);
            const raw = await fs.readFile(full, 'utf8');
            const fm = matter(raw);
            if (fm.data && fm.data.draft !== true) {
              let body = fm.content;
              body = body.replace(
                /(\]\(|!\[[^\)]*\]\()(?!(?:https?:|\/\/|#))([^)\s]+)\)/g,
                (m, open, rel) => {
                  let clean = rel.replace(/^\.\//, '').replace(/\.\.\//g, '');
                  clean = clean.replace(/^\/+/, '');
                  clean = clean.split(path.sep)
                    .filter(p => p && p !== '.' && p !== '..')
                    .join('/');
                  clean = clean.startsWith('attachments/')
                    ? clean.replace(/^attachments\//, '')
                    : clean;
                  return `${open}/attachments/${clean})`;
                },
              );
              const outPath = path.join(notesOut, p);
              await fse.ensureDir(path.dirname(outPath));
              const out = matter.stringify(body, fm.data);
              await fs.writeFile(outPath, out, 'utf8');
            }
          }
          NODE

      - name: Commit to site repo
        run: |
          cd site
          git config user.name "Vault Export Bot"
          git config user.email "bot@example.local"
          git pull --no-rebase
          git add -A
          git commit -m "Vault export from /posts: $GITHUB_SHA" || echo "No changes"
          git push
```

### Required secret

In your **vault** repo settings → *Secrets and variables* → *Actions*, add:

- `SITE_REPO_PAT` — a [personal access
  token](https://github.com/settings/tokens) with permission to push to your
  **site** repo.
  - Fine-grained token: `Contents: read and write` on `<your-site-repo>`.
  - Classic token: `repo` scope is sufficient.

Without this, the Action cannot check out or push to the site repo.

### Important quirks

- The site repo's `src/content/posts/` is **fully replaced** on every run.
  Do not edit post Markdown directly in the site repo — it will be
  overwritten on the next vault push. Edit in the vault.
- `public/attachments/` is also fully replaced. Put unrelated static assets
  somewhere else under `public/` (e.g. `public/img/`).
- Asset paths get flattened: a vault file at `posts/attachments/foo.jpg`
  becomes `public/attachments/foo.jpg` on the site, so reference it as
  `/attachments/foo.jpg`.

---

## Stage 3: Site build + VPS deploy (GitHub Action `deploy.yml`)

Place this file at `.github/workflows/deploy.yml` in your **site** repo.

### What it does

1. Runs on every push to `main`, including the bot commit from Stage 2.
2. Sets up Node and installs dependencies.
3. Builds the static site.
4. SSHes into your VPS and rsyncs the build output to the document root.

### The full workflow file

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Setup SSH
        env:
          DEPLOY_SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
          DEPLOY_PORT: ${{ secrets.DEPLOY_PORT || '22' }}
        run: |
          mkdir -p ~/.ssh
          echo "$DEPLOY_SSH_KEY" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -p $DEPLOY_PORT $DEPLOY_HOST >> ~/.ssh/known_hosts

      - name: Deploy to server
        env:
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          DEPLOY_PORT: ${{ secrets.DEPLOY_PORT || '22' }}
        run: |
          rsync -avz --delete \
            -e "ssh -i ~/.ssh/deploy_key -p $DEPLOY_PORT -o StrictHostKeyChecking=no" \
            dist/ $DEPLOY_USER@$DEPLOY_HOST:/var/www/<your-domain>/
```

Note: the build command (`npm run build`) and output folder (`dist/`) here
match Astro. For other generators, adjust:

| Tool      | Build command       | Output folder    |
|-----------|---------------------|------------------|
| Astro     | `npm run build`     | `dist/`          |
| Hugo      | `hugo`              | `public/`        |
| Eleventy  | `npx @11ty/eleventy`| `_site/`         |
| Jekyll    | `bundle exec jekyll build` | `_site/`  |
| Next.js (static) | `next build && next export` | `out/` |

### Required secrets

In your **site** repo settings → *Secrets and variables* → *Actions*:

| Secret             | Purpose                                              |
|--------------------|------------------------------------------------------|
| `DEPLOY_SSH_KEY`   | Private SSH key authorised on the VPS.               |
| `DEPLOY_HOST`      | VPS hostname or IP.                                  |
| `DEPLOY_USER`      | SSH user that owns the document root.                |
| `DEPLOY_PORT`      | SSH port. Optional; defaults to `22` in this example. |

#### Generating an SSH key for deployment

On your local machine (or any trusted environment), generate a dedicated
deploy key — do not reuse your personal SSH key:

```bash
ssh-keygen -t ed25519 -f deploy_key -C "github-actions-deploy" -N ""
```

This produces two files: `deploy_key` (private) and `deploy_key.pub`
(public).

1. Copy the **public** key to the VPS:
   ```bash
   ssh-copy-id -i deploy_key.pub -p <port> <user>@<host>
   ```
   Or manually append `deploy_key.pub` to `~/.ssh/authorized_keys` on the
   VPS for the deploy user.
2. Paste the **private** key (the entire file, including the
   `-----BEGIN ...-----` and `-----END ...-----` lines) into the
   `DEPLOY_SSH_KEY` GitHub secret.
3. Delete `deploy_key` from your local machine once it's saved as a secret.

---

## End-to-end: what you actually do to publish

1. In Obsidian:
   - Create or edit a note in `posts/`.
   - Fill in `title`, optional `description`, `tags`, `date`.
   - Set `draft: false` when ready to publish.
2. Commit and push from your vault repo:
   ```bash
   git add posts/
   git commit -m "Publish: <title>"
   git push
   ```
3. Wait for the two Actions to finish (typically 1–3 minutes total):
   - `Export vault → site` runs in your vault repo.
   - `Deploy to VPS` runs in your site repo.
4. Visit `https://<your-domain>.com/posts/` — the post should be live.

---

## Troubleshooting

### A post didn't appear on the site

In order, check:

1. Is `draft: true` still set in the post's frontmatter? The export filter
   skips drafts.
2. Did the vault push actually touch `posts/**`? The Action's path filter
   ignores changes to other folders.
3. Did `Export vault → site` succeed? Check the Actions tab on your **vault**
   repo. A failure here means the post never reached the site repo.
4. Did `Deploy to VPS` succeed? Check the Actions tab on your **site** repo.
   A common failure is the build step rejecting a post with malformed
   frontmatter (missing `title`, invalid `date`, etc.).

### An attachment is broken (404 on the site)

- Ensure the file is inside `posts/` (typically `posts/attachments/`) and
  has been committed.
- Asset paths are flattened — if you reference an image by hand, the URL on
  the site will be `/attachments/<filename>`, not
  `/attachments/some/nested/path/<filename>`.

### "Vault export bot" can't push

- Re-check the `SITE_REPO_PAT` secret in your **vault** repo's settings. The
  PAT must have write access to your site repo and must not be expired.

### SSH/rsync deploy fails

- Confirm `DEPLOY_SSH_KEY` contains the full private key, including
  `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE
  KEY-----` lines.
- Confirm the public counterpart is in the VPS user's
  `~/.ssh/authorized_keys`.
- Confirm the VPS is reachable on `DEPLOY_PORT` and that `DEPLOY_USER` has
  write permission on the document root.

### I edited a post directly in the site repo and it disappeared

Expected. Stage 2 wipes `src/content/posts/` on every run. Edit the post in
the vault instead.

---

## Modifying the pipeline

### Add a second content type

This pipeline only auto-exports `posts/`. To add another vault folder (say,
`essays/`):

1. In the vault, create the new folder and a template.
2. In the vault repo's `export-to-site.yml`:
   - Add the folder under `paths:` so the Action triggers on changes.
   - Add a second `obsidian-export ... --start-at .../essays` step.
   - Extend the Node filter to write into `site/src/content/essays/`.
3. In the site repo:
   - Add a collection schema for `essays`.
   - Add pages that render the new collection.

### Change the deploy target

Edit `deploy.yml` and update the `rsync` destination. If you change ports,
hosts, or users, update the matching secrets too.

### Test the export locally

You can run `obsidian-export` on your machine to dry-run the conversion:

```bash
cargo install obsidian-export
mkdir -p /tmp/export
obsidian-export ~/path/to/your-vault \
  --start-at ~/path/to/your-vault/posts \
  /tmp/export
```

Inspect `/tmp/export/` to see what the workflow would hand to the filter
script.

---

## Summary cheat sheet

| You want to...                  | Do this                                                                 |
|---------------------------------|-------------------------------------------------------------------------|
| Publish a new post              | Write in `posts/`, set `draft: false`, push to `main`.                  |
| Unpublish a post                | Set `draft: true` (or delete the file) in the vault, push.              |
| Edit site templates / styling   | Edit the site repo, push to `main`.                                     |
| Change the post schema          | Edit the site's content config, push to `main`.                         |
| Add a new attachment            | Drop it in `posts/attachments/`, reference it, push.                    |
| Roll back a bad deploy          | Revert the offending commit on the site repo's `main` and push.         |

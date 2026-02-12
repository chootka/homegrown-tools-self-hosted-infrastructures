# upcheck — Server Health Checker CLI

A Node.js command-line tool that checks whether your web services are up or down. Save endpoints and check them all with one command.

## Setup

```bash
# Install dependencies
npm install

# Make it available as a global command
npm link

# Now you can use it from anywhere
upcheck --help
```

## Usage

```bash
# Add endpoints to monitor
upcheck add https://example.com "My Site"
upcheck add https://wiki.example.com "Class Wiki"

# Check all saved endpoints
upcheck status

# Check a single URL (doesn't need to be saved)
upcheck status https://example.com

# See your saved endpoints
upcheck list

# Remove one
upcheck remove https://example.com
```

### Example output

```
  Checking 3 endpoint(s)...

  ✓  My Site              https://example.com                200  (120ms)
  ✓  Class Wiki           https://wiki.example.com           200  (340ms)
  ✗  Old Server           https://old.example.com            TIMEOUT

  Summary: 2/3 up
```

## Node.js Concepts Walkthrough

### 1. `package.json` and npm

Every Node.js project starts with `package.json`. It declares:
- **name/version** — identity of your project
- **bin** — makes your script available as a CLI command
- **dependencies** — packages your project needs (installed with `npm install`)
- **type: "module"** — enables modern `import/export` syntax

When you run `npm link`, npm creates a symlink so you can run `upcheck` from anywhere on your system.

### 2. The shebang line

```javascript
#!/usr/bin/env node
```

Just like `#!/bin/bash` for shell scripts, this tells the OS to run this file with Node.js. Without it, the system wouldn't know how to execute the file.

### 3. Commander.js (CLI framework)

```javascript
program
  .command("add <url>")
  .argument("[name]", "description")
  .action((url, name) => { ... });
```

Commander handles argument parsing, help text generation, and subcommand routing. `<url>` means required; `[name]` means optional. This saves us from manually parsing `process.argv`.

### 4. `fetch` and async/await

```javascript
async function checkUrl(url) {
  const response = await fetch(url);
  return { status: response.status };
}
```

`fetch` is built into Node.js 18+ (no extra packages needed). `async/await` lets us write asynchronous code that reads like synchronous code — no callbacks or `.then()` chains.

### 5. AbortController (timeouts)

```javascript
const controller = new AbortController();
const timer = setTimeout(() => controller.abort(), 5000);
await fetch(url, { signal: controller.signal });
```

We don't want to wait forever for a dead server. `AbortController` lets us cancel the request after a timeout. This is a standard web API that also works in Node.js.

### 6. JSON file persistence

```javascript
const data = JSON.parse(readFileSync(DATA_FILE, "utf-8"));
writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
```

We store endpoints in `~/.upcheck.json` — a simple JSON file in your home directory. This is a lightweight alternative to a database. Many CLI tools use this pattern for configuration and state.

### 7. Process exit codes

```javascript
process.exit(1);  // something went wrong
```

Just like in bash, exit code `0` means success and non-zero means failure. This matters when you chain commands or use them in scripts — the next command can check whether the previous one succeeded.

### 8. `Promise.all` (parallel requests)

```javascript
const results = await Promise.all(
  targets.map(async (ep) => {
    return await checkUrl(ep.url);
  })
);
```

Instead of checking URLs one by one, we fire all requests at the same time and wait for them all to finish. This is much faster when checking multiple endpoints.

## Try It

1. `npm install && npm link`
2. `upcheck add https://example.com "Example"`
3. `upcheck add https://httpstat.us/500 "Broken endpoint"`
4. `upcheck status`
5. `upcheck list`
6. Open `~/.upcheck.json` to see how the data is stored
7. Try modifying the script — add a `--timeout` flag, or save the last check time

## Connection to the Course

In weeks 3–4, we'll set up our own web servers. This tool gives you a way to monitor them. Imagine running `upcheck status` every morning to confirm your self-hosted services are online — or setting up a cron job to do it automatically and alert you when something goes down.

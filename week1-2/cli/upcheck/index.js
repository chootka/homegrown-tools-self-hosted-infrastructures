#!/usr/bin/env node
// =============================================================
// upcheck — Server Health Checker CLI
//
// A simple tool that checks whether web services are up or down.
// Saves endpoints to a local JSON file so you can re-check them.
//
// Usage:
//   upcheck add <url> [name]   — save a URL to monitor
//   upcheck remove <url>       — remove a saved URL
//   upcheck list               — show all saved endpoints
//   upcheck status [url]       — check if endpoints are up/down
//
// Concepts: commander.js, fetch, async/await, JSON file I/O,
//           process exit codes, colored terminal output
// =============================================================

import { program } from "commander";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { homedir } from "node:os";

// ----- Configuration ----------------------------------------
const DATA_FILE = resolve(homedir(), ".upcheck.json");
const TIMEOUT_MS = 5000;

// ----- Color helpers (ANSI escape codes) --------------------
// These work the same way as in our bash script — we wrap text
// in special character sequences that terminals interpret as colors.
const color = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`,
  dim: (text) => `\x1b[2m${text}\x1b[0m`,
};

// ----- Data persistence -------------------------------------
// We store endpoints in a simple JSON file in the home directory.
// This is a lightweight alternative to a database — perfect for
// small CLI tools. You'll see this pattern again when we work
// with configuration files on self-hosted servers.

function loadEndpoints() {
  if (!existsSync(DATA_FILE)) return [];
  try {
    return JSON.parse(readFileSync(DATA_FILE, "utf-8"));
  } catch {
    return [];
  }
}

function saveEndpoints(endpoints) {
  writeFileSync(DATA_FILE, JSON.stringify(endpoints, null, 2) + "\n");
}

// ----- Health check logic -----------------------------------
// We use the built-in fetch API (available in Node 18+).
// AbortController lets us set a timeout so we don't wait forever.

async function checkUrl(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  const start = Date.now();
  try {
    const response = await fetch(url, { signal: controller.signal });
    const ms = Date.now() - start;
    return { up: true, status: response.status, ms };
  } catch {
    return { up: false, status: "TIMEOUT", ms: Date.now() - start };
  } finally {
    clearTimeout(timer);
  }
}

// ----- CLI commands -----------------------------------------
// commander.js is a popular library for building CLIs.
// Each .command() defines a subcommand with its own arguments
// and action handler.

program
  .name("upcheck")
  .description("Check whether your web services are up or down")
  .version("1.0.0");

// --- add ---
program
  .command("add <url>")
  .argument("[name]", "a friendly name for this endpoint")
  .description("Add a URL to monitor")
  .action((url, name) => {
    const endpoints = loadEndpoints();

    // Check for duplicates
    if (endpoints.some((e) => e.url === url)) {
      console.log(color.yellow(`  !  ${url} is already in your list.`));
      process.exit(1);
    }

    endpoints.push({ url, name: name || url });
    saveEndpoints(endpoints);
    console.log(color.green(`  ✓  Added ${name || url} (${url})`));
  });

// --- remove ---
program
  .command("remove <url>")
  .description("Remove a URL from monitoring")
  .action((url) => {
    let endpoints = loadEndpoints();
    const before = endpoints.length;
    endpoints = endpoints.filter((e) => e.url !== url);

    if (endpoints.length === before) {
      console.log(color.yellow(`  !  ${url} was not in your list.`));
      process.exit(1);
    }

    saveEndpoints(endpoints);
    console.log(color.green(`  ✓  Removed ${url}`));
  });

// --- list ---
program
  .command("list")
  .description("Show all saved endpoints")
  .action(() => {
    const endpoints = loadEndpoints();
    if (endpoints.length === 0) {
      console.log(color.dim("  No endpoints saved. Use 'upcheck add <url>' to add one."));
      return;
    }
    console.log(color.bold(`\n  ${endpoints.length} saved endpoint(s):\n`));
    for (const ep of endpoints) {
      console.log(`  •  ${ep.name.padEnd(20)} ${color.dim(ep.url)}`);
    }
    console.log();
  });

// --- status ---
program
  .command("status [url]")
  .description("Check if endpoints are up or down")
  .action(async (url) => {
    let targets;

    if (url) {
      // Check a single URL (doesn't need to be saved)
      const endpoints = loadEndpoints();
      const saved = endpoints.find((e) => e.url === url);
      targets = [{ url, name: saved ? saved.name : url }];
    } else {
      // Check all saved endpoints
      targets = loadEndpoints();
    }

    if (targets.length === 0) {
      console.log(color.dim("  No endpoints to check. Use 'upcheck add <url>' first."));
      return;
    }

    console.log(color.bold(`\n  Checking ${targets.length} endpoint(s)...\n`));

    // Run all checks in parallel with Promise.all
    const results = await Promise.all(
      targets.map(async (ep) => {
        const result = await checkUrl(ep.url);
        return { ...ep, ...result };
      })
    );

    // Print results
    let upCount = 0;
    for (const r of results) {
      if (r.up) {
        upCount++;
        const badge = color.green("✓");
        const time = color.dim(`(${r.ms}ms)`);
        console.log(`  ${badge}  ${r.name.padEnd(20)} ${r.url.padEnd(35)} ${r.status}  ${time}`);
      } else {
        const badge = color.red("✗");
        console.log(`  ${badge}  ${r.name.padEnd(20)} ${r.url.padEnd(35)} ${color.red(r.status)}`);
      }
    }

    // Summary
    console.log(color.bold(`\n  Summary: ${upCount}/${results.length} up\n`));

    // Exit with an error code if anything is down — useful for
    // scripting and automation (e.g. cron jobs, CI pipelines).
    if (upCount < results.length) {
      process.exit(1);
    }
  });

// Parse the command-line arguments and run the matched command.
program.parse();

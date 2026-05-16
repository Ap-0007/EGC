#!/usr/bin/env node
'use strict';

const { createStateStore } = require('./lib/state-store');

async function bootstrap(options = {}) {
  const store = await createStateStore(options);
  const dbPath = store.dbPath;
  try {
    return {
      ok: true,
      dbPath,
      migrations: store.getAppliedMigrations(),
    };
  } finally {
    store.close();
  }
}

if (require.main === module) {
  bootstrap()
    .then(result => {
      console.error(`[bootstrap-state-db] OK ${result.dbPath} (${result.migrations.length} migrations)`);
      process.exit(0);
    })
    .catch(err => {
      console.error(`[bootstrap-state-db] FAILED: ${err.message}`);
      process.exit(1);
    });
}

module.exports = { bootstrap };

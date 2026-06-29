fs.writeFileSync(stateFilePath, JSON.stringify(state));
fs.chmodSync(stateFilePath, 0o600);
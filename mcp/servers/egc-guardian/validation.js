const fs = require('fs');
const auditLogPath = '~/.egc/audit.log';
function validateCall(call) {
  if (!call.allowed) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      toolName: call.toolName,
      payload: call.payload,
      reason: 'Blocked by validation'
    };
    fs.appendFileSync(auditLogPath, JSON.stringify(logEntry) + '\n');
    return false;
  }
  // ...
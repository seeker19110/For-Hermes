function loadFeishuClient() {
  // Preferred dependency after decoupling.
  try {
    return require("../../feishu-common/index.js");
  } catch (primaryErr) {
    // Backward compatibility for older monorepo layouts.
    try {
      return require("../../common/feishu-client.js");
    } catch (legacyErr) {
      const err = new Error(
        "Missing dependency: feishu-common. Install feishu-common skill first, then retry.",
      );
      err.cause = { primaryErr, legacyErr };
      throw err;
    }
  }
}

module.exports = loadFeishuClient();

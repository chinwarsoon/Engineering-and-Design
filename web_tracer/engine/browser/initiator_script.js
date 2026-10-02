/*
 * engine/browser/initiator_script.js — injected via Playwright add_init_script (T24, §8.4).
 *
 * Wraps window.fetch and XMLHttpRequest so every network request records the *initiating*
 * JavaScript function and line via `new Error().stack`. Playwright's extraHTTPHeaders is
 * page-level only and cannot name the initiating function — this patch is what gives the
 * project its key advantage (workplan §8.3.1 / §8.4). Results are stored in
 * window.__wt_initiators keyed by `url|epoch` and read back from Python via URL + time.
 */
(function () {
  if (window.__wt_patched) return;
  window.__wt_patched = true;
  window.__wt_initiators = {};

  function parseStack(stack) {
    if (!stack) return null;
    var lines = String(stack).split("\n").slice(1);
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var m =
        line.match(/at\s+(.+?)\s+\((.+?):(\d+):(\d+)\)/) ||
        line.match(/(.+?):(\d+):(\d+)/);
      if (m) {
        if (m[2] !== undefined) {
          return { file: m[2], line: parseInt(m[3], 10), column: parseInt(m[4], 10), function: m[1] };
        }
        return { file: m[1], line: parseInt(m[2], 10), column: parseInt(m[3], 10) };
      }
    }
    return null;
  }

  function record(url) {
    try {
      var info = parseStack(new Error().stack);
      window.__wt_initiators[String(url) + "|" + Date.now()] = info;
    } catch (e) {
      /* never break the page */
    }
  }

  var realFetch = window.fetch ? window.fetch.bind(window) : null;
  if (realFetch) {
    window.fetch = function (input, init) {
      var url = typeof input === "string" ? input : input && input.url;
      record(url);
      return realFetch(input, init);
    };
  }

  var RealXHR = window.XMLHttpRequest;
  if (RealXHR) {
    var proto = RealXHR.prototype;
    var realOpen = proto.open;
    proto.open = function (method, url) {
      this.__wt_url = url;
      record(url);
      return realOpen.apply(this, arguments);
    };
  }
})();

/**
 * mdBook: chapter narration strip + optional auto-advance to next SUMMARY page.
 * Expects MP3 at {site root}/audio/chapters/{page-stem}.mp3 (see build_public_mdbook.py).
 */
(function () {
  "use strict";

  function pageStem() {
    var seg = location.pathname.split("/").pop() || "";
    return seg.replace(/\.html?$/i, "");
  }

  /** mdBook lives under site-url; strip trailing .html path segment except filename */
  function siteRootPathname() {
    var path = location.pathname;
    var noFile = path.replace(/\/[^/]+\.html?$/i, "");
    if (noFile.endsWith("/chapters")) {
      var root = noFile.slice(0, -"/chapters".length);
      return root || "/";
    }
    return noFile || "/";
  }

  function chapterMp3Url() {
    var stem = pageStem();
    var root = siteRootPathname();
    return location.origin + root + "/audio/chapters/" + encodeURIComponent(stem) + ".mp3";
  }

  /** Sidebar chapter links in DOM order (deduped by pathname). */
  function orderedChapterUrls() {
    var seen = {};
    var out = [];
    var sel = "#sidebar a[href$='.html'], aside.sidebar a[href$='.html']";
    document.querySelectorAll(sel).forEach(function (a) {
      try {
        var u = new URL(a.href);
        var key = u.pathname;
        if (!seen[key]) {
          seen[key] = true;
          out.push(u.href);
        }
      } catch (_) {}
    });
    return out;
  }

  function currentChapterIndex(urls) {
    var here = new URL(location.href).pathname;
    return urls.findIndex(function (h) {
      try {
        return new URL(h).pathname === here;
      } catch (_) {
        return false;
      }
    });
  }

  function mp3Exists(url, cb) {
    fetch(url, { method: "HEAD", cache: "force-cache" })
      .then(function (r) {
        cb(r.ok);
      })
      .catch(function () {
        cb(false);
      });
  }

  function loadAutonextPref() {
    try {
      return localStorage.getItem("hw-os-autonext") !== "0";
    } catch (_) {
      return true;
    }
  }

  function saveAutonextPref(on) {
    try {
      localStorage.setItem("hw-os-autonext", on ? "1" : "0");
    } catch (_) {}
  }

  /** Same-tab chapter advance: next page should start narration if autoplay is on. */
  var CHAIN_PLAY_KEY = "hw-os-narration-chain";

  function markNarrationChainHandoff() {
    try {
      sessionStorage.setItem(CHAIN_PLAY_KEY, "1");
    } catch (_) {}
  }

  function consumeNarrationChainHandoff() {
    try {
      if (sessionStorage.getItem(CHAIN_PLAY_KEY) !== "1") return false;
      sessionStorage.removeItem(CHAIN_PLAY_KEY);
      return true;
    } catch (_) {
      return false;
    }
  }

  function tryPlayAfterLoad(audio, shouldChain) {
    if (!shouldChain || !loadAutonextPref()) return;

    function attempt() {
      var p = audio.play();
      if (p && typeof p.then === "function") {
        p.catch(function () {
          /* Browser autoplay policy — controls remain for manual play. */
        });
      }
    }

    if (audio.readyState >= 3) {
      attempt();
      return;
    }
    audio.addEventListener(
      "canplay",
      function onReady() {
        audio.removeEventListener("canplay", onReady);
        attempt();
      },
      false
    );
  }

  function mount() {
    var url = chapterMp3Url();
    var stem = pageStem();
    if (!stem) return;

    mp3Exists(url, function (ok) {
      if (!ok) return;

      var wrap = document.createElement("div");
      wrap.id = "hw-os-listen";
      wrap.innerHTML =
        '<span class="hw-os-listen-label" title="Narration for this page">' +
        '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
        '<path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>' +
        "</svg> Listen</span>" +
        "<audio preload=\"metadata\" controls playsinline></audio>" +
        '<label class="hw-os-autonext">' +
        '<input type="checkbox" id="hw-os-autonext-cb" /> Autoplay' +
        "</label>";

      document.body.appendChild(wrap);
      document.body.classList.add("hw-os-listen-active");

      var audio = wrap.querySelector("audio");
      audio.src = url;
      audio.preload = "auto";
      var cb = wrap.querySelector("#hw-os-autonext-cb");
      cb.checked = loadAutonextPref();
      cb.addEventListener("change", function () {
        saveAutonextPref(cb.checked);
      });

      tryPlayAfterLoad(audio, consumeNarrationChainHandoff());

      audio.addEventListener("ended", function () {
        if (!cb.checked) return;
        var urls = orderedChapterUrls();
        var i = currentChapterIndex(urls);
        if (i < 0 || i >= urls.length - 1) return;
        markNarrationChainHandoff();
        window.location.href = urls[i + 1];
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();

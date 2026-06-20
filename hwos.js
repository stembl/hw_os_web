// The Hardware OS — mdBook customizations
// Source of truth: web/mdbook-assets/hwos.js in stembl/hw_os
// Injected via additional-js by mdBook build.

(function hwosFavicon() {
  // Override mdBook's default favicon with the D4+ mark.
  // Done via JS because head.hbs injects before mdBook's own <link> tags.
  var links = document.querySelectorAll('link[rel*="icon"]');
  var icon = 'media/logo-d4plus-icon-web.png';
  for (var i = 0; i < links.length; i++) { links[i].href = icon; }
  if (!links.length) {
    var link = document.createElement('link');
    link.rel = 'icon';
    link.type = 'image/png';
    link.href = icon;
    document.head.appendChild(link);
  }
})();

(function hwosNav() {
  // Brand link below menu title in sidebar
  var menuTitle = document.querySelector('.menu-title');
  if (menuTitle) {
    var brandEl = document.createElement('div');
    brandEl.className = 'hwos-sidebar-brand';
    brandEl.innerHTML =
      '<a href="https://thehardwareos.com" rel="noopener" class="hwos-brand-link">'
      + '<img src="media/logo-d4plus-icon-web.png" class="hwos-brand-icon" alt="" aria-hidden="true" />'
      + 'thehardwareos.com'
      + '</a>';
    menuTitle.parentNode.insertBefore(brandEl, menuTitle.nextSibling);
  }

  // Page footer — appended to .page-wrapper, outside .content prose column
  var pageWrapper = document.querySelector('.page-wrapper');
  if (pageWrapper) {
    var footer = document.createElement('footer');
    footer.className = 'hwos-page-footer';
    footer.innerHTML =
      'Read online free \u2014 print, ebook, and audio in preparation. '
      + '<a href="https://thehardwareos.com" rel="noopener">thehardwareos.com</a>'
      + ' \u00a0\u00b7\u00a0 \u00a9 2026 Steve Embleton \u2014 All Rights Reserved';
    pageWrapper.appendChild(footer);
  }
})();

(function hwosParts() {
  // Inject part-title labels into the sidebar TOC.
  // The compiled toc.html is a flat list — part headings from SUMMARY.md
  // are not in the built HTML, so we add them via MutationObserver.
  var PARTS = [
    { before: '01-the-missing-manual.html',
      label:  'Part I \u2014 Why Hardware Programs Break' },
    { before: '04-dri-ownership-and-decision-authority.html',
      label:  'Part II \u2014 The Hardware OS Core' },
    { before: '09-requirements-lifecycle.html',
      label:  'Part III \u2014 Technical Evidence' },
    { before: '15-what-every-tier-wants.html',
      label:  'Part IV \u2014 Running the Organization' },
    { before: '18-rollout-sequence-triage-then-system.html',
      label:  'Part V \u2014 Adoption and Scale' }
  ];

  function injectParts() {
    var ol = document.querySelector('.sidebar-scrollbox ol.chapter');
    if (!ol) return false;
    if (ol.querySelector('.part-title')) return true;
    PARTS.forEach(function(part) {
      var link = ol.querySelector('a[href$="' + part.before + '"]');
      if (!link) return;
      var li = document.createElement('li');
      li.className = 'part-title';
      li.textContent = part.label;
      link.closest('li').insertAdjacentElement('beforebegin', li);
    });
    return true;
  }

  if (!injectParts()) {
    var target = document.querySelector('.sidebar-scrollbox') || document.getElementById('sidebar');
    if (target) {
      var obs = new MutationObserver(function() {
        if (injectParts()) obs.disconnect();
      });
      obs.observe(target, { childList: true, subtree: true });
    }
  }
})();

(function hwosDiagrams() {
  // Swap diagram SVGs between light and dark variants when the mdBook theme changes.
  // mdBook sets multiple classes on <html>: "js sidebar-visible navy" etc.
  // Dark themes: coal, navy, ayu, rust.

  function isDark() {
    var cl = document.documentElement.classList;
    return cl.contains('coal') || cl.contains('navy') || cl.contains('ayu') || cl.contains('rust');
  }

  function swapDiagrams() {
    var dark = isDark();
    var imgs = document.querySelectorAll('img[src*="diagram-"]');
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      var src = img.getAttribute('src');
      if (dark && src.indexOf('-dark.svg') === -1) {
        img.setAttribute('src', src.replace('.svg', '-dark.svg'));
      } else if (!dark && src.indexOf('-dark.svg') !== -1) {
        img.setAttribute('src', src.replace('-dark.svg', '.svg'));
      }
    }
  }

  swapDiagrams();

  // Watch for theme class changes on <html> (user switches theme via mdBook menu).
  var obs = new MutationObserver(function(mutations) {
    for (var i = 0; i < mutations.length; i++) {
      if (mutations[i].attributeName === 'class') { swapDiagrams(); break; }
    }
  });
  obs.observe(document.documentElement, { attributes: true });
})();

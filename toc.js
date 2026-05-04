// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item expanded "><a href="index.html"><strong aria-hidden="true">1.</strong> The Hardware OS</a></li><li class="chapter-item expanded "><a href="chapters/01-the-missing-manual.html"><strong aria-hidden="true">2.</strong> 1. The Missing Manual</a></li><li class="chapter-item expanded "><a href="chapters/02-process-is-the-product.html"><strong aria-hidden="true">3.</strong> 2. Process Is the Product</a></li><li class="chapter-item expanded "><a href="chapters/03-failure-patterns-chaos-drift-unowned-decisions.html"><strong aria-hidden="true">4.</strong> 3. Failure Patterns: Chaos, Drift, and Unowned Decisions</a></li><li class="chapter-item expanded "><a href="chapters/04-dri-ownership-and-decision-authority.html"><strong aria-hidden="true">5.</strong> 4. DRI Ownership and Decision Authority</a></li><li class="chapter-item expanded "><a href="chapters/05-spec-integrity-and-requirement-hygiene.html"><strong aria-hidden="true">6.</strong> 5. Spec Integrity and Requirement Hygiene</a></li><li class="chapter-item expanded "><a href="chapters/06-gates-risk-registers-one-page-truth.html"><strong aria-hidden="true">7.</strong> 6. Gates, Risk Registers, and One-Page Truth</a></li><li class="chapter-item expanded "><a href="chapters/08-automation-decisions-at-concept-stage.html"><strong aria-hidden="true">8.</strong> 8. Automation Decisions at Concept Stage</a></li><li class="chapter-item expanded "><a href="chapters/15-schedule-from-real-dependencies.html"><strong aria-hidden="true">9.</strong> 15. Schedule from Real Dependencies and Honest Critical Path</a></li><li class="chapter-item expanded "><a href="chapters/09-requirements-lifecycle.html"><strong aria-hidden="true">10.</strong> 9. Requirements Lifecycle (Hypothesis -&gt; Bless -&gt; Evidence -&gt; Revise)</a></li><li class="chapter-item expanded "><a href="chapters/10-requirements-from-physics.html"><strong aria-hidden="true">11.</strong> 10. Requirements from Physics (Not Stacked Buffers)</a></li><li class="chapter-item expanded "><a href="chapters/11-many-factors-one-honest-limit.html"><strong aria-hidden="true">12.</strong> 11. Many Factors, One Honest Limit</a></li><li class="chapter-item expanded "><a href="chapters/12-models-and-tests-that-change-decisions.html"><strong aria-hidden="true">13.</strong> 12. Models and Tests That Change Decisions</a></li><li class="chapter-item expanded "><a href="chapters/07-fleet-as-instrumented-experiment.html"><strong aria-hidden="true">14.</strong> 7. Fleet as Instrumented Experiment</a></li><li class="chapter-item expanded "><a href="chapters/13-risk-and-how-we-define-done-on-paper.html"><strong aria-hidden="true">15.</strong> 13. Risk and How We Define Done on Paper</a></li><li class="chapter-item expanded "><a href="chapters/14-what-every-tier-wants.html"><strong aria-hidden="true">16.</strong> 14. What Every Tier Wants (Exec to Supplier)</a></li><li class="chapter-item expanded "><a href="chapters/16-first-article-fast-disciplined-iteration.html"><strong aria-hidden="true">17.</strong> 16. First Article: Fast, Disciplined Iteration</a></li><li class="chapter-item expanded "><a href="chapters/17-supplier-data-critical-characteristics-producibility.html"><strong aria-hidden="true">18.</strong> 17. Supplier Data, Critical Characteristics, and Producibility</a></li><li class="chapter-item expanded "><a href="chapters/18-rollout-sequence-triage-then-system.html"><strong aria-hidden="true">19.</strong> 18. Rollout Sequence: Triage Then System</a></li><li class="chapter-item expanded "><a href="chapters/19-training-cadence-failure-recovery.html"><strong aria-hidden="true">20.</strong> 19. Training, Cadence, and Failure Recovery</a></li><li class="chapter-item expanded "><a href="chapters/20-what-this-os-does-not-cover.html"><strong aria-hidden="true">21.</strong> 20. What This OS Does Not Cover</a></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString().split("#")[0];
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);

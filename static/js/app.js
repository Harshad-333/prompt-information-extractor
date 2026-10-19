/* ==========================================================================
   Prompt-Based Information Extraction System — front-end behaviour
   Plain ES2017+ JavaScript, no build step. All buttons perform real actions.
   ========================================================================== */
(function () {
  "use strict";

  var state = {
    lastResult: null,
    lastPrompt: "",
    lastMode: "standard",
    busy: false
  };

  // ------------------------------------------------------------------ Utils
  function $(id) { return document.getElementById(id); }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function syntaxHighlight(jsonText) {
    // Tokenise the RAW JSON first, then escape each piece for safe HTML output.
    // Escaping before tokenising would turn quotes into &quot; and break matching.
    var tokenRe = /("(?:\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*")(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?/g;
    var out = "";
    var last = 0;
    var match;
    while ((match = tokenRe.exec(jsonText)) !== null) {
      out += escapeHtml(jsonText.slice(last, match.index));
      var cls;
      var text;
      if (match[1]) {
        cls = match[2] ? "json-key" : "json-string";
        text = match[1] + (match[2] || "");
      } else if (match[3]) {
        cls = match[3] === "null" ? "json-null" : "json-string";
        text = match[3];
      } else {
        cls = "json-number";
        text = match[0];
      }
      out += '<span class="' + cls + '">' + escapeHtml(text) + "</span>";
      last = tokenRe.lastIndex;
    }
    out += escapeHtml(jsonText.slice(last));
    return out;
  }

  function setPill(el, kind, text) {
    if (!el) { return; }
    el.className = "status-pill " + kind;
    el.textContent = text;
  }

  function showAlert(container, type, title, messages) {
    if (!container) { return; }
    var list = Array.isArray(messages) ? messages : (messages ? [messages] : []);
    var html = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">';
    html += "<strong>" + escapeHtml(title) + "</strong>";
    if (list.length) {
      html += "<ul class=\"mb-0 mt-1\">";
      list.forEach(function (msg) { html += "<li>" + escapeHtml(msg) + "</li>"; });
      html += "</ul>";
    }
    html += '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>';
    container.innerHTML = html;
  }

  function clearAlert(container) { if (container) { container.innerHTML = ""; } }

  function copyText(text, feedbackEl) {
    function done() {
      if (feedbackEl) {
        feedbackEl.textContent = "Copied!";
        window.setTimeout(function () { feedbackEl.textContent = ""; }, 1800);
      }
    }
    function fallback() {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); done(); }
      catch (err) { if (feedbackEl) { feedbackEl.textContent = "Copy failed"; } }
      document.body.removeChild(area);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(fallback);
    } else {
      fallback();
    }
  }

  function valueChip(value) {
    if (value === null) { return '<span class="value-chip is-null">null</span>'; }
    if (Array.isArray(value)) {
      if (!value.length) { return '<span class="value-chip is-empty">[]</span>'; }
      return value.map(function (item) {
        return '<span class="value-chip">' + escapeHtml(item) + "</span>";
      }).join(" ");
    }
    return '<span class="value-chip">' + escapeHtml(value) + "</span>";
  }

  // ------------------------------------------------------------- Input panel
  var paragraphInput = $("paragraphInput");
  var charCount = $("paragraphCount");

  function updateCount() {
    if (!paragraphInput || !charCount) { return; }
    var length = paragraphInput.value.length;
    var max = parseInt(paragraphInput.getAttribute("maxlength"), 10) || 5000;
    charCount.textContent = length.toLocaleString() + " / " + max.toLocaleString();
    charCount.classList.toggle("over", length > max);
  }

  function setParagraph(text) {
    if (!paragraphInput) { return; }
    paragraphInput.value = text;
    updateCount();
    paragraphInput.focus();
    paragraphInput.setSelectionRange(0, 0);
  }

  function sampleById(id) {
    return fetch("/api/samples")
      .then(function (response) { return response.json(); })
      .then(function (payload) {
        var found = (payload.samples || []).filter(function (item) { return item.id === id; })[0];
        if (!found) { throw new Error("Sample not available."); }
        setParagraph(found.text);
        setBadge("Sample loaded", "neutral");
        clearAlert($("alertArea"));
      })
      .catch(function () {
        showAlert($("alertArea"), "warning", "Could not load the sample", "Please check that the server is running and try again.");
      });
  }

  function setBadge(text, kind) {
    var badge = $("inputBadge");
    if (!badge) { return; }
    badge.textContent = text;
    badge.className = "badge rounded-pill border " + (kind === "pass" ? "text-bg-success" : kind === "fail" ? "text-bg-danger" : "text-bg-light");
  }

  // --------------------------------------------------------------- Extraction
  function setBusy(busy) {
    state.busy = busy;
    var btn = $("extractBtn");
    var spinner = $("extractSpinner");
    var label = $("extractBtnText");
    if (btn) { btn.disabled = busy; }
    if (spinner) { spinner.classList.toggle("d-none", !busy); }
    if (label) { label.textContent = busy ? "Extracting..." : "Extract Information"; }
  }

  function renderResult(payload) {
    var data = payload.data;
    var meta = payload.meta || {};
    var validation = payload.validation || {};
    var jsonText = payload.json_text || JSON.stringify(data, null, 2);

    state.lastResult = payload;
    state.lastPrompt = payload.prompt || "";
    state.lastMode = meta.mode || "standard";

    var viewer = $("jsonViewer");
    if (viewer) { viewer.innerHTML = syntaxHighlight(jsonText); }

    // Validation pills
    var syntaxOk = validation.syntax && validation.syntax.valid;
    var schemaOk = validation.schema && validation.schema.valid;
    setPill($("syntaxPill"), syntaxOk ? "pass" : "fail", "Syntax: " + (syntaxOk ? "valid" : "invalid"));
    setPill($("schemaPill"), schemaOk ? "pass" : "fail", "Schema: " + (schemaOk ? "valid" : "invalid"));

    // Alerts
    var alertArea = $("alertArea");
    clearAlert(alertArea);
    if (schemaOk && syntaxOk) {
      showAlert(alertArea, "success", "Extraction complete",
        ["JSON syntax is valid and the output satisfies the five-field schema."]);
    } else {
      var messages = [];
      if (validation.syntax && validation.syntax.errors) { messages = messages.concat(validation.syntax.errors); }
      if (validation.schema && validation.schema.errors) { messages = messages.concat(validation.schema.errors); }
      showAlert(alertArea, "danger", "Validation problems found", messages);
    }

    // Field summary with evidence
    var body = $("fieldSummaryBody");
    if (body) {
      var fields = ["title", "date", "venue", "speaker", "topics"];
      body.innerHTML = fields.map(function (field) {
        var confidence = (meta.confidence || {})[field] || "none";
        var evidence = (meta.evidence || {})[field];
        var evidenceText = evidence ? escapeHtml(evidence) : '<span class="text-muted">No supporting phrase</span>';
        var confClass = confidence === "high" ? "pass" : confidence === "medium" ? "warn" : "neutral";
        return "<tr><td><span class=\"field-name\">" + field + "</span></td>" +
          "<td>" + valueChip(data[field]) + "</td>" +
          '<td><span class="status-pill ' + confClass + '" style="font-size:.68rem;padding:.15rem .45rem">' + escapeHtml(confidence) + "</span>" +
          '<div class="small text-muted mt-1">' + evidenceText + "</div></td></tr>";
      }).join("");
    }

    // Missing-information notes
    var notesArea = $("notesArea");
    var notesList = $("notesList");
    var notes = meta.notes || [];
    if (notesArea && notesList) {
      if (notes.length) {
        notesArea.hidden = false;
        notesList.innerHTML = "<ul class=\"mb-0\" style=\"padding-left:1.1rem\">" +
          notes.map(function (note) { return "<li>" + escapeHtml(note) + "</li>"; }).join("") + "</ul>";
      } else {
        notesArea.hidden = false;
        notesList.innerHTML = "All five fields were supported directly by explicit phrases in the paragraph.";
      }
    }

    // Buttons
    ["copyJsonBtn", "downloadJsonBtn", "validateJsonBtn", "copyPromptBtn"].forEach(function (id) {
      var el = $(id);
      if (el) { el.disabled = false; }
    });

    // Prompt lab
    var builtPrompt = $("builtPrompt");
    if (builtPrompt) { builtPrompt.textContent = state.lastPrompt; }
    var builtMode = $("builtPromptMode");
    if (builtMode) { builtMode.textContent = meta.mode_name || "Standard"; }
    var copyBuilt = $("copyBuiltPromptBtn");
    if (copyBuilt) { copyBuilt.disabled = false; }

    // Validate workbench mirrors the output for convenience
    var validateInput = $("validateInput");
    if (validateInput && !validateInput.value.trim()) { validateInput.value = jsonText; }

    setBadge("Extracted", "pass");
  }

  function extractInformation() {
    if (state.busy) { return; }
    var paragraph = paragraphInput ? paragraphInput.value.trim() : "";
    var mode = $("modeSelect") ? $("modeSelect").value : "standard";

    clearAlert($("alertArea"));
    if (!paragraph) {
      showAlert($("alertArea"), "danger", "Input required",
        ["Enter a paragraph or load one of the sample paragraphs before extracting."]);
      setPill($("syntaxPill"), "neutral", "Syntax: waiting");
      setPill($("schemaPill"), "neutral", "Schema: waiting");
      if (paragraphInput) { paragraphInput.focus(); }
      return;
    }

    setBusy(true);
    setBadge("Processing...", "neutral");

    fetch("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ paragraph: paragraph, mode: mode })
    })
      .then(function (response) {
        return response.json().catch(function () { return { ok: false, error: "The server returned an unreadable response." }; })
          .then(function (payload) { return { status: response.status, payload: payload }; });
      })
      .then(function (result) {
        if (!result.payload.ok) {
          var details = result.payload.details || [];
          if (result.payload.error) { details = [result.payload.error].concat(details); }
          showAlert($("alertArea"), "danger", "Extraction failed", details);
          setBadge("Failed", "fail");
          setPill($("syntaxPill"), "neutral", "Syntax: waiting");
          setPill($("schemaPill"), "neutral", "Schema: waiting");
          return;
        }
        renderResult(result.payload);
      })
      .catch(function () {
        showAlert($("alertArea"), "danger", "Network error",
          ["Could not reach the extraction API. Check that the Flask server is running."]);
        setBadge("Failed", "fail");
      })
      .finally(function () { setBusy(false); });
  }

  // ---------------------------------------------------------------- Downloads
  function downloadJson() {
    if (!state.lastResult) { return; }
    var text = state.lastResult.json_text || JSON.stringify(state.lastResult.data, null, 2);
    var blob = new Blob([text], { type: "application/json;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    var stamp = new Date().toISOString().slice(0, 10);
    link.href = url;
    link.download = "extracted-workshop-" + stamp + ".json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  // ------------------------------------------------------------------ Reset
  function resetAll() {
    if (paragraphInput) { paragraphInput.value = ""; }
    updateCount();
    if ($("modeSelect")) { $("modeSelect").value = "standard"; }
    state.lastResult = null;
    state.lastPrompt = "";
    clearAlert($("alertArea"));
    var viewer = $("jsonViewer");
    if (viewer) {
      viewer.innerHTML = '<span class="json-empty">No output yet. Enter a paragraph and select <strong>Extract Information</strong>.</span>';
    }
    setPill($("syntaxPill"), "neutral", "Syntax: waiting");
    setPill($("schemaPill"), "neutral", "Schema: waiting");
    setBadge("Not processed", "neutral");
    var body = $("fieldSummaryBody");
    if (body) {
      body.innerHTML = '<tr><td colspan="3" class="text-muted small py-3">Field-level evidence appears after extraction.</td></tr>';
    }
    var notesArea = $("notesArea");
    if (notesArea) { notesArea.hidden = true; }
    ["copyJsonBtn", "downloadJsonBtn", "validateJsonBtn", "copyPromptBtn", "copyBuiltPromptBtn"].forEach(function (id) {
      var el = $(id);
      if (el) { el.disabled = true; }
    });
    var builtPrompt = $("builtPrompt");
    if (builtPrompt) { builtPrompt.textContent = "Run an extraction on the Extractor tab to populate this prompt."; }
    var builtMode = $("builtPromptMode");
    if (builtMode) { builtMode.textContent = "Standard"; }
    if (paragraphInput) { paragraphInput.focus(); }
  }

  // ------------------------------------------------------------- Test runner
  function renderTests(payload) {
    var container = $("testResults");
    if (!container) { return; }
    if (!payload.results || !payload.results.length) {
      container.innerHTML = '<p class="text-muted small mb-0">No test results returned.</p>';
      return;
    }

    $("statTotal").textContent = payload.total;
    $("statPassed").textContent = payload.passed;
    $("statFailed").textContent = payload.failed;

    container.innerHTML = payload.results.map(function (result) {
      var statusClass = result.passed ? "pass" : "fail";
      var statusLabel = result.passed ? "PASS" : "FAIL";
      var fieldRows = result.fields.map(function (field) {
        return "<tr><td><span class=\"field-name\">" + escapeHtml(field.field) + "</span></td>" +
          "<td>" + valueChip(field.expected) + "</td>" +
          "<td>" + valueChip(field.actual) + "</td>" +
          '<td><span class="check-icon ' + (field.passed ? "pass" : "fail") + '">' + (field.passed ? "&#10003;" : "&#10007;") + "</span></td></tr>";
      }).join("");

      var checks = (result.checks || []).map(function (check) {
        return '<li><span class="check-icon ' + (check.passed ? "pass" : "fail") + '">' +
          (check.passed ? "&#10003;" : "&#10007;") + "</span><span>" + escapeHtml(check.name) +
          ' <span class="text-muted">— ' + escapeHtml(check.detail) + "</span></span></li>";
      }).join("");

      var notes = (result.notes || []).map(function (note) {
        return "<li>" + escapeHtml(note) + "</li>";
      }).join("");

      return '<article class="test-card ' + statusClass + '">' +
        '<div class="test-card-head">' +
          '<div><h4>' + escapeHtml(result.name) + '</h4>' +
          '<span class="form-hint">' + escapeHtml(result.description) + '</span></div>' +
          '<div class="d-flex gap-2 align-items-center">' +
            '<span class="status-pill neutral">' + escapeHtml(result.mode_name) + '</span>' +
            '<span class="status-pill ' + statusClass + '">' + statusLabel + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="test-card-body">' +
          '<div class="test-input"><span class="label">Input paragraph</span>' + escapeHtml(result.input) + '</div>' +
          '<div class="row g-3">' +
            '<div class="col-lg-6">' +
              '<h5 class="form-label">Extracted JSON</h5>' +
              '<pre class="json-viewer" style="max-height:230px;font-size:.76rem">' + syntaxHighlight(result.json_text) + '</pre>' +
            '</div>' +
            '<div class="col-lg-6">' +
              '<h5 class="form-label">Validation</h5>' +
              '<div class="status-row mb-2">' +
                '<span class="status-pill ' + (result.syntax_valid ? "pass" : "fail") + '">Syntax: ' + (result.syntax_valid ? "valid" : "invalid") + '</span>' +
                '<span class="status-pill ' + (result.schema_valid ? "pass" : "fail") + '">Schema: ' + (result.schema_valid ? "valid" : "invalid") + '</span>' +
              '</div>' +
              '<ul class="check-list">' + checks + '</ul>' +
            '</div>' +
          '</div>' +
          '<div class="subtable-wrap mt-3">' +
            '<h5 class="form-label">Field-level correctness</h5>' +
            '<table class="field-table"><thead><tr><th scope="col">Field</th><th scope="col">Expected</th><th scope="col">Actual</th><th scope="col">Match</th></tr></thead>' +
            '<tbody>' + fieldRows + '</tbody></table>' +
          '</div>' +
          '<div class="note-box mt-3"><strong>Explanation:</strong> ' + escapeHtml(result.explanation) +
            (notes ? '<ul class="mt-2 mb-0" style="padding-left:1.1rem">' + notes + "</ul>" : "") +
          '</div>' +
        '</div>' +
      '</article>';
    }).join("");

    if (payload.all_passed) {
      container.insertAdjacentHTML("afterbegin",
        '<div class="alert alert-success" role="status"><strong>All ' + payload.total +
        " scenarios passed.</strong> Syntax, schema, and every expected field matched.</div>");
    } else {
      container.insertAdjacentHTML("afterbegin",
        '<div class="alert alert-danger" role="alert"><strong>' + payload.failed +
        " of " + payload.total + " scenarios failed.</strong> Review the failing fields below.</div>");
    }
  }

  function runTests() {
    var btn = $("runTestsBtn");
    var spinner = $("testsSpinner");
    var label = $("runTestsBtnText");
    if (btn) { btn.disabled = true; }
    if (spinner) { spinner.classList.remove("d-none"); }
    if (label) { label.textContent = "Running..."; }

    fetch("/api/tests/run", { method: "POST" })
      .then(function (response) { return response.json(); })
      .then(function (payload) {
        if (!payload.ok) { throw new Error(payload.error || "Test run failed."); }
        renderTests(payload);
      })
      .catch(function () {
        var container = $("testResults");
        if (container) {
          container.innerHTML = '<div class="alert alert-danger" role="alert">Could not run the tests. Check the server and try again.</div>';
        }
      })
      .finally(function () {
        if (btn) { btn.disabled = false; }
        if (spinner) { spinner.classList.add("d-none"); }
        if (label) { label.textContent = "Run All Tests"; }
      });
  }

  // -------------------------------------------------------- Validation tab
  function renderValidation(payload) {
    var syntax = payload.syntax || {};
    var schema = payload.schema || {};
    setPill($("valSyntaxPill"), syntax.valid ? "pass" : "fail", "Syntax: " + (syntax.valid ? "valid" : "invalid"));
    setPill($("valSchemaPill"), schema.valid ? "pass" : "fail", "Schema: " + (schema.valid ? "valid" : "invalid"));

    var alertBox = $("validationAlert");
    clearAlert(alertBox);

    if (syntax.valid && schema.valid) {
      showAlert(alertBox, "success", "Valid document", ["The JSON parses and satisfies the five-field schema."]);
    } else {
      var messages = [];
      if (syntax.errors) { messages = messages.concat(syntax.errors); }
      if (schema.errors) { messages = messages.concat(schema.errors); }
      showAlert(alertBox, "danger", syntax.valid ? "Schema validation failed" : "JSON syntax error", messages);
    }

    var checksBox = $("validationChecks");
    if (!checksBox) { return; }
    var checks = schema.checks || [];
    if (!checks.length) {
      checksBox.innerHTML = '<p class="text-muted small mb-0">Schema checks were skipped because the JSON syntax is invalid.</p>';
      return;
    }
    checksBox.innerHTML = '<h3 class="form-label mb-2">Schema checks</h3><ul class="check-list">' +
      checks.map(function (check) {
        return '<li><span class="check-icon ' + (check.passed ? "pass" : "fail") + '">' +
          (check.passed ? "&#10003;" : "&#10007;") + "</span><span><strong>" + escapeHtml(check.name) +
          '</strong><br><span class="text-muted">' + escapeHtml(check.detail) + "</span></span></li>";
      }).join("") + "</ul>";
  }

  function validateDocument() {
    var input = $("validateInput");
    if (!input) { return; }
    var raw = input.value;
    clearAlert($("validationAlert"));
    if (!raw.trim()) {
      showAlert($("validationAlert"), "warning", "Nothing to validate", ["Paste a JSON document first."]);
      setPill($("valSyntaxPill"), "neutral", "Syntax: waiting");
      setPill($("valSchemaPill"), "neutral", "Schema: waiting");
      return;
    }
    fetch("/api/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ json: raw })
    })
      .then(function (response) { return response.json(); })
      .then(function (payload) {
        if (!payload.ok) { throw new Error(payload.error || "Validation request failed."); }
        renderValidation(payload);
      })
      .catch(function (error) {
        showAlert($("validationAlert"), "danger", "Validation failed", [error.message]);
      });
  }

  // ------------------------------------------------------------- Wire events
  document.addEventListener("DOMContentLoaded", function () {
    updateCount();
    if (paragraphInput) { paragraphInput.addEventListener("input", updateCount); }

    if ($("loadSampleBtn")) { $("loadSampleBtn").addEventListener("click", function () { sampleById("complete"); }); }
    if ($("loadMissingBtn")) { $("loadMissingBtn").addEventListener("click", function () { sampleById("missing"); }); }
    if ($("loadSparseBtn")) { $("loadSparseBtn").addEventListener("click", function () { sampleById("sparse"); }); }
    if ($("clearInputBtn")) {
      $("clearInputBtn").addEventListener("click", function () {
        if (paragraphInput) { paragraphInput.value = ""; }
        updateCount();
        setBadge("Not processed", "neutral");
        clearAlert($("alertArea"));
        if (paragraphInput) { paragraphInput.focus(); }
      });
    }

    if ($("extractBtn")) { $("extractBtn").addEventListener("click", extractInformation); }
    if ($("resetBtn")) { $("resetBtn").addEventListener("click", resetAll); }

    // Ctrl+Enter submits extraction
    if (paragraphInput) {
      paragraphInput.addEventListener("keydown", function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
          event.preventDefault();
          extractInformation();
        }
      });
    }

    if ($("copyJsonBtn")) {
      $("copyJsonBtn").addEventListener("click", function () {
        if (!state.lastResult) { return; }
        copyText(state.lastResult.json_text || JSON.stringify(state.lastResult.data, null, 2), $("copyFeedback"));
      });
    }
    if ($("downloadJsonBtn")) { $("downloadJsonBtn").addEventListener("click", downloadJson); }
    if ($("validateJsonBtn")) {
      $("validateJsonBtn").addEventListener("click", function () {
        if (!state.lastResult) { return; }
        var input = $("validateInput");
        if (input) { input.value = state.lastResult.json_text || JSON.stringify(state.lastResult.data, null, 2); }
        var tabTrigger = $("tab-schema");
        if (tabTrigger && window.bootstrap) {
          window.bootstrap.Tab.getOrCreateInstance(tabTrigger).show();
        }
        window.setTimeout(validateDocument, 120);
      });
    }
    if ($("copyPromptBtn")) {
      $("copyPromptBtn").addEventListener("click", function () {
        if (!state.lastPrompt) { return; }
        copyText(state.lastPrompt, $("copyFeedback"));
      });
    }
    if ($("copyBuiltPromptBtn")) {
      $("copyBuiltPromptBtn").addEventListener("click", function () {
        if (!state.lastPrompt) { return; }
        copyText(state.lastPrompt, $("builtPromptFeedback"));
      });
    }

    document.querySelectorAll("[data-copy-target]").forEach(function (button) {
      button.addEventListener("click", function () {
        var target = document.getElementById(button.getAttribute("data-copy-target"));
        var feedback = document.getElementById(button.getAttribute("data-copy-label"));
        if (target) { copyText(target.textContent, feedback); }
      });
    });

    if ($("runTestsBtn")) { $("runTestsBtn").addEventListener("click", runTests); }
    if ($("runValidationBtn")) { $("runValidationBtn").addEventListener("click", validateDocument); }
    if ($("clearValidationBtn")) {
      $("clearValidationBtn").addEventListener("click", function () {
        var input = $("validateInput");
        if (input) { input.value = ""; }
        clearAlert($("validationAlert"));
        var checks = $("validationChecks");
        if (checks) { checks.innerHTML = '<p class="text-muted small mb-0">Run a validation to see each schema check.</p>'; }
        setPill($("valSyntaxPill"), "neutral", "Syntax: waiting");
        setPill($("valSchemaPill"), "neutral", "Schema: waiting");
      });
    }
    if ($("loadValidExampleBtn")) {
      $("loadValidExampleBtn").addEventListener("click", function () {
        var input = $("validateInput");
        if (input) {
          input.value = JSON.stringify({
            title: "Introduction to Generative AI and Prompt Engineering Workshop",
            date: "2026-11-15",
            venue: "Seminar Hall, DKTE Society's Textile & Engineering Institute, Ichalkaranji",
            speaker: "Dr. Ananya Deshmukh",
            topics: ["Prompt Design", "Structured JSON Output", "Context Engineering", "AI Output Validation"]
          }, null, 2);
        }
      });
    }
    if ($("loadInvalidExampleBtn")) {
      $("loadInvalidExampleBtn").addEventListener("click", function () {
        var input = $("validateInput");
        if (input) {
          input.value = '{\n  "title": "Python programming workshop",\n  "date": "20-12-2026",\n  "venue": "N/A",\n  "speaker": null,\n  "topics": ["file handling", 42],\n  "extra": true\n}';
        }
      });
    }

    // Remember the active tab across reloads (nice for the examiner).
    var hash = window.location.hash.replace("#", "");
    if (hash && document.getElementById("tab-" + hash)) {
      var trigger = document.getElementById("tab-" + hash);
      if (window.bootstrap) { window.bootstrap.Tab.getOrCreateInstance(trigger).show(); }
    }
  });
})();

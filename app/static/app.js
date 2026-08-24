/**
 * Software Blueprint AI — Frontend Interactive Application
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const projectIdeaInput = document.getElementById("projectIdeaInput");
  const charCount = document.getElementById("charCount");
  const blueprintForm = document.getElementById("blueprintForm");
  const generateBtn = document.getElementById("generateBtn");
  const chipBtns = document.querySelectorAll(".chip-btn");

  const loadingContainer = document.getElementById("loadingContainer");
  const loadingStage = document.getElementById("loadingStage");
  const loadingDescription = document.getElementById("loadingDescription");
  const stepReq = document.getElementById("stepReq");
  const stepPlan = document.getElementById("stepPlan");

  const errorAlert = document.getElementById("errorAlert");
  const errorMessage = document.getElementById("errorMessage");
  const closeErrorBtn = document.getElementById("closeErrorBtn");

  const resultsSection = document.getElementById("resultsSection");
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Summary Elements
  const displayProjectName = document.getElementById("displayProjectName");
  const displayProjectDesc = document.getElementById("displayProjectDesc");
  const statsTotalHours = document.getElementById("statsTotalHours");
  const statStakeholders = document.getElementById("statStakeholders");
  const statFRs = document.getElementById("statFRs");
  const statNFRs = document.getElementById("statNFRs");
  const statModules = document.getElementById("statModules");
  const statTasks = document.getElementById("statTasks");
  const statMilestones = document.getElementById("statMilestones");

  // Content Containers
  const roadmapTimeline = document.getElementById("roadmapTimeline");
  const overviewMilestonesGrid = document.getElementById("overviewMilestonesGrid");
  const overviewAmbiguitiesList = document.getElementById("overviewAmbiguitiesList");
  const overviewConstraintsList = document.getElementById("overviewConstraintsList");
  const overviewAssumptionsList = document.getElementById("overviewAssumptionsList");

  const stakeholderCountBadge = document.getElementById("stakeholderCountBadge");
  const stakeholdersGrid = document.getElementById("stakeholdersGrid");
  const functionalRequirementsList = document.getElementById("functionalRequirementsList");
  const nfrGrid = document.getElementById("nfrGrid");

  const modulesContainer = document.getElementById("modulesContainer");
  const totalTasksCountBadge = document.getElementById("totalTasksCountBadge");
  const tasksContainer = document.getElementById("tasksContainer");

  const traceabilityTableBody = document.getElementById("traceabilityTableBody");
  const rawJsonCode = document.getElementById("rawJsonCode");
  const copyJsonBtn = document.getElementById("copyJsonBtn");
  const downloadJsonBtn = document.getElementById("downloadJsonBtn");
  const downloadMdBtn = document.getElementById("downloadMdBtn");

  let currentBlueprint = null;
  let activeFilter = "all";

  // Check health on load
  checkServerHealth();

  // Character counter & shortcut listener
  projectIdeaInput.addEventListener("input", () => {
    const len = projectIdeaInput.value.length;
    charCount.textContent = `${len} character${len === 1 ? "" : "s"}`;
  });

  projectIdeaInput.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
      e.preventDefault();
      blueprintForm.dispatchEvent(new Event("submit"));
    }
  });

  // Template prompt chips
  chipBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      projectIdeaInput.value = btn.getAttribute("data-prompt");
      projectIdeaInput.dispatchEvent(new Event("input"));
      projectIdeaInput.focus();
    });
  });

  // Close error alert
  closeErrorBtn.addEventListener("click", () => {
    errorAlert.classList.add("hidden");
  });

  // Tab switching
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTabId = btn.getAttribute("data-tab");
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const activePane = document.getElementById(targetTabId);
      if (activePane) {
        activePane.classList.add("active");
      }
    });
  });

  // Functional Requirements Filter
  const filterChips = document.querySelectorAll(".filter-chip");
  filterChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      filterChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      activeFilter = chip.getAttribute("data-filter");
      renderFunctionalRequirements();
    });
  });

  // Copy JSON button
  copyJsonBtn.addEventListener("click", () => {
    if (!currentBlueprint) return;
    navigator.clipboard.writeText(JSON.stringify(currentBlueprint, null, 2)).then(() => {
      const originalText = copyJsonBtn.innerHTML;
      copyJsonBtn.innerHTML = `✓ Copied!`;
      setTimeout(() => {
        copyJsonBtn.innerHTML = originalText;
      }, 2000);
    });
  });

  // Download JSON button
  downloadJsonBtn.addEventListener("click", () => {
    if (!currentBlueprint) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentBlueprint, null, 2));
    const dlAnchor = document.createElement("a");
    const safeName = (currentBlueprint.requirements?.project_name || "software-blueprint")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `${safeName}-blueprint.json`);
    dlAnchor.click();
  });

  // Download Markdown button
  downloadMdBtn.addEventListener("click", () => {
    if (!currentBlueprint) return;
    const mdContent = generateMarkdownReport(currentBlueprint);
    const dataStr = "data:text/markdown;charset=utf-8," + encodeURIComponent(mdContent);
    const dlAnchor = document.createElement("a");
    const safeName = (currentBlueprint.requirements?.project_name || "software-blueprint")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `${safeName}-blueprint.md`);
    dlAnchor.click();
  });

  // Form Submit Handler
  blueprintForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const idea = projectIdeaInput.value.trim();
    if (!idea || idea.length < 5) {
      showError("Please enter a descriptive project idea of at least 5 characters.");
      return;
    }

    // UI Loading State
    errorAlert.classList.add("hidden");
    resultsSection.classList.add("hidden");
    loadingContainer.classList.remove("hidden");
    generateBtn.disabled = true;

    // Simulate Agent Step Progression
    stepReq.classList.add("active");
    stepPlan.classList.remove("active");
    loadingStage.textContent = "Executing Module 1: Requirement Analysis Agent...";
    loadingDescription.textContent = "Analyzing stakeholders, eliciting functional & non-functional requirements, constraints, and ambiguities...";

    const stepInterval = setTimeout(() => {
      stepPlan.classList.add("active");
      loadingStage.textContent = "Executing Module 2: Project Planning Agent...";
      loadingDescription.textContent = "Synthesizing cohesive modules, DAG task scheduling, effort hours, milestones, and development roadmap...";
    }, 4500);

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_idea: idea })
      });

      clearTimeout(stepInterval);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: "Network request failed" }));
        throw new Error(errData.detail || `Server error (${response.status})`);
      }

      const blueprint = await response.json();
      currentBlueprint = blueprint;

      // Render Results
      renderBlueprint(blueprint);
      loadingContainer.classList.add("hidden");
      resultsSection.classList.remove("hidden");

      // Smooth scroll down to results
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (err) {
      clearTimeout(stepInterval);
      loadingContainer.classList.add("hidden");
      showError(err.message || "Failed to connect to Blueprint AI server or Ollama.");
    } finally {
      generateBtn.disabled = false;
    }
  });

  // Check Server Health
  async function checkServerHealth() {
    const statusText = document.querySelector("#ollamaStatus .status-text");
    const statusDot = document.querySelector("#ollamaStatus .status-dot");
    try {
      const res = await fetch("/health");
      if (res.ok) {
        statusText.textContent = "Ollama: Qwen 2.5 3B (Ready)";
        statusDot.classList.add("online");
      }
    } catch {
      statusText.textContent = "Server Offline";
      statusDot.classList.remove("online");
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorAlert.classList.remove("hidden");
  }

  // Render Full Blueprint Data
  function renderBlueprint(data) {
    const reqs = data.requirements || {};
    const plan = data.project_plan || {};

    // Hero Meta
    displayProjectName.textContent = reqs.project_name || "Software Blueprint";
    displayProjectDesc.textContent = reqs.project_description || "";

    // Stats
    const totalHours = (plan.tasks || []).reduce((sum, t) => sum + (Number(t.estimated_hours) || 0), 0);
    statsTotalHours.textContent = `${totalHours.toFixed(1)} Hours Total Effort`;
    statStakeholders.textContent = (reqs.stakeholders || []).length;
    statFRs.textContent = (reqs.functional_requirements || []).length;
    statNFRs.textContent = (reqs.non_functional_requirements || []).length;
    statModules.textContent = (plan.modules || []).length;
    statTasks.textContent = (plan.tasks || []).length;
    statMilestones.textContent = (plan.milestones || []).length;

    // Render Tabs
    renderOverview(reqs, plan);
    renderStakeholders(reqs.stakeholders || []);
    renderFunctionalRequirements();
    renderNFRs(reqs.non_functional_requirements || []);
    renderModules(plan.modules || []);
    renderTasks(plan.tasks || []);
    renderTraceability(reqs, plan);

    // Raw JSON
    rawJsonCode.textContent = JSON.stringify(data, null, 2);
  }

  // Render Tab 1: Overview
  function renderOverview(reqs, plan) {
    // Roadmap
    roadmapTimeline.innerHTML = "";
    (plan.roadmap || []).forEach((phase) => {
      const item = document.createElement("div");
      item.className = "timeline-item";
      item.innerHTML = `<div class="timeline-title">${escapeHtml(phase)}</div>`;
      roadmapTimeline.appendChild(item);
    });

    // Milestones
    overviewMilestonesGrid.innerHTML = "";
    (plan.milestones || []).forEach((m) => {
      const card = document.createElement("div");
      card.className = "milestone-card";
      card.innerHTML = `
        <div class="milestone-id">${escapeHtml(m.id)}</div>
        <div class="milestone-name">${escapeHtml(m.name)}</div>
        <div class="milestone-desc">${escapeHtml(m.description)}</div>
      `;
      overviewMilestonesGrid.appendChild(card);
    });

    // Ambiguities
    overviewAmbiguitiesList.innerHTML = "";
    if (reqs.ambiguities && reqs.ambiguities.length > 0) {
      reqs.ambiguities.forEach((amb) => {
        const item = document.createElement("div");
        item.className = "ambiguity-item";
        item.innerHTML = `
          <div class="ambiguity-text">⚠️ ${escapeHtml(amb.ambiguity)}</div>
          <div class="clarification-tip">💡 <strong>Suggested Clarification:</strong> ${escapeHtml(amb.possible_clarification)}</div>
        `;
        overviewAmbiguitiesList.appendChild(item);
      });
    } else {
      overviewAmbiguitiesList.innerHTML = `<p class="st-desc">No critical ambiguities detected.</p>`;
    }

    // Constraints & Assumptions
    overviewConstraintsList.innerHTML = "";
    (reqs.constraints || []).forEach((c) => {
      const li = document.createElement("li");
      li.textContent = c;
      overviewConstraintsList.appendChild(li);
    });

    overviewAssumptionsList.innerHTML = "";
    (reqs.assumptions || []).forEach((a) => {
      const li = document.createElement("li");
      li.textContent = a;
      overviewAssumptionsList.appendChild(li);
    });
  }

  // Render Stakeholders
  function renderStakeholders(stakeholders) {
    stakeholderCountBadge.textContent = `${stakeholders.length} Roles`;
    stakeholdersGrid.innerHTML = "";
    stakeholders.forEach((st) => {
      const card = document.createElement("div");
      card.className = "stakeholder-card";
      card.innerHTML = `
        <div class="st-header">
          <span class="st-id">${escapeHtml(st.id)}</span>
          <span class="st-name">${escapeHtml(st.name)}</span>
        </div>
        <div class="st-desc">${escapeHtml(st.description)}</div>
      `;
      stakeholdersGrid.appendChild(card);
    });
  }

  // Render Functional Requirements with Filtering
  function renderFunctionalRequirements() {
    if (!currentBlueprint || !currentBlueprint.requirements) return;
    const frs = currentBlueprint.requirements.functional_requirements || [];
    functionalRequirementsList.innerHTML = "";

    const filtered = frs.filter((fr) => {
      if (activeFilter === "all") return true;
      return fr.priority?.toLowerCase() === activeFilter.toLowerCase();
    });

    if (filtered.length === 0) {
      functionalRequirementsList.innerHTML = `<p class="st-desc" style="padding: 12px;">No functional requirements matching priority "${activeFilter}".</p>`;
      return;
    }

    filtered.forEach((fr) => {
      const card = document.createElement("div");
      card.className = "fr-card";
      const priClass = getPriorityBadgeClass(fr.priority);

      const stakeholdersHtml = (fr.stakeholders || [])
        .map((s) => `<span class="stakeholder-tag">${escapeHtml(s)}</span>`)
        .join(" ");

      card.innerHTML = `
        <div class="fr-header">
          <div class="fr-id-title">
            <span class="fr-id">${escapeHtml(fr.id)}</span>
            <span class="fr-title">${escapeHtml(fr.title)}</span>
          </div>
          <span class="priority-badge ${priClass}">${escapeHtml(fr.priority || "Must")}</span>
        </div>
        <div class="fr-desc">${escapeHtml(fr.description)}</div>
        <div class="fr-footer">
          <span>Target Stakeholders:</span>
          ${stakeholdersHtml || '<span class="st-desc">None</span>'}
        </div>
      `;
      functionalRequirementsList.appendChild(card);
    });
  }

  // Render Non-Functional Requirements
  function renderNFRs(nfrs) {
    nfrGrid.innerHTML = "";
    nfrs.forEach((nfr) => {
      const card = document.createElement("div");
      card.className = "nfr-card";
      const priClass = getPriorityBadgeClass(nfr.priority);
      card.innerHTML = `
        <div class="nfr-header">
          <span class="nfr-id">${escapeHtml(nfr.id)}</span>
          <span class="nfr-category">${escapeHtml(nfr.category || "General")}</span>
          <span class="priority-badge ${priClass}">${escapeHtml(nfr.priority || "Must")}</span>
        </div>
        <div class="nfr-desc">${escapeHtml(nfr.description)}</div>
      `;
      nfrGrid.appendChild(card);
    });
  }

  // Render Modules
  function renderModules(modules) {
    modulesContainer.innerHTML = "";
    modules.forEach((mod) => {
      const card = document.createElement("div");
      card.className = "module-card";
      const reqTags = (mod.requirement_ids || [])
        .map((id) => `<span class="code-tag">${escapeHtml(id)}</span>`)
        .join(" ");

      card.innerHTML = `
        <span class="module-id">${escapeHtml(mod.id)}</span>
        <div class="module-name">${escapeHtml(mod.name)}</div>
        <div class="module-desc">${escapeHtml(mod.description)}</div>
        <div class="module-reqs-tags">
          <span style="font-size: 0.75rem; color: var(--text-muted);">Mapped Reqs:</span>
          ${reqTags || '<span class="st-desc">None</span>'}
        </div>
      `;
      modulesContainer.appendChild(card);
    });
  }

  // Render Tasks
  function renderTasks(tasks) {
    totalTasksCountBadge.textContent = `${tasks.length} Tasks`;
    tasksContainer.innerHTML = "";
    tasks.forEach((t) => {
      const card = document.createElement("div");
      card.className = "task-card";
      const priClass = getPriorityBadgeClass(t.priority);

      const reqTags = (t.requirement_ids || [])
        .map((id) => `<span class="code-tag">${escapeHtml(id)}</span>`)
        .join(" ");

      const depTags = (t.dependencies && t.dependencies.length > 0)
        ? t.dependencies.map((d) => `<span class="code-tag">${escapeHtml(d)}</span>`).join(" ")
        : '<span style="color: var(--text-muted);">None (Root)</span>';

      card.innerHTML = `
        <div class="task-header">
          <div class="task-id-title">
            <span class="task-id">${escapeHtml(t.id)}</span>
            <span class="task-title">${escapeHtml(t.title)}</span>
          </div>
          <span class="priority-badge ${priClass}">${escapeHtml(t.priority || "Must")}</span>
        </div>
        <div class="task-desc">${escapeHtml(t.description)}</div>
        <div class="task-meta-row">
          <span class="task-hours">⏱️ ${t.estimated_hours || 4} hrs</span>
          <div class="task-req-links">
            <span>📌 Addresses:</span>
            ${reqTags}
          </div>
          <div class="task-deps">
            <span>🔗 Prerequisite:</span>
            ${depTags}
          </div>
        </div>
      `;
      tasksContainer.appendChild(card);
    });
  }

  // Render Traceability Table
  function renderTraceability(reqs, plan) {
    traceabilityTableBody.innerHTML = "";
    const frs = reqs.functional_requirements || [];
    const tasks = plan.tasks || [];
    const modules = plan.modules || [];

    frs.forEach((fr) => {
      const linkedTasks = tasks.filter((t) => (t.requirement_ids || []).includes(fr.id));
      const linkedMod = modules.find((m) => (m.requirement_ids || []).includes(fr.id));

      const row = document.createElement("tr");
      const priClass = getPriorityBadgeClass(fr.priority);

      const taskChips = linkedTasks.length > 0
        ? linkedTasks.map((t) => `<span class="code-tag" title="${escapeHtml(t.title)}">${escapeHtml(t.id)}: ${escapeHtml(t.title.substring(0, 24))}...</span>`).join("<br>")
        : '<span style="color: #f43f5e;">Unassigned (0 Tasks)</span>';

      const modName = linkedMod ? `<span class="code-tag">${escapeHtml(linkedMod.id)}: ${escapeHtml(linkedMod.name)}</span>` : '<span style="color: var(--text-muted);">None</span>';

      row.innerHTML = `
        <td><span class="fr-id">${escapeHtml(fr.id)}</span></td>
        <td><strong>${escapeHtml(fr.title)}</strong><br><small style="color: var(--text-secondary);">${escapeHtml(fr.description.substring(0, 70))}...</small></td>
        <td><span class="priority-badge ${priClass}">${escapeHtml(fr.priority || "Must")}</span></td>
        <td>${modName}</td>
        <td>${taskChips}</td>
      `;
      traceabilityTableBody.appendChild(row);
    });
  }

  // Priority Badge Class Helper
  function getPriorityBadgeClass(priority) {
    const p = (priority || "").toLowerCase();
    if (p.includes("must")) return "priority-must";
    if (p.includes("should")) return "priority-should";
    if (p.includes("could")) return "priority-could";
    return "priority-wont";
  }

  // HTML escaping utility
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Generate Markdown Document
  function generateMarkdownReport(data) {
    const reqs = data.requirements || {};
    const plan = data.project_plan || {};

    let md = `# Software Engineering Blueprint: ${reqs.project_name || "Project"}\n\n`;
    md += `## 1. Executive Summary\n${reqs.project_description || ""}\n\n`;

    md += `## 2. Stakeholders\n`;
    (reqs.stakeholders || []).forEach((st) => {
      md += `- **${st.id} (${st.name})**: ${st.description}\n`;
    });
    md += `\n`;

    md += `## 3. Functional Requirements (FR)\n`;
    (reqs.functional_requirements || []).forEach((fr) => {
      md += `### ${fr.id}: ${fr.title} [Priority: ${fr.priority}]\n`;
      md += `${fr.description}\n`;
      md += `- **Stakeholders**: ${(fr.stakeholders || []).join(", ") || "None"}\n\n`;
    });

    md += `## 4. Non-Functional Requirements (NFR)\n`;
    (reqs.non_functional_requirements || []).forEach((nfr) => {
      md += `- **${nfr.id} [${nfr.category}]**: ${nfr.description} *(Priority: ${nfr.priority})*\n`;
    });
    md += `\n`;

    md += `## 5. Development Modules\n`;
    (plan.modules || []).forEach((mod) => {
      md += `### ${mod.id}: ${mod.name}\n${mod.description}\n`;
      md += `- **Mapped Requirements**: ${(mod.requirement_ids || []).join(", ") || "None"}\n\n`;
    });

    md += `## 6. Work Breakdown Structure (Tasks & Dependencies)\n`;
    (plan.tasks || []).forEach((t) => {
      const deps = (t.dependencies || []).length > 0 ? t.dependencies.join(", ") : "None";
      md += `### ${t.id}: ${t.title}\n`;
      md += `${t.description}\n`;
      md += `- **Estimated Hours**: ${t.estimated_hours} hrs\n`;
      md += `- **Priority**: ${t.priority}\n`;
      md += `- **Requirement IDs**: ${(t.requirement_ids || []).join(", ")}\n`;
      md += `- **Dependencies**: ${deps}\n\n`;
    });

    md += `## 7. Milestones & Roadmap\n`;
    (plan.milestones || []).forEach((m) => {
      md += `- **${m.id} (${m.name})**: ${m.description}\n`;
    });
    md += `\n### Roadmap Phases:\n`;
    (plan.roadmap || []).forEach((phase, idx) => {
      md += `${idx + 1}. ${phase}\n`;
    });

    return md;
  }
});

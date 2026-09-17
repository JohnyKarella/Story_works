// ── Storyworks Admin Interactions ──
document.addEventListener("DOMContentLoaded", () => {
  // Auto-dismiss alerts after 5s
  setTimeout(() => {
    document.querySelectorAll(".flash-alert").forEach((el) => {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.5s ease";
      setTimeout(() => el.remove(), 500);
    });
  }, 5000);
  // Close modals on escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAllModals();
    }
  });
  // Close modal when clicking overlay outside modal-box
  document.querySelectorAll(".modal-overlay").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeAllModals();
      }
    });
  });
  // Mobile menu toggle & drawer handling
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.querySelector(".sidebar");
  const sidebarBackdrop = document.getElementById("sidebarBackdrop");
  const sidebarClose = document.getElementById("sidebarClose");

  function toggleSidebar(open) {
    if (!sidebar) return;
    const shouldOpen = open !== undefined ? open : !sidebar.classList.contains("open");
    if (shouldOpen) {
      sidebar.classList.add("open");
      if (sidebarBackdrop) sidebarBackdrop.classList.add("active");
      document.body.style.overflow = "hidden";
    } else {
      sidebar.classList.remove("open");
      if (sidebarBackdrop) sidebarBackdrop.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  if (menuToggle) {
    menuToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSidebar();
    });
  }
  if (sidebarClose) {
    sidebarClose.addEventListener("click", () => toggleSidebar(false));
  }
  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener("click", () => toggleSidebar(false));
  }
  // Auto-close sidebar on nav link click on mobile
  document.querySelectorAll(".sidebar .nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 992) {
        toggleSidebar(false);
      }
    });
  });
  // Initialize real-time new message pop-up notification listener
  initAdminNotificationPoller();
});
function closeAllModals() {
  document.querySelectorAll(".modal-overlay").forEach((m) => {
    m.classList.remove("active");
  });
}
function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add("active");
}
// Format exact date & time helper for admin
function formatExactDateTime(isoStr) {
  if (!isoStr) return "—";
  try {
    const d = new Date(isoStr.replace(" ", "T"));
    if (isNaN(d.getTime())) return isoStr;
    return d.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
    });
  } catch (e) {
    return isoStr;
  }
}

// Inquiry View Modal
function viewInquiry(item) {
  const nameEl = document.getElementById("modalInquiryName");
  if (nameEl) nameEl.textContent = `${item.first_name} ${item.last_name || ""}`;
  
  const emailEl = document.getElementById("modalInquiryEmail");
  if (emailEl) {
    emailEl.textContent = item.email;
    emailEl.href = `mailto:${item.email}`;
  }

  const phoneEl = document.getElementById("modalInquiryPhone");
  if (phoneEl) {
    phoneEl.textContent = item.phone || "—";
    if (item.phone) {
      phoneEl.href = `tel:${item.phone}`;
    } else {
      phoneEl.removeAttribute("href");
    }
  }

  const companyEl = document.getElementById("modalInquiryCompany");
  if (companyEl) companyEl.textContent = item.company || "—";

  const budgetEl = document.getElementById("modalInquiryBudget");
  if (budgetEl) budgetEl.textContent = item.budget || "—";

  const servicesEl = document.getElementById("modalInquiryServices");
  if (servicesEl) servicesEl.textContent = item.services || "None specified";

  const formattedCreated = formatExactDateTime(item.created_at);
  const dateEl = document.getElementById("modalInquiryDate");
  if (dateEl) dateEl.textContent = formattedCreated;

  const formattedUpdated = formatExactDateTime(item.updated_at || item.created_at);
  const updatedEl = document.getElementById("modalInquiryUpdated");
  if (updatedEl) updatedEl.textContent = formattedUpdated;

  const timelineVal = item.timeline || "1 – 2 Months (Standard)";
  const timelinePill = document.getElementById("modalInquiryTimeline");
  if (timelinePill) timelinePill.innerHTML = `<i class="far fa-hourglass"></i> Target: ${timelineVal}`;
  const timelineValEl = document.getElementById("modalInquiryTimelineVal");
  if (timelineValEl) timelineValEl.textContent = timelineVal;

  const messageEl = document.getElementById("modalInquiryMessage");
  if (messageEl) messageEl.textContent = item.message;

  // Milestone Stepper Logic for Admin
  const s1 = document.getElementById("adminStep1");
  const s2 = document.getElementById("adminStep2");
  const s3 = document.getElementById("adminStep3");
  const s4 = document.getElementById("adminStep4");

  if (s1 && s2 && s3 && s4) {
    const s1Icon = s1.querySelector(".admin-node-icon");
    const s2Icon = s2.querySelector(".admin-node-icon");
    const s3Icon = s3.querySelector(".admin-node-icon");
    const s4Icon = s4.querySelector(".admin-node-icon");

    // Helper to set active/completed/pending
    const setNode = (node, icon, state) => {
      if (state === "completed") {
        icon.style.background = "#10b981";
        icon.style.borderColor = "#10b981";
        icon.style.color = "#fff";
      } else if (state === "active") {
        icon.style.background = "var(--primary)";
        icon.style.borderColor = "var(--primary)";
        icon.style.color = "#fff";
      } else {
        icon.style.background = "var(--bg-card)";
        icon.style.borderColor = "var(--border-color)";
        icon.style.color = "var(--text-dim)";
      }
    };

    setNode(s1, s1Icon, "completed");
    const st = (item.status || "new").toLowerCase();

    if (st === "new") {
      setNode(s2, s2Icon, "active");
      setNode(s3, s3Icon, "pending");
      setNode(s4, s4Icon, "pending");
    } else if (st === "contacted") {
      setNode(s2, s2Icon, "completed");
      setNode(s3, s3Icon, "active");
      setNode(s4, s4Icon, "pending");
    } else if (st === "in_progress") {
      setNode(s2, s2Icon, "completed");
      setNode(s3, s3Icon, "completed");
      setNode(s4, s4Icon, "active");
    } else {
      setNode(s2, s2Icon, "completed");
      setNode(s3, s3Icon, "completed");
      setNode(s4, s4Icon, "completed");
    }
  }

  // Client Account Timeline Info (if registered)
  const clientWrap = document.getElementById("modalInquiryClientWrap");
  if (clientWrap) {
    if (item.user_id || item.client_username) {
      clientWrap.style.display = "block";
      const uEl = document.getElementById("modalInquiryClientUsername");
      if (uEl) uEl.textContent = item.client_username ? `@${item.client_username}` : "Registered Client";
      const cCreatedEl = document.getElementById("modalInquiryClientCreated");
      if (cCreatedEl) cCreatedEl.textContent = formatExactDateTime(item.client_created_at);
      const cLoginEl = document.getElementById("modalInquiryClientLastLogin");
      if (cLoginEl) cLoginEl.textContent = formatExactDateTime(item.client_last_login);
    } else {
      clientWrap.style.display = "none";
    }
  }

  // Status form action
  const statusForm = document.getElementById("modalStatusForm");
  if (statusForm) {
    statusForm.action = `/admin/inquiries/${item.id}/status`;
    const sel = statusForm.querySelector('select[name="status"]');
    if (sel) sel.value = item.status;
  }
  // Notes form action
  const notesForm = document.getElementById("modalNotesForm");
  if (notesForm) {
    notesForm.action = `/admin/inquiries/${item.id}/notes`;
    const txt = notesForm.querySelector('textarea[name="notes"]');
    if (txt) txt.value = item.notes || "";
  }
  openModal("inquiryModal");
}
// Service Edit Modal (with robust null guards and dataset support)
function openEditService(serviceOrBtn) {
  let service = serviceOrBtn;
  if (serviceOrBtn instanceof HTMLElement) {
    const d = serviceOrBtn.dataset;
    service = {
      id: d.id,
      title: d.title || "",
      slug: d.slug || "",
      short_desc: d.shortDesc || "",
      full_desc: d.fullDesc || "",
      icon: d.icon || "",
      display_order: d.order || 0,
      is_active: d.active === "1" || d.active === "true"
    };
  }
  const form = document.getElementById("editServiceForm");
  if (!form || !service) return;
  form.action = `/admin/services/${service.id}/edit`;
  const setInputVal = (selector, val) => {
    const el = form.querySelector(selector);
    if (el) el.value = val !== undefined && val !== null ? val : "";
  };
  setInputVal('input[name="title"]', service.title);
  setInputVal('input[name="slug"]', service.slug);
  setInputVal('input[name="short_desc"]', service.short_desc);
  setInputVal('textarea[name="full_desc"]', service.full_desc);
  setInputVal('input[name="icon"]', service.icon);
  setInputVal('input[name="display_order"]', service.display_order || 0);
  const activeCheckbox = form.querySelector('input[name="is_active"]');
  if (activeCheckbox) {
    activeCheckbox.checked = Boolean(service.is_active);
  }
  openModal("editServiceModal");
}
// Quick image preview on file input change
function previewImage(input, previewId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.getElementById(previewId);
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = "block";
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}
// ── Real-Time Admin New Message Pop-Up Notifications ──
let lastKnownInquiryId = parseInt(sessionStorage.getItem("lastInquiryId") || "0", 10);
function initAdminNotificationPoller() {
  let container = document.getElementById("adminToastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "adminToastContainer";
    container.className = "admin-toast-container";
    document.body.appendChild(container);
  }
  // Poll every 4 seconds
  setInterval(checkNewInquiries, 4000);
  checkNewInquiries();
}
async function checkNewInquiries() {
  try {
    const res = await fetch("/admin/api/unread-inquiries");
    if (!res.ok) return;
    const data = await res.json();
    if (!data.success) return;
    // Update sidebar badge
    updateInquiryBadge(data.unread_count);
    if (data.latest && data.latest.id) {
      if (lastKnownInquiryId === 0) {
        lastKnownInquiryId = data.latest.id;
        sessionStorage.setItem("lastInquiryId", String(lastKnownInquiryId));
        return;
      }
      if (data.latest.id > lastKnownInquiryId) {
        lastKnownInquiryId = data.latest.id;
        sessionStorage.setItem("lastInquiryId", String(lastKnownInquiryId));
        showAdminNotificationToast(data.latest);
        playNotificationChime();
      }
    }
  } catch (err) {
    // Silently ignore network polling errors
  }
}
function updateInquiryBadge(count) {
  const inquiriesLink = document.querySelector(".sidebar-nav a[href*='inquiries']");
  if (!inquiriesLink) return;
  let badgeEl = inquiriesLink.querySelector(".nav-badge");
  if (count > 0) {
    if (badgeEl) {
      badgeEl.textContent = count;
    } else {
      const newBadge = document.createElement("span");
      newBadge.className = "nav-badge";
      newBadge.textContent = count;
      inquiriesLink.appendChild(newBadge);
    }
  } else if (badgeEl) {
    badgeEl.remove();
  }
}
function showAdminNotificationToast(inquiry) {
  const container = document.getElementById("adminToastContainer") || document.body;
  const card = document.createElement("div");
  card.className = "admin-toast-card";
  const clientName = `${inquiry.first_name || ""} ${inquiry.last_name || ""}`.trim() || "New Client";
  const companyStr = inquiry.company ? ` (${inquiry.company})` : "";
  const msgPreview = inquiry.message || "New message received.";
  card.innerHTML = `
    <div class="admin-toast-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
      </svg>
    </div>
    <div class="admin-toast-body">
      <span class="admin-toast-badge">🔔 New Message Received!</span>
      <div class="admin-toast-title">${escapeHtml(clientName)}${escapeHtml(companyStr)}</div>
      <div class="admin-toast-msg">"${escapeHtml(msgPreview)}"</div>
      <div class="admin-toast-actions">
        <a href="/admin/inquiries" class="admin-toast-btn">View Inquiry →</a>
      </div>
    </div>
    <button type="button" class="admin-toast-close" title="Dismiss">&times;</button>
  `;
  card.querySelector(".admin-toast-close").onclick = () => {
    card.style.opacity = "0";
    card.style.transform = "translateX(50px)";
    setTimeout(() => card.remove(), 300);
  };
  container.appendChild(card);
  // Auto-dismiss after 12 seconds
  setTimeout(() => {
    if (card.parentNode) {
      card.style.opacity = "0";
      card.style.transform = "translateX(50px)";
      setTimeout(() => card.remove(), 300);
    }
  }, 12000);
}
function playNotificationChime() {
  try {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx();
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    osc1.type = "sine";
    osc2.type = "sine";
    osc1.frequency.setValueAtTime(587.33, ctx.currentTime);
    osc2.frequency.setValueAtTime(880, ctx.currentTime + 0.12);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);
    osc1.start(ctx.currentTime);
    osc1.stop(ctx.currentTime + 0.14);
    osc2.start(ctx.currentTime + 0.12);
    osc2.stop(ctx.currentTime + 0.6);
  } catch (e) {}
}
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

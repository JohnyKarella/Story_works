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
  // Mobile menu toggle if button exists
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.querySelector(".sidebar");
  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });
  }
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
// Inquiry View Modal
function viewInquiry(item) {
  document.getElementById("modalInquiryName").textContent = `${item.first_name} ${item.last_name || ""}`;
  document.getElementById("modalInquiryEmail").textContent = item.email;
  document.getElementById("modalInquiryEmail").href = `mailto:${item.email}`;
  document.getElementById("modalInquiryPhone").textContent = item.phone || "—";
  if (item.phone) {
    document.getElementById("modalInquiryPhone").href = `tel:${item.phone}`;
  } else {
    document.getElementById("modalInquiryPhone").removeAttribute("href");
  }
  document.getElementById("modalInquiryCompany").textContent = item.company || "—";
  document.getElementById("modalInquiryBudget").textContent = item.budget || "—";
  document.getElementById("modalInquiryServices").textContent = item.services || "None specified";
  document.getElementById("modalInquiryDate").textContent = item.created_at;
  document.getElementById("modalInquiryMessage").textContent = item.message;
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

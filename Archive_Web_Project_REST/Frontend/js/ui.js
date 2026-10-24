import { api, session } from "./api.js";

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[ch]);
}

export function toast(message, type = "info") {
  let root = document.getElementById("toast-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "toast-root";
    document.body.appendChild(root);
  }
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.setAttribute("role", "status");
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

export function flash(message, type = "success") {
  sessionStorage.setItem("archive.flash", JSON.stringify({ message, type }));
}

function showFlash() {
  const raw = sessionStorage.getItem("archive.flash");
  if (!raw) return;
  sessionStorage.removeItem("archive.flash");
  const { message, type } = JSON.parse(raw);
  toast(message, type);
}

export function requireAuth() {
  if (!session.isLoggedIn) {
    const next = encodeURIComponent(location.pathname.split("/").pop() + location.search);
    location.replace(`login.html?next=${next}`);
    return false;
  }
  return true;
}

const NAV_LINKS = [
  { href: "index.html", label: "Browse" },
  { href: "submit.html", label: "Submit", auth: true },
  { href: "profile.html", label: "Profile", auth: true },
];

function renderHeader() {
  const current = location.pathname.split("/").pop() || "index.html";
  const loggedIn = session.isLoggedIn;
  const links = NAV_LINKS.filter((link) => !link.auth || loggedIn)
    .map((link) => `<a href="${link.href}" class="nav-link ${current === link.href ? "active" : ""}">${link.label}</a>`)
    .join("");
  const authLinks = loggedIn
    ? `<button type="button" data-logout class="nav-link">Log out</button>`
    : `<a href="login.html" class="nav-link ${current === "login.html" ? "active" : ""}">Log in</a>
       <a href="register.html" class="btn btn-primary">Create account</a>`;

  document.getElementById("app-header").innerHTML = `
    <header class="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav class="container-page flex h-16 items-center justify-between gap-4">
        <a href="index.html" class="flex shrink-0 items-center gap-3">
          <img src="assets/logo.png" class="h-10 w-10 object-contain" alt="BAUET logo" />
          <span class="leading-tight">
            <span class="block text-base font-bold text-slate-900">BAUET Archive</span>
            <span class="hidden text-xs text-slate-500 sm:block">Projects &amp; Theses</span>
          </span>
        </a>
        <div class="hidden items-center gap-1 md:flex">${links}${authLinks}</div>
        <button type="button" data-menu class="btn btn-ghost px-2 md:hidden" aria-expanded="false" aria-controls="mobile-menu">
          <span class="sr-only">Open menu</span>
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" aria-hidden="true"><path stroke="currentColor" stroke-linecap="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
      </nav>
      <div id="mobile-menu" class="hidden border-t border-slate-200 bg-white md:hidden">
        <div class="container-page flex flex-col gap-1 py-3">${links}${authLinks}</div>
      </div>
    </header>`;

  const menuButton = document.querySelector("[data-menu]");
  menuButton.addEventListener("click", () => {
    const menu = document.getElementById("mobile-menu");
    const open = menu.classList.toggle("hidden") === false;
    menuButton.setAttribute("aria-expanded", open);
  });

  document.querySelectorAll("[data-logout]").forEach((button) =>
    button.addEventListener("click", async () => {
      try {
        await api("/accounts/logout/", { method: "POST" });
      } catch {}
      session.clear();
      flash("You have been logged out.", "info");
      location.href = "login.html";
    }),
  );
}

function renderFooter() {
  document.getElementById("app-footer").innerHTML = `
    <footer class="mt-16 border-t border-slate-200 bg-white">
      <div class="container-page flex flex-col items-center justify-between gap-4 py-8 text-sm text-slate-500 sm:flex-row">
        <div class="flex items-center gap-3">
          <img src="assets/logo.png" class="h-8 w-8 object-contain" alt="" />
          <span>Bangladesh Army University of Engineering &amp; Technology</span>
        </div>
        <p>&copy; ${new Date().getFullYear()} BAUET Project &amp; Thesis Archive · Team Extreme</p>
      </div>
    </footer>`;
}

export function initLayout() {
  renderHeader();
  renderFooter();
  showFlash();
}

export function initials(person) {
  const source = person.full_name || person.username || "?";
  return source
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function avatar(person, size = "h-12 w-12") {
  if (person.image) {
    return `<img src="${escapeHtml(person.image)}" alt="" class="${size} shrink-0 rounded-full object-cover ring-2 ring-white" />`;
  }
  return `<span class="${size} flex shrink-0 items-center justify-center rounded-full bg-indigo-100 font-semibold text-indigo-700 ring-2 ring-white">${escapeHtml(initials(person))}</span>`;
}

export function postCard(post, { showStatus = false } = {}) {
  const status = showStatus && !post.is_approved
    ? `<span class="badge badge-warning mt-4 w-fit">Pending approval</span>`
    : "";
  return `
    <article class="card post-card flex flex-col p-6">
      <div class="mb-3 flex items-center justify-between gap-2 text-xs">
        <span class="badge badge-primary truncate">${escapeHtml(post.department_name)}</span>
        <span class="shrink-0 font-medium text-slate-500">${escapeHtml(post.year)}</span>
      </div>
      <h3 class="text-lg font-semibold leading-snug text-slate-900 hover:text-indigo-700">
        <a href="post.html?id=${post.id}">${escapeHtml(post.title)}</a>
      </h3>
      <p class="line-clamp-3 mt-2 flex-1 text-sm text-slate-600">${escapeHtml(post.content)}</p>
      ${status}
      <a href="post.html?id=${post.id}" class="mt-5 inline-flex items-center gap-1 text-sm font-semibold text-indigo-600 hover:text-indigo-500">
        View details
        <svg class="h-4 w-4" fill="none" viewBox="0 0 14 10" aria-hidden="true"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9"/></svg>
      </a>
    </article>`;
}

export function skeletonCards(count = 6) {
  return Array.from({ length: count }, () => `<div class="skeleton h-56"></div>`).join("");
}

export function emptyState(title, message, action = "") {
  return `
    <div class="card col-span-full flex flex-col items-center px-6 py-16 text-center">
      <h3 class="text-lg font-semibold text-slate-900">${escapeHtml(title)}</h3>
      <p class="mt-1 text-sm text-slate-500">${escapeHtml(message)}</p>
      ${action}
    </div>`;
}

export function clearFormErrors(form) {
  form.querySelectorAll(".field-error").forEach((el) => el.remove());
  form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
  form.querySelector("[data-form-error]")?.classList.add("hidden");
}

export function showFormErrors(form, error) {
  const data = error.data && typeof error.data === "object" ? error.data : {};
  const general = [];
  Object.entries(data).forEach(([name, messages]) => {
    const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
    const input = form.elements.namedItem(name);
    if (input && input.closest) {
      input.setAttribute("aria-invalid", "true");
      const p = document.createElement("p");
      p.className = "field-error";
      p.textContent = text;
      input.closest("[data-field]")?.appendChild(p) ?? input.after(p);
    } else {
      general.push(text);
    }
  });
  const box = form.querySelector("[data-form-error]");
  const message = general.join(" ") || (Object.keys(data).length ? "" : error.message);
  if (box && message) {
    box.textContent = message;
    box.classList.remove("hidden");
  }
}

export async function submitWith(button, task) {
  const label = button.textContent;
  button.disabled = true;
  button.textContent = "Please wait...";
  try {
    return await task();
  } finally {
    button.disabled = false;
    button.textContent = label;
  }
}

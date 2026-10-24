import { api } from "../api.js";
import { avatar, emptyState, escapeHtml, flash, initLayout, toast } from "../ui.js";

initLayout();

const root = document.getElementById("post-root");
const id = new URLSearchParams(location.search).get("id");

function personCard(person) {
  const meta = [person.designation || "Member", person.dept].filter(Boolean).join(" · ");
  return `
    <li class="flex items-center gap-4 rounded-xl border border-slate-200 p-4">
      ${avatar(person)}
      <div class="min-w-0">
        <p class="truncate font-semibold text-slate-900">${escapeHtml(person.full_name)}</p>
        <p class="truncate text-xs text-slate-500">${escapeHtml(meta)}</p>
        ${person.email ? `<a href="mailto:${escapeHtml(person.email)}" class="truncate text-xs text-indigo-600 hover:text-indigo-500">${escapeHtml(person.email)}</a>` : ""}
      </div>
    </li>`;
}

function peopleSection(label, people) {
  if (!people.length) return "";
  return `
    <h3 class="mt-6 text-xs font-semibold uppercase tracking-wider text-slate-500">${label}${people.length > 1 ? "s" : ""}</h3>
    <ul class="mt-3 grid gap-3 sm:grid-cols-2">${people.map(personCard).join("")}</ul>`;
}

function render(post) {
  document.title = `${post.title} · BAUET Project & Thesis Archive`;
  const paragraphs = post.content
    .split(/\n{2,}/)
    .map((p) => `<p>${escapeHtml(p).replace(/\n/g, "<br />")}</p>`)
    .join("");

  root.innerHTML = `
    <nav class="text-sm text-slate-500" aria-label="Breadcrumb">
      <a href="index.html" class="hover:text-slate-700">Browse</a>
      <span class="mx-2">/</span>
      <span>${escapeHtml(post.department_name)}</span>
    </nav>
    <div class="mt-6 grid gap-8 lg:grid-cols-[1fr_320px]">
      <article class="space-y-8">
        <header class="card p-6 sm:p-8">
          <div class="flex flex-wrap items-center gap-2 text-xs">
            <span class="badge badge-primary">${escapeHtml(post.department_name)}</span>
            <span class="badge badge-muted">${escapeHtml(post.year)}</span>
            ${post.is_approved ? "" : `<span class="badge badge-warning">Pending approval</span>`}
          </div>
          <h1 class="mt-4 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">${escapeHtml(post.title)}</h1>
          <h2 class="mt-8 text-sm font-semibold uppercase tracking-wider text-slate-500">Abstract</h2>
          <div class="mt-3 space-y-4 leading-relaxed text-slate-700">${paragraphs}</div>
        </header>
        <section class="card p-6 sm:p-8">
          <h2 class="text-lg font-semibold text-slate-900">People</h2>
          ${peopleSection("Supervisor", post.supervisors)}
          ${peopleSection("Author", post.authors)}
        </section>
      </article>
      <aside class="space-y-6 lg:sticky lg:top-24 lg:self-start">
        <div class="card p-6">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">Document</h2>
          ${post.file ? `
            <p class="mt-4 truncate text-sm font-medium text-slate-900" title="${escapeHtml(post.file_name)}">${escapeHtml(post.file_name)}</p>
            <a href="${escapeHtml(post.file)}" class="btn btn-primary mt-5 w-full" download target="_blank" rel="noopener">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" aria-hidden="true"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v12m0 0 4-4m-4 4-4-4M4 20h16"/></svg>
              Download
            </a>` : `<p class="mt-3 text-sm text-slate-500">No file attached.</p>`}
        </div>
        ${post.can_edit ? `
        <div class="card p-6">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">Manage</h2>
          <div class="mt-4 flex gap-3">
            <a href="submit.html?id=${post.id}" class="btn btn-secondary flex-1">Edit</a>
            <button type="button" data-delete class="btn btn-danger flex-1">Delete</button>
          </div>
        </div>` : ""}
      </aside>
    </div>`;

  root.querySelector("[data-delete]")?.addEventListener("click", async (event) => {
    if (!confirm(`Delete “${post.title}”? This can't be undone.`)) return;
    event.target.disabled = true;
    try {
      await api(`/posts/${post.id}/`, { method: "DELETE" });
      flash("Post deleted.");
      location.href = "profile.html";
    } catch (error) {
      event.target.disabled = false;
      toast(error.message, "error");
    }
  });
}

if (!id) {
  root.innerHTML = emptyState("Project not found", "The link you followed is incomplete.");
} else {
  api(`/posts/${encodeURIComponent(id)}/`)
    .then(render)
    .catch((error) => {
      root.innerHTML = error.status === 404
        ? emptyState("Project not found", "It may have been removed or is still awaiting approval.", `<a href="index.html" class="btn btn-primary mt-6">Back to browse</a>`)
        : emptyState("Couldn't load this project", "Make sure the API server is running, then refresh.");
    });
}

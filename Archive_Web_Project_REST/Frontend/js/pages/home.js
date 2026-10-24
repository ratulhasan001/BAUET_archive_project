import { api } from "../api.js";
import { emptyState, escapeHtml, initLayout, postCard, skeletonCards } from "../ui.js";

initLayout();

const params = new URLSearchParams(location.search);
const state = {
  department: params.get("department") || "",
  search: params.get("search") || "",
  page: Number(params.get("page")) || 1,
};

const grid = document.getElementById("post-grid");
const pagination = document.getElementById("pagination");
const summary = document.getElementById("result-summary");
const searchForm = document.getElementById("search-form");
let departments = [];

searchForm.search.value = state.search;

function syncUrl() {
  const query = new URLSearchParams();
  if (state.department) query.set("department", state.department);
  if (state.search) query.set("search", state.search);
  if (state.page > 1) query.set("page", state.page);
  const qs = query.toString();
  history.replaceState(null, "", qs ? `?${qs}` : location.pathname);
}

function renderDepartments() {
  const list = document.getElementById("department-list");
  const item = (slug, name, count) => `
    <button type="button" data-dept="${escapeHtml(slug)}" class="side-link ${state.department === slug ? "active" : ""}">
      <span>${escapeHtml(name)}</span>
      ${count !== undefined ? `<span class="text-xs text-slate-400">${count}</span>` : ""}
    </button>`;
  list.innerHTML = item("", "All departments") + departments.map((d) => item(d.slug, d.name, d.post_count)).join("");
  list.querySelectorAll("[data-dept]").forEach((button) =>
    button.addEventListener("click", () => {
      state.department = button.dataset.dept;
      state.page = 1;
      renderDepartments();
      loadPosts();
    }),
  );
}

function renderHero(count) {
  const dept = departments.find((d) => d.slug === state.department);
  document.getElementById("hero-title").textContent = dept
    ? dept.name
    : "Discover research by BAUET students and faculty";
  document.getElementById("hero-subtitle").textContent = dept
    ? `${count} approved work${count === 1 ? "" : "s"} in this department.`
    : "Browse approved projects and theses across every department.";
}

async function loadPosts() {
  syncUrl();
  grid.innerHTML = skeletonCards();
  pagination.classList.add("hidden");
  try {
    const data = await api("/posts/", {
      query: { department: state.department, search: state.search, page: state.page },
    });
    renderHero(data.count);
    summary.classList.toggle("hidden", !state.search);
    summary.innerHTML = `${data.count} result${data.count === 1 ? "" : "s"} for <span class="font-semibold text-slate-900">“${escapeHtml(state.search)}”</span>`;

    grid.innerHTML = data.results.length
      ? data.results.map((post) => postCard(post)).join("")
      : emptyState(
          "Nothing here yet",
          state.search ? "Try a different keyword." : "No approved work matches this filter.",
          `<a href="submit.html" class="btn btn-primary mt-6">Submit your work</a>`,
        );

    if (data.next || data.previous) {
      pagination.classList.remove("hidden");
      pagination.classList.add("flex");
      pagination.querySelector("[data-page=prev]").disabled = !data.previous;
      pagination.querySelector("[data-page=next]").disabled = !data.next;
      pagination.querySelector("[data-page-label]").textContent = `Page ${state.page} of ${data.total_pages}`;
    }
  } catch (error) {
    if (error.status === 404 && state.page > 1) {
      state.page = 1;
      return loadPosts();
    }
    grid.innerHTML = emptyState("Couldn't load projects", "Make sure the API server is running, then refresh.");
  }
}

pagination.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page]");
  if (!button || button.disabled) return;
  state.page += button.dataset.page === "next" ? 1 : -1;
  loadPosts();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  state.search = searchForm.search.value.trim();
  state.page = 1;
  loadPosts();
});

api("/departments/")
  .then((data) => {
    departments = data;
    renderDepartments();
  })
  .catch(() => {
    document.getElementById("department-list").innerHTML =
      `<p class="px-3 py-2 text-sm text-slate-500">Departments unavailable.</p>`;
  })
  .finally(loadPosts);

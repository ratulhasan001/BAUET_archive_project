import { api, session } from "../api.js";
import {
  avatar,
  clearFormErrors,
  emptyState,
  escapeHtml,
  initLayout,
  postCard,
  requireAuth,
  showFormErrors,
  submitWith,
  toast,
} from "../ui.js";

initLayout();

const card = document.getElementById("profile-card");
const editSection = document.getElementById("edit-section");
const form = document.getElementById("profile-form");
let profile;

function renderProfile() {
  const fullName = [profile.first_name, profile.last_name].filter(Boolean).join(" ") || profile.username;
  const person = { ...profile, full_name: fullName };
  const field = (label, value) => `
    <div>
      <dt class="text-slate-500">${label}</dt>
      <dd class="mt-1 font-medium text-slate-900">${escapeHtml(value || "—")}</dd>
    </div>`;

  card.innerHTML = `
    <div class="h-28 bg-gradient-to-r from-indigo-600 to-slate-900"></div>
    <div class="flex flex-col gap-6 px-6 pb-6 sm:flex-row sm:items-end sm:justify-between">
      <div class="-mt-12 flex flex-col gap-4 sm:flex-row sm:items-end">
        ${avatar(person, "h-24 w-24 text-2xl")}
        <div>
          <h1 class="text-2xl font-bold text-slate-900">${escapeHtml(fullName)}</h1>
          <p class="text-sm text-slate-500">${escapeHtml([profile.designation || "Member", profile.dept].filter(Boolean).join(" · "))}</p>
        </div>
      </div>
      <div class="flex gap-3">
        <button type="button" data-edit class="btn btn-secondary">Edit profile</button>
        <a href="submit.html" class="btn btn-primary">Submit work</a>
      </div>
    </div>
    <dl class="grid gap-4 border-t border-slate-100 px-6 py-5 text-sm sm:grid-cols-3">
      ${field("Email", profile.email)}
      ${field("Phone", profile.contact_number)}
      ${field("Address", profile.address)}
    </dl>`;

  card.querySelector("[data-edit]").addEventListener("click", openEditor);
}

function openEditor() {
  ["first_name", "last_name", "designation", "dept", "contact_number", "address"].forEach((name) => {
    form[name].value = profile[name] ?? "";
  });
  editSection.classList.remove("hidden");
  editSection.scrollIntoView({ behavior: "smooth" });
}

form.querySelector("[data-cancel-edit]").addEventListener("click", () => editSection.classList.add("hidden"));

form.addEventListener("submit", (event) => {
  event.preventDefault();
  clearFormErrors(form);
  const body = new FormData(form);
  if (!form.image.files.length) body.delete("image");

  submitWith(form.querySelector("[type=submit]"), async () => {
    try {
      profile = await api("/accounts/me/", { method: "PATCH", body });
      const user = session.user || {};
      session.save(session.token, {
        ...user,
        full_name: [profile.first_name, profile.last_name].filter(Boolean).join(" ") || profile.username,
        image: profile.image,
      });
      renderProfile();
      editSection.classList.add("hidden");
      form.image.value = "";
      toast("Profile updated.", "success");
    } catch (error) {
      showFormErrors(form, error);
    }
  });
});

async function loadPosts() {
  const container = document.getElementById("my-posts");
  try {
    const data = await api("/posts/", { query: { mine: 1, page_size: 100 } });
    document.getElementById("post-count").textContent = `${data.count} total`;
    container.innerHTML = data.results.length
      ? data.results.map((post) => postCard(post, { showStatus: true })).join("")
      : emptyState(
          "No submissions yet",
          "Your projects and theses will show up here.",
          `<a href="submit.html" class="btn btn-primary mt-6">Submit your first project</a>`,
        );
  } catch {
    container.innerHTML = emptyState("Couldn't load your submissions", "Please refresh the page.");
  }
}

if (requireAuth()) {
  api("/accounts/me/")
    .then((data) => {
      profile = data;
      renderProfile();
    })
    .catch(() => requireAuth());
  loadPosts();
}

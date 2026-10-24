import { api, session } from "../api.js";
import { clearFormErrors, emptyState, escapeHtml, flash, initLayout, requireAuth, showFormErrors, submitWith } from "../ui.js";

initLayout();

const form = document.getElementById("post-form");
const id = new URLSearchParams(location.search).get("id");

async function loadDepartments() {
  const departments = await api("/departments/");
  form.department.insertAdjacentHTML(
    "beforeend",
    departments.map((d) => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join(""),
  );
}

async function loadPost() {
  const post = await api(`/posts/${encodeURIComponent(id)}/`);
  if (!post.can_edit) throw new Error("You can't edit this post.");
  document.title = `Edit ${post.title} · BAUET Project & Thesis Archive`;
  document.getElementById("form-title").textContent = "Edit submission";
  document.getElementById("form-subtitle").textContent = post.title;
  document.getElementById("file-required").classList.add("hidden");
  document.getElementById("cancel-link").href = `post.html?id=${post.id}`;
  form.querySelector("[type=submit]").textContent = "Save changes";

  const currentFile = document.getElementById("current-file");
  currentFile.textContent = `Current file: ${post.file_name}. Leave empty to keep it.`;
  currentFile.classList.remove("hidden");

  form.title.value = post.title;
  form.content.value = post.content;
  form.department.value = post.department;
  form.year.value = post.year;
  const me = session.user || {};
  form.author_emails.value = post.authors.filter((a) => a.id !== me.id).map((a) => a.email).join(", ");
  form.supervisor_emails.value = post.supervisors.map((s) => s.email).join(", ");
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  clearFormErrors(form);
  const body = new FormData(form);
  if (!form.file.files.length) body.delete("file");

  submitWith(form.querySelector("[type=submit]"), async () => {
    try {
      const post = await api(id ? `/posts/${id}/` : "/posts/", { method: id ? "PATCH" : "POST", body });
      flash(id ? "Post updated." : "Submitted! It will appear in the archive once approved.");
      location.href = `post.html?id=${post.id}`;
    } catch (error) {
      showFormErrors(form, error);
      form.querySelector("[aria-invalid=true]")?.focus();
    }
  });
});

if (requireAuth()) {
  form.year.max = new Date().getFullYear() + 1;
  form.year.value = new Date().getFullYear();
  loadDepartments()
    .then(() => id && loadPost())
    .catch((error) => {
      form.outerHTML = emptyState("Can't open this form", error.message);
    });
}

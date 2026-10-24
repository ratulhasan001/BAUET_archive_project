import { api, session } from "../api.js";
import { clearFormErrors, flash, initLayout, showFormErrors, submitWith } from "../ui.js";

if (session.isLoggedIn) location.replace("index.html");

initLayout();

const form = document.getElementById("register-form");
form.addEventListener("submit", (event) => {
  event.preventDefault();
  clearFormErrors(form);
  const body = new FormData(form);
  if (!form.image.files.length) body.delete("image");

  submitWith(form.querySelector("[type=submit]"), async () => {
    try {
      const data = await api("/accounts/register/", { method: "POST", body });
      flash(data.detail);
      location.href = "login.html";
    } catch (error) {
      showFormErrors(form, error);
      form.querySelector("[aria-invalid=true]")?.focus();
    }
  });
});

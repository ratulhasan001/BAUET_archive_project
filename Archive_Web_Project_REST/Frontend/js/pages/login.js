import { api, session } from "../api.js";
import { clearFormErrors, flash, initLayout, showFormErrors, submitWith, toast } from "../ui.js";

const params = new URLSearchParams(location.search);
const next = params.get("next");
const safeNext = next && /^[\w-]+\.html(\?[^/]*)?$/.test(next) ? next : "index.html";

if (session.isLoggedIn) location.replace(safeNext);

initLayout();

if (params.get("activated") === "1") toast("Your account is active. You can log in now.", "success");
if (params.get("activated") === "0") toast("That activation link is invalid or has expired.", "error");

const form = document.getElementById("login-form");
form.addEventListener("submit", (event) => {
  event.preventDefault();
  clearFormErrors(form);
  submitWith(form.querySelector("[type=submit]"), async () => {
    try {
      const data = await api("/accounts/login/", {
        method: "POST",
        body: { username: form.username.value.trim(), password: form.password.value },
      });
      session.save(data.token, data.user);
      flash(`Welcome back, ${data.user.full_name}!`);
      location.href = safeNext;
    } catch (error) {
      showFormErrors(form, error);
    }
  });
});

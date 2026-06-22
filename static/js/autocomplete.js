(function () {
  const input = document.getElementById("q");
  if (!input) return;

  const box = document.getElementById("ac");
  const acUrl = input.dataset.autocompleteUrl;
  const searchUrl = input.dataset.searchUrl;
  let items = [],
    active = -1,
    timer = null;

  function close() {
    box.classList.remove("open");
    box.innerHTML = "";
    items = [];
    active = -1;
  }

  function render(results) {
    if (!results.length) {
      close();
      return;
    }
    box.replaceChildren(
      ...results.map((r) => {
        const el = document.createElement("div");
        el.className = "ac-item";
        el.dataset.slug = r.slug;
        el.textContent = r.label;
        el.addEventListener("click", () => {
          window.location =
            searchUrl + "?slug=" + encodeURIComponent(el.dataset.slug);
        });
        return el;
      }),
    );
    items = Array.from(box.querySelectorAll(".ac-item"));
    box.classList.add("open");
    active = -1;
  }

  input.addEventListener("input", () => {
    const q = input.value.trim();
    clearTimeout(timer);
    if (!q) {
      close();
      return;
    }
    timer = setTimeout(async () => {
      try {
        const res = await fetch(acUrl + "?q=" + encodeURIComponent(q));
        const data = await res.json();
        render(data.results);
      } catch (e) {
        close();
      }
    }, 180);
  });

  input.addEventListener("keydown", (e) => {
    if (!items.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      active = (active + 1) % items.length;
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      active = (active - 1 + items.length) % items.length;
    } else if (e.key === "Enter" && active >= 0) {
      e.preventDefault();
      items[active].click();
      return;
    } else return;
    items.forEach((el, i) => el.classList.toggle("active", i === active));
  });

  document.addEventListener("click", (e) => {
    if (!box.contains(e.target) && e.target !== input) close();
  });
})();

function toggleMyTocSubmenu(el) {
  let submenu = el.parentElement.querySelector(".mytoc-submenu");
  if (submenu.style.display === "block") {
    submenu.style.display = "none";
    el.textContent = "➕";
  } else {
    submenu.style.display = "block";
    el.textContent = "➖";
  }
}

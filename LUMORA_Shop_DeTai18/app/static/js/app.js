document.addEventListener('DOMContentLoaded', () => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const menu = document.querySelector('[data-menu]');
  if (menuToggle && menu) {
    menuToggle.addEventListener('click', e => {
      e.stopPropagation(); const opened=menu.classList.toggle('open');
      menuToggle.setAttribute('aria-expanded', String(opened));
    });
    document.addEventListener('click', e => {
      if (!menu.contains(e.target) && !menuToggle.contains(e.target)) { menu.classList.remove('open'); menuToggle.setAttribute('aria-expanded','false'); }
    });
  }
  const mobileToggle = document.querySelector('[data-mobile-toggle]');
  const mobileNav = document.querySelector('[data-mobile-nav]');
  if (mobileToggle && mobileNav) mobileToggle.addEventListener('click', () => mobileNav.classList.toggle('open'));
  document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit',e => {
    if (!window.confirm(form.dataset.confirm)) e.preventDefault();
  }));
  document.querySelectorAll('button[data-confirm]').forEach(btn => btn.addEventListener('click',e => {
    if (!window.confirm(btn.dataset.confirm)) e.preventDefault();
  }));
});

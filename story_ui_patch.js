/* Lost Ruby - story UI cleanup */
(() => {
  const style = document.createElement('style');
  style.id = 'lr-story-ui-patch';
  style.textContent = `
    .a1-story::before,
    .a1-story:before {
      content: none !important;
      display: none !important;
    }
  `;
  document.head.appendChild(style);
})();

/* Optional, file:// compatible density review images. Molecular defaults are unchanged. */
'use strict';
(function () {
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function reviewNotes(pdb, notes, context = {}) {
    const policy = window.PSI_NOTICES?.entries[pdb];
    if (policy) return policy.cautions.filter(c => (!context.part || !c.parts || c.parts.includes(context.part)) && (!context.protomer || !c.protomers || c.protomers.includes(context.protomer))).map(c => c.text);
    const entry = window.PSI_DENSITY?.entries[pdb];
    if (!entry) return [...notes];
    const updated = entry.reviewed
      ? notes.map(n => n.replace('Local density has not been visually reviewed;', 'A limited local-density screen has been completed;'))
      : [...notes];
    return entry.reviewed ? [...updated, entry.summary] : updated;
  }
  function mount(host, scene) {
    const data = window.PSI_DENSITY, item = data?.scenes[scene.key], entry = data?.entries[scene.pdb];
    if (!host || !item || !entry) return null;
    const details = document.createElement('details');
    details.className = 'more density-options';
    const regionId = 'density-review-' + scene.key;
    details.innerHTML = `<summary>Density views <span class="muted">· optional</span></summary>
      <p class="fine">${esc(entry.summary)}</p>
      <div class="density-choice" role="group" aria-label="Density visualization">
        <button type="button" data-density="sections" aria-pressed="true" aria-controls="${regionId}">Unmasked sections</button>
        <button type="button" data-density="meshes" aria-pressed="false" aria-controls="${regionId}">3D mesh previews</button>
      </div><div class="density-content" id="${regionId}" role="region" aria-label="Local density review figures"></div>
      <p class="fine">${esc(entry.processing)} <a href="${esc(entry.source_url)}">Deposited source</a> · <a href="docs/DENSITY_VISUALIZATION_PILOT.md">Methods and limitations</a></p>`;
    host.appendChild(details);
    const content = details.querySelector('.density-content'), buttons = [...details.querySelectorAll('[data-density]')];
    let mode = 'sections', rendered = null;
    function render() {
      if (!details.open || rendered === mode) return;
      const images = item[mode] || [];
      const note = mode === 'sections' ? entry.sections_note : entry.meshes_note;
      content.innerHTML = `<p class="fine">${esc(note)}</p>${images.length ? '' : `<p class="note" role="status">${esc(item.message || 'This experimental density view is unavailable for this scene.')}</p>`}
        ${item.feature_notes?.length ? `<ul class="fine">${item.feature_notes.map(n => `<li>${esc(n)}</li>`).join('')}</ul>` : ''}
        <div class="density-figures">${images.map((im, imageIndex) =>
        `<figure><a href="${esc(mode === 'meshes' ? 'density.html?scene=' + encodeURIComponent(scene.key) + '&preset=' + imageIndex : im.src)}" target="_blank" rel="noopener"${mode === 'meshes' ? ' aria-label="Open interactive density: ' + esc(scene.pdb + ' protomer ' + scene.protomer + ' ' + im.label) + '"' : ''}><img src="${esc(im.src)}" alt="${esc(scene.pdb + ' protomer ' + scene.protomer + ' ' + im.label)}" decoding="async"></a><figcaption>${esc(im.label)}<br>${esc(im.caption)}${mode === 'meshes' ? '<span class="density-links"><a href="density.html?scene=' + encodeURIComponent(scene.key) + '&preset=' + imageIndex + '" target="_blank" rel="noopener">Inspect in 3D</a> · <a href="' + esc(im.src) + '" target="_blank" rel="noopener">Static PNG</a></span>' : ''}</figcaption></figure>`).join('')}</div>`;
      rendered = mode;
    }
    const onToggle = () => render();
    const handlers = buttons.map(button => {
      const handler = () => {
        mode = button.dataset.density;
        buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
        render();
      };
      button.addEventListener('click', handler);return handler;
    });
    details.addEventListener('toggle', onToggle);
    // No density images are created or fetched until the user opens this panel.
    return { destroy() { details.removeEventListener('toggle', onToggle);buttons.forEach((b,i) => b.removeEventListener('click', handlers[i])); } };
  }
  window.PSIDensity = { mount, reviewNotes };
})();

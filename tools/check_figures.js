// Audit every figure's SVG geometry in a real browser: elements escaping the
// viewBox, and text labels colliding with each other. Diagrams are hand-authored
// with absolute coordinates, so a moved label can silently land on top of
// something — this catches that without reading eleven screenshots.
//
//   agent-browser open <note url>
//   agent-browser eval "$(cat tools/check_figures.js)"
//
// Note: getBBox() reports pre-transform coordinates, so rotated text is skipped
// rather than reported as out of bounds.
(() => {
  const out = [];
  document.querySelectorAll('figure svg').forEach((svg, fi) => {
    const vb = svg.viewBox.baseVal;
    const issues = [];
    const boxes = [];
    svg.querySelectorAll('text,rect,line,path,polyline,circle').forEach(el => {
      if (el.getAttribute("transform")) return;  // getBBox is pre-transform
      let b; try { b = el.getBBox(); } catch (e) { return; }
      if (!b || (!b.width && !b.height)) return;
      const tag = el.tagName;
      const label = tag === 'text' ? (el.textContent || '').trim().slice(0, 28) : tag;
      // out of bounds against the declared viewBox
      const pad = 0.5;
      if (b.x < vb.x - pad || b.y < vb.y - pad ||
          b.x + b.width > vb.x + vb.width + pad ||
          b.y + b.height > vb.y + vb.height + pad) {
        issues.push(`OUT-OF-BOUNDS ${tag} "${label}" box=[${b.x.toFixed(0)},${b.y.toFixed(0)},${(b.x+b.width).toFixed(0)},${(b.y+b.height).toFixed(0)}] vb=[0,0,${vb.width},${vb.height}]`);
      }
      if (tag === 'text') boxes.push({ label, b });
    });
    // text-on-text collisions
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const A = boxes[i].b, B = boxes[j].b;
        const ox = Math.min(A.x+A.width, B.x+B.width) - Math.max(A.x, B.x);
        const oy = Math.min(A.y+A.height, B.y+B.height) - Math.max(A.y, B.y);
        if (ox > 1.5 && oy > 1.5) {
          issues.push(`TEXT-OVERLAP "${boxes[i].label}" x "${boxes[j].label}" (${ox.toFixed(0)}x${oy.toFixed(0)}px)`);
        }
      }
    }
    if (issues.length) out.push(`fig${fi}:\n  ` + issues.join('\n  '));
  });
  return out.length ? out.join('\n') : 'no geometry issues found';
})()

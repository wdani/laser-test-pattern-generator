(() => {
  const app = document.querySelector('.app');
  const moduleTitle = document.getElementById('activeModuleTitle');
  const subnavList = document.getElementById('subnavList');
  const panels = [...document.querySelectorAll('[data-panel]')];
  const contextTitle = document.getElementById('contextTitle');
  const contextList = document.getElementById('contextList');
  const state = {
    activeModule: 'pattern',
    material: 'Cork',
    output: 'Both',
    rows: 7,
    cols: 7,
    stockW: 100,
    stockH: 100,
    margin: 8,
    tile: 8,
    gap: 2,
    designShape: 'rectangle',
    designText: 'Romy',
    designMotif: 'star',
    designTextPosition: 'lower third'
  };
  const $ = (id) => document.getElementById(id);

  const subnavs = {
    pattern: [
      ['Job Setup','job'], ['Stock','stock'], ['Material','material'], ['Grid','grid'], ['Laser','laser'], ['Output','output'], ['Verify','verify']
    ],
    design: [
      ['Design Setup','design_setup'], ['Shape','design_shape'], ['Text & Motif','design_text'], ['Pattern','design_pattern'], ['Output','design_output'], ['Verify','design_verify']
    ],
    journal: [
      ['Result Log','journal_log'], ['Material Runs','journal_runs'], ['Photos','journal_photos'], ['Export','journal_export']
    ],
    tools: [
      ['SVG Detail Checker','tool_svg'], ['Hybrid Planner','tool_hybrid'], ['V-bit Calculator','tool_vbit'], ['Cost Calculator','tool_cost']
    ],
    machine: [
      ['Machine Profiles','machine_profiles'], ['Output Profiles','machine_output'], ['Home Assistant','machine_ha'], ['Maintenance','machine_maintenance']
    ],
    settings: [
      ['App Settings','settings_app'], ['API Status','settings_api'], ['Update Check','settings_update'], ['About','settings_about']
    ]
  };

  const moduleNames = { pattern: 'Laser Test Pattern', design: 'Parametric Design', journal: 'Journal', tools: 'Helpers', machine: 'Machine', settings: 'Settings' };
  const contextCopy = {
    job: ['Decide whether this stays a laser-only test or becomes a repeatable material preset.', 'Manifest snapshot should capture stock, material, S-scale, and preview warnings.', 'Quote risk is low for tests, higher for single personalized pieces.'],
    stock: ['Stock bounds feed preview and SVG fit checks.', 'Safe margin is part of every export snapshot.', 'Origin choice must match the sender workflow.'],
    material: ['Material connects presets, journal runs, and cost estimate.', 'Thickness can influence V-bit and laser recommendations.', 'Journal candidate: Cork fine 7 x 7.'],
    grid: ['Grid footprint is reused by preview and cost timing.', 'Rows and columns are reflected in file-name snapshots.', 'Dense grids need extra label clearance checks.'],
    laser: ['Laser settings are tied to selected output profile.', 'NC S-scale still needs sender verification.', 'Future journal entry can store best cell choices.'],
    output: ['No files are written by this prototype.', 'Both MKS and NC names are shown for planning only.', 'Manifest preview follows output profile choice.'],
    verify: ['Verification stays the final gate before real machine use.', 'Safety checklist is shared across modules.', 'Preview warning state remains visible in the rail.'],
    design_setup: ['This is the second active workflow for comparison.', 'It creates a design preview from parameters, not machine-control output.', 'The same shell pattern should support material tests and simple design jobs.'],
    design_shape: ['Shape and size drive the preview bounds.', 'Circle and rectangle blanks test how well the UI handles different generator inputs.', 'Safe margin is a design constraint, not a machine guarantee.'],
    design_text: ['The name field should feel friendly but still precise.', 'Motif choices show where a future generator could build SVG layers.', 'Text position needs immediate preview feedback.'],
    design_pattern: ['Pattern intent helps compare laser-only and hybrid design flows.', 'Helper tools can advise before real CAM or laser export exists.', 'Safety stays visible even for playful design work.'],
    design_output: ['Returned paths would be authoritative in a future backend.', 'For now the package is a static output plan only.', 'SVG preview is the first target; CNC/laser layers are later work.'],
    design_verify: ['Design generators still need material and output verification.', 'Preview all layers before any future machine export.', 'This concept never writes files or sends jobs.'],
    journal_log: ['Save as material preset if the macro photo confirms the selected cell.', 'Retest if edge smoke repeats above 18% power.', 'Best-cell metadata should link to the settings snapshot.'],
    journal_runs: ['Use approved runs as quick-start presets.', 'Retest flags should reduce material confidence.', 'Batch differences matter before quoting repeat work.'],
    journal_photos: ['Macro photos prove smoke, focus, and edge quality.', 'Failed-job hints should point to speed, power, focus, or air assist.', 'No image files are written in this static concept.'],
    journal_export: ['Export should package markdown, CSV, photos, and JSON later.', 'Settings snapshot belongs next to generated machine files.', 'Static prototype does not write the package.'],
    tool_svg: ['Laser the hairline details instead of forcing a tiny cutter.', 'Mill only the reachable outer pocket and bold border.', 'Use red SVG issues as preflight warnings.'],
    tool_hybrid: ['Mill first, laser second, cut outline last.', 'Keep origin handoff visible so the user knows what must not move.', 'Estimated CNC and laser time should feed the cost calculator.'],
    tool_vbit: ['If computed width is wider than the text stroke, laser the text.', 'Depth and angle should be stored with the manifest.', 'Use V-bit for bold borders, not fragile hairlines.'],
    tool_cost: ['Single-piece quote risk is setup-heavy.', 'Wear, filter, and packaging should be explicit.', 'Final price stays a planning mock here.'],
    machine_profiles: ['Selected machine controls S-scale interpretation.', 'Warn when NC output needs sender verification.', 'Makera 0-1 is selected for the current mock.'],
    machine_output: ['Preview MKS and NC before using either file.', 'MKS and NC can diverge in power scaling.', 'No post-processor writes files here.'],
    machine_ha: ['Check air assist before trusting the run readiness.', 'Not connected states should be obvious to testers.', 'No network calls are made by this concept.'],
    machine_maintenance: ['Lens/filter/tool-wear can change job readiness.', 'Replace worn small cutters before fine hardwood details.', 'Runtime counters are mock values only.'],
    settings_app: ['Default units and export preferences shape new jobs.', 'Settings remain static in this prototype.', 'No persistence is performed.'],
    settings_api: ['JSON API readiness is shown as a design target.', 'Generate remains disabled in this static package.', 'Preview/config shapes are source-of-truth candidates.'],
    settings_update: ['Offline package mode avoids internet dependency.', 'Feedback is returned as markdown from the form.', 'No update check is performed.'],
    settings_about: ['Concept A favors a dedicated desktop-program shell.', 'The stable v1.x Python core remains the comparison baseline.', 'Future UI work should follow the JSON API.']
  };

  function renderContext(view){
    const lines = contextCopy[view] || contextCopy.job;
    const panel = panels.find(p => p.dataset.panel === view);
    if (contextTitle) contextTitle.textContent = panel?.querySelector('h1')?.textContent || 'Job intelligence';
    if (contextList) contextList.innerHTML = lines.map(line => `<li>${line}</li>`).join('');
  }

  function openPanel(view){
    app.dataset.view = view;
    panels.forEach(p => p.classList.toggle('active-panel', p.dataset.panel === view));
    document.querySelectorAll('.sub').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    renderContext(view);
    renderPreview();
  }

  function renderSubnav(module){
    const labels = subnavs[module] || subnavs.pattern;
    state.activeModule = module;
    moduleTitle.textContent = moduleNames[module] || 'Test Pattern';
    subnavList.innerHTML = '';
    labels.forEach(([label, view], index) => {
      const btn = document.createElement('button');
      btn.className = 'sub' + (index === 0 ? ' active' : '');
      btn.textContent = label;
      btn.dataset.view = view;
      btn.addEventListener('click', () => openPanel(btn.dataset.view));
      subnavList.appendChild(btn);
    });
    openPanel(labels[0][1]);
  }

  document.querySelectorAll('.module').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.module').forEach(b => b.classList.toggle('active', b === btn));
      renderSubnav(btn.dataset.module);
    });
  });

  function clamp(n,min,max){ n = Number.parseInt(n,10); return Number.isFinite(n) ? Math.min(Math.max(n,min),max) : min; }
  function slug(v){ return v.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,''); }

  function svgEl(tag, attrs = {}, text = ''){
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text) node.textContent = text;
    return node;
  }

  function starPath(cx, cy, outer, inner){
    const points = [];
    for (let i = 0; i < 10; i++) {
      const angle = -Math.PI / 2 + i * Math.PI / 5;
      const radius = i % 2 === 0 ? outer : inner;
      points.push(`${cx + Math.cos(angle) * radius},${cy + Math.sin(angle) * radius}`);
    }
    return points.join(' ');
  }

  function renderLaserPreview(g){
    const cell = Math.min(22, Math.floor(180 / Math.max(state.rows,state.cols)));
    const gap = Math.max(7, Math.round(cell*.45));
    const w = state.cols*cell + (state.cols-1)*gap;
    const h = state.rows*cell + (state.rows-1)*gap;
    const sx = 210 - w/2, sy = 260 - h/2;
    for(let r=0;r<state.rows;r++){
      for(let c=0;c<state.cols;c++){
        const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');
        rect.setAttribute('class','tile');
        rect.setAttribute('x',sx+c*(cell+gap));
        rect.setAttribute('y',sy+r*(cell+gap));
        rect.setAttribute('width',cell);
        rect.setAttribute('height',cell);
        rect.setAttribute('rx','3');
        g.appendChild(rect);
      }
    }
  }

  function renderDesignPreview(g){
    const isCircle = state.designShape === 'circle';
    const textY = state.designTextPosition === 'top' ? 188 : state.designTextPosition === 'center' ? 262 : 330;
    const shapeAttrs = isCircle
      ? { cx: 210, cy: 260, r: 126, class: 'design-shape' }
      : { x: 74, y: 164, width: 272, height: 190, rx: 20, class: 'design-shape' };
    g.appendChild(svgEl(isCircle ? 'circle' : 'rect', shapeAttrs));
    g.appendChild(svgEl('rect', { x: 92, y: 182, width: 236, height: 154, rx: 14, class: 'design-safe' }));

    if (state.designMotif === 'star') {
      g.appendChild(svgEl('polygon', { points: starPath(210, 218, 38, 16), class: 'design-motif' }));
    } else if (state.designMotif === 'stripes') {
      for (let x = 118; x <= 300; x += 28) {
        g.appendChild(svgEl('line', { x1: x, y1: 196, x2: x + 36, y2: 324, class: 'design-motif-line' }));
      }
    } else if (state.designMotif === 'radial pattern') {
      for (let i = 0; i < 16; i++) {
        const angle = i * Math.PI / 8;
        g.appendChild(svgEl('line', {
          x1: 210,
          y1: 260,
          x2: 210 + Math.cos(angle) * 88,
          y2: 260 + Math.sin(angle) * 88,
          class: 'design-motif-line'
        }));
      }
    } else {
      for (let i = -2; i < 7; i++) {
        g.appendChild(svgEl('line', { x1: 96 + i * 36, y1: 336, x2: 180 + i * 36, y2: 184, class: 'design-gradient-line' }));
      }
    }

    g.appendChild(svgEl('text', { x: 210, y: textY, class: 'design-text', 'text-anchor': 'middle' }, state.designText || 'Romy'));
  }

  function renderPreview(){
    const g = $('previewGrid'); if(!g) return; g.innerHTML='';
    const previewStatus = $('previewStatus');
    if (state.activeModule === 'design' || app.dataset.view.startsWith('design_')) {
      if (previewStatus) previewStatus.textContent = 'design draft';
      renderDesignPreview(g);
      return;
    }
    if (previewStatus) previewStatus.textContent = 'preview required';
    renderLaserPreview(g);
  }

  function render(){
    const mat = state.material;
    $('readyMaterial').textContent = mat;
    $('readyStock').textContent = `${state.stockW} x ${state.stockH} mm`;
    $('fileMks').textContent = `${slug(mat)}_material_test.mks`;
    $('fileNc').textContent = `${slug(mat)}_material_test.nc`;
    $('fileMks').classList.toggle('dim', state.output === 'NC');
    $('fileNc').classList.toggle('dim', state.output === 'MKS');
    renderPreview();
  }

  $('material')?.addEventListener('change', e => { state.material = e.target.value; render(); });
  [['stockW','stockW'],['stockH','stockH'],['margin','margin'],['rows','rows'],['cols','cols'],['tile','tile'],['gap','gap']].forEach(([id,key]) => {
    $(id)?.addEventListener('input', e => { state[key] = clamp(e.target.value, key === 'rows' || key === 'cols' ? 1 : 0, key === 'rows' || key === 'cols' ? 12 : 500); render(); });
  });
  $('designShape')?.addEventListener('change', e => { state.designShape = e.target.value; renderPreview(); });
  $('designText')?.addEventListener('input', e => { state.designText = e.target.value; renderPreview(); });
  $('designTextPosition')?.addEventListener('change', e => { state.designTextPosition = e.target.value; renderPreview(); });
  $('designMotif')?.addEventListener('change', e => { state.designMotif = e.target.value; renderPreview(); });
  document.querySelectorAll('#outputChoice button').forEach(btn => btn.addEventListener('click', () => {
    state.output = btn.dataset.output;
    document.querySelectorAll('#outputChoice button').forEach(b => b.classList.toggle('selected', b === btn));
    render();
  }));
  $('generateMock')?.addEventListener('click', () => { $('generateMsg').textContent = 'Static prototype only: generation is intentionally inactive.'; });
  $('motionToggle')?.addEventListener('click', () => {
    document.body.classList.toggle('reduce-motion');
    $('motionToggle').textContent = document.body.classList.contains('reduce-motion') ? 'Motion off' : 'Motion on';
  });
  renderSubnav('pattern');
  render();
})();

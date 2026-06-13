(() => {
  const views = [...document.querySelectorAll('.view')];
  const navButtons = [...document.querySelectorAll('.global-nav button')];
  const jobButtons = [...document.querySelectorAll('.queue-job')];
  const outputButtons = [...document.querySelectorAll('.format-tabs button')];
  const tiles = document.getElementById('tiles');
  const state = { job: 'laserPattern', output: 'Both' };

  const jobs = {
    laserPattern: {
      kicker: 'Material settings job',
      title: 'Laser Test Pattern',
      summary: 'Find reliable laser settings for cork and save the best result as material memory.',
      goal: 'Create a 7 x 7 cork test grid with clear output and preflight state.',
      railIdea: 'Laser Test Pattern',
      railWhy: 'This is a concrete job: find usable material settings, not just open a module.',
      railTools: 'Uses: Material Journal, Output Profile, Cost Calculator, Preflight.',
      preview: 'Laser Test Pattern preview',
      status: 'margin low',
      fileBase: 'laser_test_pattern_cork',
      brief: [['Material', 'Cork 3 mm'], ['Stock', '100 x 100 mm'], ['Machine', 'Makera laser profile'], ['Purpose', 'Material library']],
      settingsLabel: 'Laser Test Pattern settings',
      settings: [['Material', 'Cork'], ['Preset', 'Cork fine 7 x 7'], ['Stock', '100 x 100 mm'], ['Margin', '8 mm'], ['Grid', '7 x 7'], ['Tile / gap', '8 mm / 2 mm'], ['Speed range', '2200-4000 mm/min'], ['Power range', '5-20 %'], ['Mode', 'Offset Fill'], ['Output', 'MKS + NC']],
      plan: ['Choose material and stock size.', 'Generate labeled power/speed grid.', 'Preview MKS and NC output names.', 'Run only after preflight, then save the best cell.'],
      tools: ['Material Journal', 'Cost Calculator', 'Output Profile', 'Preflight Checklist'],
      readiness: [['Material', 'safe'], ['Output', 'previewed'], ['Air assist', 'review'], ['Journal', 'candidate']],
      memory: [['Settings hash', 'LTG-7F42-CORK-MKS'], ['Last result', '3000 mm/min at 12%'], ['Next action', 'macro photo before preset']],
      warnings: ['Air assist is not confirmed.', 'NC S-scale must be checked before use.', 'Macro photo missing before preset promotion.']
    },
    nameplate: {
      kicker: 'Parametric generator job',
      title: 'Parametric Design Generator',
      summary: 'Create a simple nameplate or pattern design from shape, size, text, motif, operation intent, and output target parameters.',
      goal: 'Generate a simple Romy nameplate preview from parameters.',
      railIdea: 'Parametric Nameplate',
      railWhy: 'A job for quick personalized parts that do not need a full CAD/CAM workflow.',
      railTools: 'Uses: Pattern Generator, SVG Preview, V-bit Calculator, Cost Calculator.',
      preview: 'Nameplate generator preview',
      status: 'parameter draft',
      fileBase: 'romy_star_nameplate',
      brief: [['Material', 'Basswood 2 mm'], ['Blank', '100 x 100 mm'], ['Text', 'Romy'], ['Symbol', 'Star']],
      settingsLabel: 'Parametric design settings',
      settings: [['Workpiece shape', 'rectangle / circle'], ['Width / height', '120 x 55 mm'], ['Diameter', '80 mm option'], ['Thickness', '3 mm'], ['Name text', 'Romy'], ['Text position', 'lower third'], ['Motif / pattern', 'star, stripes, radial, diagonal'], ['Operation intent', 'laser only or CNC outline + laser detail'], ['Output target', 'SVG preview, future layers'], ['Machine output', 'not generated yet']],
      plan: ['Set shape, size, and material thickness.', 'Place the name and motif from parameters.', 'Preview text fit, safe margin, and pattern readability.', 'Keep output as SVG preview/future layers until real backend support exists.'],
      tools: ['Parametric Pattern Generator', 'Text Fit Check', 'SVG Preview', 'Preflight Checklist'],
      readiness: [['Text fit', 'ok'], ['Motif', 'star'], ['SVG preview', 'ready'], ['Machine files', 'not real yet']],
      memory: [['Design hash', 'PAR-STAR-ROMY'], ['Reusable template', 'nameplate 120 x 55'], ['Next action', 'compare rectangle and circle blanks']],
      warnings: ['Generated design preview is not machine-control output.', 'Future CNC/laser layers must be previewed before use.', 'Text should remain readable at final scale.']
    },
    hybridCoaster: {
      kicker: 'Hybrid making job',
      title: 'Hybrid Coaster',
      summary: 'Plan a coaster where the pocket and border are milled, then fine animal details and name are lasered.',
      goal: 'Split one coaster idea into CNC, laser, and handoff steps.',
      railIdea: 'Hybrid Coaster',
      railWhy: 'A concrete project job: decide what gets milled, what gets lasered, and in which order.',
      railTools: 'Uses: SVG Detail Checker, V-bit Calculator, Cost Calculator, Preflight.',
      preview: 'Hybrid Coaster preview',
      status: 'hybrid review',
      fileBase: 'hybrid_coaster_horse',
      brief: [['Material', 'Cork or wood 6 mm'], ['Diameter', '90 mm'], ['Motif', 'Horse + name'], ['Machine', 'CNC + laser']],
      settingsLabel: 'Hybrid project settings',
      settings: [['Outer shape', '90 mm coaster'], ['CNC operation', '2 mm shallow pocket'], ['Cutter', '3.175 mm endmill'], ['V-bit option', '60 deg for bold border'], ['Laser detail', 'eye, mane, name'], ['Order', 'mill, clean, laser, cut'], ['Origin handoff', 'front-left pin'], ['Estimated time', '34 min']],
      plan: ['Check motif details before choosing cutter.', 'Mill the shallow pocket and bold border.', 'Vacuum chips and keep origin reference.', 'Laser fine details, then cut outline last.'],
      tools: ['SVG Detail Checker', 'V-bit Calculator', 'Operation Sequencer', 'Cost Calculator'],
      readiness: [['SVG detail', 'review'], ['Origin', 'handoff'], ['Tool wear', 'ok'], ['Safety', 'review']],
      memory: [['Project hash', 'HYB-COASTER-HORSE'], ['Known issue', 'fine eye detail'], ['Next action', 'laser small details']],
      warnings: ['Do not mill hairline mane or eye detail.', 'Keep origin reference during handoff.', 'Cut the outside contour last so the part does not shift.']
    },
    failedJob: {
      kicker: 'Diagnosis job',
      title: 'Failed Job Analysis',
      summary: 'Turn a bad result into a practical next attempt: less burn, clearer text, better focus, or safer workholding.',
      goal: 'Explain why a result failed and propose the next test settings.',
      railIdea: 'Failed Job Analysis',
      railWhy: 'A workshop job for learning from mistakes instead of guessing new settings.',
      railTools: 'Uses: Material Journal, Symptom Checklist, Photo Notes, Preflight.',
      preview: 'Failed job notes preview',
      status: 'diagnose',
      fileBase: 'failed_job_analysis_cork',
      brief: [['Symptom', 'burned edges'], ['Material', 'Cork 3 mm'], ['Previous run', '18% power'], ['Goal', 'cleaner mark']],
      settingsLabel: 'Failure diagnosis inputs',
      settings: [['Symptom', 'burned / too dark'], ['Likely cause', 'too much power'], ['Secondary cause', 'air assist unknown'], ['Suggested speed', '+15 %'], ['Suggested power', '-3 to -5 %'], ['Photo evidence', 'macro needed'], ['Retest area', 'small offcut'], ['Journal action', 'mark previous as failed']],
      plan: ['Record symptom and previous settings.', 'Compare with material journal candidates.', 'Suggest one small retest change.', 'Save failed and retest notes together.'],
      tools: ['Failed-job Checklist', 'Material Journal', 'Photo Notes', 'Cost Risk'],
      readiness: [['Photo', 'missing'], ['Retest', 'small'], ['Safety', 'ok'], ['Confidence', 'medium']],
      memory: [['Failure hash', 'FAIL-CORK-18P'], ['Next result', 'pending'], ['Next action', 'reduce power first']],
      warnings: ['Do not change speed, power, and focus all at once.', 'Use a small offcut before rerunning the full job.', 'Unknown plastics must never be laser-tested.']
    },
    bugreport: {
      kicker: 'Support package job',
      title: 'Bugreport Package',
      summary: 'Collect the details needed to report a Makera Studio or output issue clearly during beta testing.',
      goal: 'Create a clean report package with version, machine, files, screenshots, and reproduction steps.',
      railIdea: 'Bugreport Package',
      railWhy: 'A job for beta/support work that normal CAM tools do not structure well.',
      railTools: 'Uses: Manifest Snapshot, Screenshot Notes, Output Profile, Repro Steps.',
      preview: 'Bugreport package preview',
      status: 'package draft',
      fileBase: 'makera_bugreport_package',
      brief: [['Issue', 'NC preview mismatch'], ['Machine', 'Makera profile'], ['App version', 'beta note'], ['Output', 'MKS + NC']],
      settingsLabel: 'Bugreport fields',
      settings: [['Title', 'NC S-scale mismatch'], ['Expected', 'same visual power map'], ['Actual', 'NC preview differs'], ['Files', '.mks, .nc, manifest'], ['Screenshots', 'preview + sender'], ['Steps', '4 reproduction steps'], ['Safety note', 'no machine run needed'], ['Export', 'Discord/GitHub text']],
      plan: ['Collect app and machine version.', 'Attach output names and settings snapshot.', 'Write expected versus actual behavior.', 'Export a readable report text mock.'],
      tools: ['Manifest Snapshot', 'Output Profile', 'Screenshot Notes', 'Report Formatter'],
      readiness: [['Files', 'listed'], ['Screenshots', 'needed'], ['Steps', 'draft'], ['Privacy', 'local']],
      memory: [['Report hash', 'BUG-NC-SCALE'], ['Package state', 'draft'], ['Next action', 'add screenshot']],
      warnings: ['Do not include private paths unless the user chooses to.', 'This prototype does not send anything.', 'Report text should be reviewed before sending.']
    }
  };

  const el = (id) => document.getElementById(id);
  const html = (items, map) => items.map(map).join('');
  const svgEl = (tag, attrs = {}, text = '') => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text) node.textContent = text;
    return node;
  };

  function openView(name) {
    views.forEach(view => view.classList.toggle('active', view.dataset.panel === name));
    navButtons.forEach(button => button.classList.toggle('active', button.dataset.view === name));
  }

  function starPoints(cx, cy, outer, inner) {
    const points = [];
    for (let i = 0; i < 10; i++) {
      const angle = -Math.PI / 2 + i * Math.PI / 5;
      const radius = i % 2 === 0 ? outer : inner;
      points.push(`${cx + Math.cos(angle) * radius},${cy + Math.sin(angle) * radius}`);
    }
    return points.join(' ');
  }

  function renderLaserTiles() {
    if (!tiles) return;
    const rows = 7, cols = 7, cell = 18, gap = 12, startX = 132, startY = 128;
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('class', 'tileRect');
        rect.setAttribute('x', startX + col * (cell + gap));
        rect.setAttribute('y', startY + row * (cell + gap));
        rect.setAttribute('width', cell);
        rect.setAttribute('height', cell);
        rect.setAttribute('rx', '3');
        tiles.appendChild(rect);
      }
    }
  }

  function renderNameplatePreview() {
    if (!tiles) return;
    tiles.appendChild(svgEl('rect', { x: 84, y: 150, width: 252, height: 128, rx: 20, class: 'nameplate-blank' }));
    tiles.appendChild(svgEl('rect', { x: 104, y: 170, width: 212, height: 88, rx: 14, class: 'nameplate-safe' }));
    tiles.appendChild(svgEl('polygon', { points: starPoints(210, 194, 32, 14), class: 'nameplate-motif' }));
    for (let i = 0; i < 6; i++) {
      tiles.appendChild(svgEl('line', { x1: 112 + i * 38, y1: 264, x2: 148 + i * 38, y2: 174, class: 'nameplate-pattern' }));
    }
    tiles.appendChild(svgEl('text', { x: 210, y: 242, class: 'nameplate-text', 'text-anchor': 'middle' }, 'Romy'));
  }

  function renderHelperPreview() {
    if (!tiles) return;
    tiles.appendChild(svgEl('circle', { cx: 210, cy: 210, r: 94, class: 'helper-preview-shape' }));
    tiles.appendChild(svgEl('path', { d: 'M142 226 C166 148 220 150 248 212 S294 264 318 190', class: 'helper-preview-line' }));
    tiles.appendChild(svgEl('text', { x: 210, y: 330, class: 'helper-preview-text', 'text-anchor': 'middle' }, 'helper view'));
  }

  function renderJobPreview() {
    if (!tiles) return;
    tiles.innerHTML = '';
    if (state.job === 'nameplate') {
      renderNameplatePreview();
    } else if (state.job === 'laserPattern') {
      renderLaserTiles();
    } else {
      renderHelperPreview();
    }
  }

  function renderOutput(job) {
    if (state.job === 'nameplate') {
      el('mks').textContent = `${job.fileBase}.svg`;
      el('nc').textContent = `${job.fileBase}_future_layers.json`;
      el('mks').classList.remove('dim');
      el('nc').classList.remove('dim');
      return;
    }
    el('mks').textContent = `${job.fileBase}.mks`;
    el('nc').textContent = `${job.fileBase}.nc`;
    el('mks').classList.toggle('dim', state.output === 'NC');
    el('nc').classList.toggle('dim', state.output === 'MKS');
  }

  function renderJob() {
    const job = jobs[state.job] || jobs.laserPattern;
    jobButtons.forEach(button => button.classList.toggle('active', button.dataset.job === state.job));
    el('railJobIdea').textContent = job.railIdea;
    el('railJobWhy').textContent = job.railWhy;
    el('railJobTools').textContent = job.railTools;
    el('jobKicker').textContent = job.kicker;
    el('jobTitle').textContent = job.title;
    el('jobSummary').textContent = job.summary;
    el('jobGoal').textContent = job.goal;
    el('settingsLabel').textContent = job.settingsLabel;
    el('previewTitle').textContent = job.preview;
    el('bounds').textContent = job.status;
    el('briefFacts').innerHTML = html(job.brief, ([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`);
    el('settingsGrid').innerHTML = html(job.settings, ([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`);
    el('jobPlan').innerHTML = html(job.plan, item => `<li>${item}</li>`);
    el('jobTools').innerHTML = html(job.tools, item => `<span>${item}</span>`);
    el('readinessGrid').innerHTML = html(job.readiness, ([label, value]) => `<span><b>${label}</b><strong>${value}</strong></span>`);
    el('memoryGrid').innerHTML = html(job.memory, ([label, value]) => `<div><b>${label}</b><strong>${value}</strong></div>`);
    el('warningList').innerHTML = html(job.warnings, item => `<li>${item}</li>`);
    renderOutput(job);
    renderJobPreview();
  }

  navButtons.forEach(button => button.addEventListener('click', () => openView(button.dataset.view)));
  jobButtons.forEach(button => button.addEventListener('click', () => {
    state.job = button.dataset.job;
    renderJob();
    openView('job');
  }));
  outputButtons.forEach(button => button.addEventListener('click', () => {
    state.output = button.dataset.output;
    outputButtons.forEach(item => item.classList.toggle('active', item === button));
    renderOutput(jobs[state.job] || jobs.laserPattern);
  }));
  el('mockGenerate')?.addEventListener('click', () => {
    el('mockMessage').textContent = 'Static prototype only: no files are generated or sent.';
  });

  renderJob();
})();

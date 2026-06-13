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
  let activeLanguage = 'en';

  const translations = {
    en: {
      localBadge: 'Local in browser',
      motionOff: 'Motion off',
      motionOn: 'Motion on'
    },
    de: {
      localBadge: 'Lokal im Browser',
      motionOff: 'Bewegung aus',
      motionOn: 'Bewegung an'
    }
  };

  const languageCopy = {
    en: {
      moduleNames: { pattern: 'Laser Test Pattern', design: 'Parametric Design', journal: 'Journal', tools: 'Helpers', machine: 'Machine', settings: 'Settings' },
      previewRequired: 'preview required',
      designDraft: 'design draft',
      generateDisabled: 'Static prototype only: generation is intentionally inactive.',
      designPositions: { 'lower third': 'lower third', center: 'center', top: 'top' }
    },
    de: {
      moduleNames: { pattern: 'Laser-Testmuster', design: 'Parametrisches Design', journal: 'Journal', tools: 'Helfer', machine: 'Maschine', settings: 'Einstellungen' },
      previewRequired: 'Vorschau erforderlich',
      designDraft: 'Design-Entwurf',
      generateDisabled: 'Statischer Prototyp: Erzeugung ist absichtlich deaktiviert.',
      designPositions: { 'lower third': 'unteres Drittel', center: 'Mitte', top: 'oben' }
    }
  };

  const subnavLabels = {
    de: {
      'Job Setup': 'Job einrichten',
      Stock: 'Werkst\u00fcck',
      Material: 'Material',
      Grid: 'Raster',
      Laser: 'Laser',
      Output: 'Ausgabe',
      Verify: 'Pr\u00fcfen',
      'Design Setup': 'Design einrichten',
      Shape: 'Form',
      'Text & Motif': 'Text & Motiv',
      Pattern: 'Muster',
      'Result Log': 'Ergebnislog',
      'Material Runs': 'Materialtests',
      Photos: 'Fotos',
      Export: 'Export',
      'SVG Detail Checker': 'SVG-Detailpr\u00fcfung',
      'Hybrid Planner': 'Hybrid-Planer',
      'V-bit Calculator': 'V-Bit-Rechner',
      'Cost Calculator': 'Kostenrechner',
      'Machine Profiles': 'Maschinenprofile',
      'Output Profiles': 'Ausgabeprofile',
      'Home Assistant': 'Home Assistant',
      Maintenance: 'Wartung',
      'App Settings': 'App-Einstellungen',
      'API Status': 'API-Status',
      'Update Check': 'Update-Pr\u00fcfung',
      About: '\u00dcber'
    }
  };

  const staticTextDe = {
    'v2 program shell - stable v1.x backend mock': 'v2 Program Shell - stabiler v1.x Backend-Mock',
    'Laser Test Pattern': 'Laser-Testmuster',
    'Parametric Design': 'Parametrisches Design',
    'Journal': 'Journal',
    'Helpers': 'Helfer',
    'Machine': 'Maschine',
    'Settings': 'Einstellungen',
    'Active module': 'Aktives Modul',
    'Test Pattern': 'Testmuster',
    'Mock modules show local static data only.': 'Mock-Module zeigen nur lokale statische Daten.',
    'Preview': 'Vorschau',
    'required': 'erforderlich',
    'Material': 'Material',
    'Stock': 'Werkst\u00fcck',
    'S profile': 'S-Profil',
    'check NC': 'NC pr\u00fcfen',
    'Generation': 'Erzeugung',
    'mock only': 'nur Mock',
    'Current Job': 'Aktueller Job',
    'The job is the shared object for future modules: pattern generation, journal, archive, costing, and safety.': 'Der Job ist das gemeinsame Objekt f\u00fcr sp\u00e4tere Module: Mustererzeugung, Journal, Archiv, Kosten und Sicherheit.',
    'Job name': 'Jobname',
    'Job type': 'Jobtyp',
    'Laser material test': 'Laser-Materialtest',
    'Parametric nameplate': 'Parametrisches Namensschild',
    'Hybrid CNC/Laser': 'Hybrid CNC/Laser',
    'SVG feasibility check': 'SVG-Machbarkeitspr\u00fcfung',
    'Status': 'Status',
    'Draft / needs preview': 'Entwurf / braucht Vorschau',
    'Ready after verification': 'Bereit nach Pr\u00fcfung',
    'Active workflow': 'Aktiver Workflow',
    'Current material-test generator': 'Aktueller Materialtest-Generator',
    'Nameplate/pattern generator concept': 'Namensschild-/Muster-Generator-Konzept',
    'Helper surface': 'Helferfl\u00e4che',
    'Material Journal': 'Material-Journal',
    'Best settings, photos, repeatability': 'Beste Einstellungen, Fotos, Wiederholbarkeit',
    'Cost + Manifest': 'Kosten + Manifest',
    'Quote risk and settings snapshot': 'Angebotsrisiko und Einstellungs-Snapshot',
    'Stock / Workpiece': 'Werkst\u00fcck / Rohling',
    'Set physical stock dimensions before grid and output decisions.': 'Physische Werkst\u00fcckma\u00dfe vor Raster- und Ausgabeentscheidungen festlegen.',
    'Width': 'Breite',
    'Height': 'H\u00f6he',
    'Safe margin': 'Sicherer Rand',
    'Origin': 'Nullpunkt',
    'Stock bounds and margin are preview-only in this prototype. Real files must still be verified.': 'Werkst\u00fcckgrenzen und Rand sind in diesem Prototyp nur Vorschauwerte. Echte Dateien m\u00fcssen weiterhin gepr\u00fcft werden.',
    'Material & Preset': 'Material & Preset',
    'Material choices should later connect to presets, journal results, and cost estimates.': 'Materialauswahl soll sp\u00e4ter Presets, Journal-Ergebnisse und Kostensch\u00e4tzungen verbinden.',
    'Preset': 'Preset',
    'Thickness': 'Dicke',
    'Journal link': 'Journal-Link',
    'not logged yet': 'noch nicht geloggt',
    'Test Grid': 'Testraster',
    'Speed/power combinations, spacing, labels, and layout footprint.': 'Geschwindigkeit/Leistung, Abstand, Labels und Layout-Fl\u00e4che.',
    'Rows': 'Zeilen',
    'Columns': 'Spalten',
    'Tile size': 'Kachelgr\u00f6\u00dfe',
    'Gap': 'Abstand',
    'Laser Settings': 'Laser-Einstellungen',
    'Mode, speed, power, and machine output profile.': 'Modus, Geschwindigkeit, Leistung und Maschinenausgabeprofil.',
    'Mode': 'Modus',
    'Speed min': 'Geschwindigkeit min',
    'Speed max': 'Geschwindigkeit max',
    'Power range': 'Leistungsbereich',
    'Output': 'Ausgabe',
    'Select planned output. The static prototype never writes files.': 'Geplante Ausgabe ausw\u00e4hlen. Der statische Prototyp schreibt keine Dateien.',
    'Generate disabled \u00b7 static prototype': 'Erzeugung deaktiviert - statischer Prototyp',
    'No files are created in this concept.': 'In diesem Konzept werden keine Dateien erzeugt.',
    'Preview & Verify': 'Vorschau & Pr\u00fcfung',
    'Global safety and file verification before any real machine use.': 'Globale Sicherheits- und Dateipr\u00fcfung vor jeder echten Maschinennutzung.',
    'Preview MKS/NC in Makera Studio or your sender/viewer.': 'MKS/NC in Makera Studio oder deinem Sender/Viewer pr\u00fcfen.',
    'Check NC S scale/profile before running GRBL-style output.': 'NC-S-Skala/Profil vor GRBL-artiger Ausgabe pr\u00fcfen.',
    'Verify stock origin, bounds, focus, air assist, and extraction.': 'Nullpunkt, Grenzen, Fokus, Air Assist und Absaugung pr\u00fcfen.',
    'Avoid unsafe or unknown laser materials.': 'Unsichere oder unbekannte Lasermaterialien vermeiden.',
    'Parametric Design Generator': 'Parametrischer Design Generator',
    'Create a simple CNC/laser-ready design preview from parameters. This prototype does not create real files.': 'Erzeugt eine einfache CNC-/Laser-Designvorschau aus Parametern. Dieser Prototyp erstellt keine echten Dateien.',
    'Design name': 'Designname',
    'Operation intent': 'Bearbeitungsziel',
    'laser only': 'nur Laser',
    'CNC outline + laser detail': 'CNC-Kontur + Laser-Detail',
    'hybrid placeholder': 'Hybrid-Platzhalter',
    'Output target': 'Ausgabeziel',
    'SVG preview': 'SVG-Vorschau',
    'future CNC/laser layers': 'sp\u00e4tere CNC-/Laser-Ebenen',
    'not real machine output yet': 'noch keine echte Maschinenausgabe',
    'Parametric Nameplate': 'Parametrisches Namensschild',
    'Shape, name, motif, preview': 'Form, Name, Motiv, Vorschau',
    'Helper': 'Helfer',
    'Text Fit Check': 'Text-Fit-Pr\u00fcfung',
    'Keep the name readable at size': 'Name in Zielgr\u00f6\u00dfe lesbar halten',
    'Layer Plan': 'Ebenenplan',
    'Separate cut, score, and laser detail': 'Schnitt, Markierung und Laser-Detail trennen',
    'Safety': 'Sicherheit',
    'Verify before export': 'Vor Export pr\u00fcfen',
    'No direct machine output in concept': 'Keine direkte Maschinenausgabe im Konzept',
    'Workpiece Shape': 'Werkst\u00fcckform',
    'Choose a simple blank shape and size before placing text or motifs.': 'Einfache Rohlingform und Gr\u00f6\u00dfe w\u00e4hlen, bevor Text oder Motiv platziert werden.',
    'Shape': 'Form',
    'Diameter': 'Durchmesser',
    'Text & Motif': 'Text & Motiv',
    'Position a name and a simple motif without requiring a full CAD workflow.': 'Name und einfaches Motiv platzieren, ohne einen kompletten CAD-Workflow zu brauchen.',
    'Name text': 'Namenstext',
    'Text position': 'Textposition',
    'Motif': 'Motiv',
    'Motif position': 'Motivposition',
    'top center': 'oben mittig',
    'left side': 'linke Seite',
    'background': 'Hintergrund',
    'Text and motif output are design-preview placeholders only. Real CAM/layer generation is future work.': 'Text- und Motiv-Ausgabe sind nur Designvorschau-Platzhalter. Echte CAM-/Ebenenerzeugung ist sp\u00e4tere Arbeit.',
    'Pattern Intent': 'Musterabsicht',
    'Explore decorative pattern ideas before deciding whether the result belongs to laser, CNC, or hybrid output.': 'Dekorative Musterideen testen, bevor Laser-, CNC- oder Hybrid-Ausgabe entschieden wird.',
    'SVG preview first': 'Zuerst SVG-Vorschau',
    'future layer split': 'sp\u00e4tere Ebenentrennung',
    'no machine output': 'keine Maschinenausgabe',
    'verify material safety': 'Materialsicherheit pr\u00fcfen',
    'Laser only': 'Nur Laser',
    'engraved name + motif': 'gravierter Name + Motiv',
    'Useful for fast personalization on known laser-safe material.': 'N\u00fctzlich f\u00fcr schnelle Personalisierung auf bekannt lasersicherem Material.',
    'CNC outline + laser detail': 'CNC-Kontur + Laser-Detail',
    'Future flow could cut a clean border and laser the name/motif after preview.': 'Ein sp\u00e4terer Flow k\u00f6nnte einen sauberen Rand schneiden und Name/Motiv nach Vorschau lasern.',
    'Design Output Package': 'Design-Ausgabepaket',
    'Plan what the future generator might produce while keeping this concept static.': 'Planen, was der sp\u00e4tere Generator erzeugen k\u00f6nnte, w\u00e4hrend dieses Konzept statisch bleibt.',
    'Design Verify': 'Design pr\u00fcfen',
    'Keep safety and output review visible even for a friendly design generator.': 'Sicherheit und Ausgabekontrolle auch bei einem einfachen Design-Generator sichtbar halten.',
    'Modern Preview': 'Moderne Vorschau',
    'Fit': 'Einpassen',
    'Zoom': 'Zoom',
    'Center': 'Zentrieren',
    'Grid': 'Raster',
    'Labels': 'Labels',
    'Bounds': 'Grenzen',
    'Travel': 'Fahrweg',
    'Front warnings': 'Wichtige Hinweise',
    'Verify generated files before machine use. This prototype has no machine control and no file output.': 'Erzeugte Dateien vor Maschinennutzung pr\u00fcfen. Dieser Prototyp hat keine Maschinensteuerung und keine Dateiausgabe.',
    'Job intelligence': 'Job-Kontext',
    'Decide whether this stays a laser-only test or becomes a repeatable material preset.': 'Entscheiden, ob dies ein reiner Lasertest bleibt oder ein wiederholbares Material-Preset wird.',
    'Manifest snapshot should capture stock, material, S-scale, and preview warnings.': 'Der Manifest-Snapshot sollte Werkst\u00fcck, Material, S-Skala und Vorschauwarnungen erfassen.',
    'Quote risk is low for tests, higher for single personalized pieces.': 'Das Angebotsrisiko ist bei Tests niedrig, bei Einzelst\u00fccken h\u00f6her.',
    'This is the second active workflow for comparison.': 'Dies ist der zweite aktive Workflow f\u00fcr den Vergleich.',
    'It creates a design preview from parameters, not machine-control output.': 'Er erstellt eine Designvorschau aus Parametern, keine Maschinensteuerungs-Ausgabe.',
    'The same shell pattern should support material tests and simple design jobs.': 'Dieselbe Shell-Struktur sollte Materialtests und einfache Designjobs tragen.',
    'Shape and size drive the preview bounds.': 'Form und Gr\u00f6\u00dfe bestimmen die Vorschaugrenzen.',
    'Circle and rectangle blanks test how well the UI handles different generator inputs.': 'Kreis- und Rechteckrohlinge zeigen, wie gut die UI verschiedene Generator-Eingaben tr\u00e4gt.',
    'Safe margin is a design constraint, not a machine guarantee.': 'Der sichere Rand ist eine Designbedingung, keine Maschinengarantie.',
    'The name field should feel friendly but still precise.': 'Das Namensfeld soll freundlich wirken, aber pr\u00e4zise bleiben.',
    'Motif choices show where a future generator could build SVG layers.': 'Motivoptionen zeigen, wo ein sp\u00e4terer Generator SVG-Ebenen bauen k\u00f6nnte.',
    'Text position needs immediate preview feedback.': 'Die Textposition braucht sofortige Vorschau-R\u00fcckmeldung.',
    'Pattern intent helps compare laser-only and hybrid design flows.': 'Die Musterabsicht hilft beim Vergleich von reinen Laser- und Hybrid-Designflows.',
    'Safety stays visible even for playful design work.': 'Sicherheit bleibt auch bei spielerischer Designarbeit sichtbar.',
    'Returned paths would be authoritative in a future backend.': 'Zur\u00fcckgegebene Pfade w\u00e4ren in einem sp\u00e4teren Backend verbindlich.',
    'For now the package is a static output plan only.': 'Aktuell ist das Paket nur ein statischer Ausgabeplan.',
    'SVG preview is the first target; CNC/laser layers are later work.': 'SVG-Vorschau ist das erste Ziel; CNC-/Laser-Ebenen sind sp\u00e4tere Arbeit.',
    'Design generators still need material and output verification.': 'Design-Generatoren brauchen weiterhin Material- und Ausgabepr\u00fcfung.',
    'Preview all layers before any future machine export.': 'Alle Ebenen vor jedem sp\u00e4teren Maschinenexport pr\u00fcfen.',
    'This concept never writes files or sends jobs.': 'Dieses Konzept schreibt nie Dateien und sendet keine Jobs.'
  };

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

  function localizedModuleName(module) {
    return languageCopy[activeLanguage]?.moduleNames?.[module] || moduleNames[module] || 'Test Pattern';
  }

  function localizedSubnavLabel(label) {
    return subnavLabels[activeLanguage]?.[label] || label;
  }

  function localizedText(text) {
    if (activeLanguage !== 'de') return text;
    return staticTextDe[text] || text;
  }

  function updateMotionLabel() {
    const button = $('motionToggle');
    if (!button) return;
    const key = document.body.classList.contains('reduce-motion') ? 'motionOff' : 'motionOn';
    button.textContent = translations[activeLanguage]?.[key] || translations.en[key];
  }

  function applyStaticLanguage() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest('script, style, svg, [data-i18n], [data-language-switch]')) return NodeFilter.FILTER_REJECT;
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      if (!node.__sourceText) node.__sourceText = node.nodeValue;
      const source = node.__sourceText;
      const trimmed = source.trim();
      if (!trimmed) return;
      const translated = localizedText(trimmed);
      node.nodeValue = source.replace(trimmed, translated);
    });
    updateMotionLabel();
  }

  function refreshLanguage(language) {
    activeLanguage = language;
    const currentView = app.dataset.view;
    renderSubnav(state.activeModule, currentView);
    render();
    applyStaticLanguage();
  }

  function renderContext(view){
    const lines = contextCopy[view] || contextCopy.job;
    const panel = panels.find(p => p.dataset.panel === view);
    if (contextTitle) contextTitle.textContent = localizedText(panel?.querySelector('h1')?.textContent || 'Job intelligence');
    if (contextList) contextList.innerHTML = lines.map(line => `<li>${localizedText(line)}</li>`).join('');
  }

  function openPanel(view){
    app.dataset.view = view;
    panels.forEach(p => p.classList.toggle('active-panel', p.dataset.panel === view));
    document.querySelectorAll('.sub').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    renderContext(view);
    renderPreview();
  }

  function renderSubnav(module, targetView){
    const labels = subnavs[module] || subnavs.pattern;
    state.activeModule = module;
    moduleTitle.textContent = localizedModuleName(module);
    subnavList.innerHTML = '';
    labels.forEach(([label, view], index) => {
      const btn = document.createElement('button');
      btn.className = 'sub' + ((targetView ? view === targetView : index === 0) ? ' active' : '');
      btn.textContent = localizedSubnavLabel(label);
      btn.dataset.view = view;
      btn.addEventListener('click', () => openPanel(btn.dataset.view));
      subnavList.appendChild(btn);
    });
    const hasTarget = labels.some(([, view]) => view === targetView);
    openPanel(hasTarget ? targetView : labels[0][1]);
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
      if (previewStatus) previewStatus.textContent = languageCopy[activeLanguage]?.designDraft || 'design draft';
      renderDesignPreview(g);
      return;
    }
    if (previewStatus) previewStatus.textContent = languageCopy[activeLanguage]?.previewRequired || 'preview required';
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
  $('generateMock')?.addEventListener('click', () => { $('generateMsg').textContent = languageCopy[activeLanguage]?.generateDisabled || languageCopy.en.generateDisabled; });
  $('motionToggle')?.addEventListener('click', () => {
    document.body.classList.toggle('reduce-motion');
    updateMotionLabel();
  });
  activeLanguage = V2I18n.getLanguage();
  renderSubnav('pattern');
  render();
  V2I18n.initLanguage(translations, refreshLanguage);
  applyStaticLanguage();
})();

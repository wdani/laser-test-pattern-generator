(() => {
  const views = [...document.querySelectorAll('.view')];
  const navButtons = [...document.querySelectorAll('.global-nav button')];
  const jobButtons = [...document.querySelectorAll('.queue-job')];
  const outputButtons = [...document.querySelectorAll('.format-tabs button')];
  const tiles = document.getElementById('tiles');
  const state = { job: 'laserPattern', output: 'Both' };
  let activeLanguage = 'en';

  const translations = {
    en: { localBadge: 'Local in browser' },
    de: { localBadge: 'Lokal im Browser' }
  };

  const staticTextDe = {
    'Local workshop jobs plus focused helpers - not a CAM replacement': 'Lokale Werkstatt-Jobs plus fokussierte Helfer - kein CAM-Ersatz',
    'Dashboard': 'Dashboard',
    'Current Job': 'Aktueller Job',
    'Helpers': 'Helfer',
    'Machine': 'Maschine',
    'Settings': 'Einstellungen',
    'Workshop jobs': 'Werkstatt-Jobs',
    'Active workflows + helpers': 'Aktive Workflows + Helfer',
    'active': 'aktiv',
    'helper': 'Helfer',
    'Laser Test Pattern': 'Laser-Testmuster',
    'Find material settings': 'Materialwerte finden',
    'Parametric Design': 'Parametrisches Design',
    'Nameplate from parameters': 'Namensschild aus Parametern',
    'Hybrid Planner': 'Hybrid-Planer',
    'CNC pocket + laser detail': 'CNC-Tasche + Laser-Detail',
    'Failed Job Analysis': 'Fehlgeschlagener Job',
    'Burned, too light, fuzzy': 'Verbrannt, zu hell, unscharf',
    'Bugreport Package': 'Bugreport-Paket',
    'Clean report for beta issues': 'Sauberer Bericht f\u00fcr Beta-Probleme',
    'Job idea': 'Job-Idee',
    'Today in the workshop': 'Heute in der Werkstatt',
    'Open check: air assist unknown': 'Offene Pr\u00fcfung: Air Assist unbekannt',
    'Next idea: parametric nameplate with Romy': 'N\u00e4chste Idee: parametrisches Namensschild mit Romy',
    'Maintenance: lens clean due in 2 runs': 'Wartung: Linse in 2 Jobs reinigen',
    'Workshop overview': 'Werkstatt\u00fcbersicht',
    'Choose an active workflow, then use the right helpers.': 'Aktiven Workflow w\u00e4hlen, dann passende Helfer nutzen.',
    'Concept B is a workshop app with concrete job types. Laser Test Pattern and Parametric Design are active workflows; calculators, safety, journal, and diagnostics support the selected job.': 'Concept B ist eine Werkstatt-App mit konkreten Jobtypen. Laser Test Pattern und Parametric Design sind aktive Workflows; Rechner, Sicherheit, Journal und Diagnose unterst\u00fctzen den gew\u00e4hlten Job.',
    'Material job': 'Material-Job',
    'Find reliable power/speed settings and save them to the material memory.': 'Verl\u00e4ssliche Leistungs-/Geschwindigkeitswerte finden und in der Material-Erinnerung speichern.',
    'Active generator job': 'Aktiver Generator-Job',
    'Create a simple design from dimensions, text, motif, pattern, and operation intent.': 'Ein einfaches Design aus Ma\u00dfen, Text, Motiv, Muster und Bearbeitungsziel erstellen.',
    'Helper job': 'Helfer-Job',
    'Decide what gets milled, what gets lasered, and which step comes first.': 'Entscheiden, was gefr\u00e4st, was gelasert und welcher Schritt zuerst kommt.',
    'Turn a bad result into concrete next settings: speed, power, focus, air assist, or cutter.': 'Ein schlechtes Ergebnis in konkrete n\u00e4chste Einstellungen \u00fcbersetzen: Geschwindigkeit, Leistung, Fokus, Air Assist oder Fr\u00e4ser.',
    'Support helper': 'Support-Helfer',
    'Collect app version, machine, files, screenshots, and reproduction steps.': 'App-Version, Maschine, Dateien, Screenshots und Repro-Schritte sammeln.',
    'Active workflow': 'Aktiver Workflow',
    'The first active job type and source of the material-test preview.': 'Der erste aktive Jobtyp und Ursprung der Materialtest-Vorschau.',
    'Nameplate/pattern generator concept with SVG preview and future layers.': 'Namensschild-/Muster-Generator-Konzept mit SVG-Vorschau und sp\u00e4teren Ebenen.',
    'Tool': 'Werkzeug',
    'Stores best cells, photos, notes, and repeatability.': 'Speichert beste Zellen, Fotos, Notizen und Wiederholbarkeit.',
    'SVG Detail Checker': 'SVG-Detailpr\u00fcfung',
    'Supports generator and hybrid jobs when an imported design is involved.': 'Unterst\u00fctzt Generator- und Hybrid-Jobs, wenn ein importiertes Design beteiligt ist.',
    'V-bit Calculator': 'V-Bit-Rechner',
    'Helps decide whether text and borders can be milled.': 'Hilft zu entscheiden, ob Text und R\u00e4nder gefr\u00e4st werden k\u00f6nnen.',
    'Cost Calculator': 'Kostenrechner',
    "Uses the selected job's material, time, setup, and risk.": 'Nutzt Material, Zeit, Einrichtung und Risiko des ausgew\u00e4hlten Jobs.',
    'Preflight Checklist': 'Sicherheits-Checkliste',
    'Checks material safety, output scale, air assist, and machine readiness.': 'Pr\u00fcft Materialsicherheit, Ausgabeskala, Air Assist und Maschinenbereitschaft.',
    'Job brief': 'Job-Briefing',
    'Making plan': 'Ablaufplan',
    'Tools for this job': 'Werkzeuge f\u00fcr diesen Job',
    'Readiness': 'Bereitschaft',
    'Memory / output': 'Erinnerung / Ausgabe',
    'Tools and assistants': 'Werkzeuge und Assistenten',
    'Helpers for the selected job, not separate projects.': 'Helfer f\u00fcr den ausgew\u00e4hlten Job, keine separaten Projekte.',
    'These tools are supporting surfaces. They help the current job with feasibility, calculation, safety, documentation, and export decisions.': 'Diese Werkzeuge sind unterst\u00fctzende Fl\u00e4chen. Sie helfen dem aktuellen Job bei Machbarkeit, Berechnung, Sicherheit, Dokumentation und Exportentscheidungen.',
    'Output plan': 'Ausgabeplan',
    'Mock generate message': 'Mock-Erzeugung melden',
    'No files are generated.': 'Es werden keine Dateien erzeugt.',
    'Front warnings': 'Wichtige Hinweise',
    'Machine': 'Maschine',
    'Profiles, local monitor mock, and maintenance context.': 'Profile, lokaler Monitor-Mock und Wartungskontext.',
    'The machine area supports jobs with profile assumptions and readiness state. It does not control hardware.': 'Der Maschinenbereich unterst\u00fctzt Jobs mit Profilannahmen und Bereitschaftsstatus. Er steuert keine Hardware.',
    'Static local prototype settings': 'Statische lokale Prototyp-Einstellungen',
    'No persistence, no backend, no build system, no generation, no cloud dependency.': 'Keine Persistenz, kein Backend, kein Build-System, keine Erzeugung, keine Cloud-Abh\u00e4ngigkeit.',
    'Fit': 'Einpassen',
    'Layers': 'Ebenen',
    'Warnings': 'Warnungen',
    'Static prototype only: no files are generated or sent.': 'Statischer Prototyp: Es werden keine Dateien erzeugt oder gesendet.',
    'Material settings job': 'Material-Einstellungsjob',
    'Find reliable laser settings for cork and save the best result as material memory.': 'Zuverl\u00e4ssige Lasereinstellungen f\u00fcr Kork finden und das beste Ergebnis als Material-Erinnerung speichern.',
    'Create a 7 x 7 cork test grid with clear output and preflight state.': 'Ein 7 x 7 Kork-Testraster mit klarer Ausgabe und Preflight-Status erstellen.',
    'This is a concrete job: find usable material settings, not just open a module.': 'Das ist ein konkreter Job: brauchbare Materialwerte finden, nicht nur ein Modul \u00f6ffnen.',
    'Uses: Material Journal, Output Profile, Cost Calculator, Preflight.': 'Nutzt: Material-Journal, Ausgabeprofil, Kostenrechner, Preflight.',
    'Laser Test Pattern preview': 'Laser-Testmuster-Vorschau',
    'margin low': 'Rand knapp',
    'Material': 'Material',
    'Cork 3 mm': 'Kork 3 mm',
    'Stock': 'Werkst\u00fcck',
    '100 x 100 mm': '100 x 100 mm',
    'Makera laser profile': 'Makera Laserprofil',
    'Purpose': 'Zweck',
    'Material library': 'Materialbibliothek',
    'Laser Test Pattern settings': 'Laser-Testmuster-Einstellungen',
    'Cork': 'Kork',
    'Preset': 'Preset',
    'Cork fine 7 x 7': 'Kork fein 7 x 7',
    'Margin': 'Rand',
    '8 mm': '8 mm',
    'Grid': 'Raster',
    '7 x 7': '7 x 7',
    'Tile / gap': 'Kachel / Abstand',
    '8 mm / 2 mm': '8 mm / 2 mm',
    'Speed range': 'Geschwindigkeitsbereich',
    '2200-4000 mm/min': '2200-4000 mm/min',
    'Power range': 'Leistungsbereich',
    '5-20 %': '5-20 %',
    'Mode': 'Modus',
    'Offset Fill': 'Offset Fill',
    'MKS + NC': 'MKS + NC',
    'Choose material and stock size.': 'Material und Werkst\u00fcckgr\u00f6\u00dfe w\u00e4hlen.',
    'Generate labeled power/speed grid.': 'Beschriftetes Leistungs-/Geschwindigkeitsraster erzeugen.',
    'Preview MKS and NC output names.': 'MKS- und NC-Ausgabenamen pr\u00fcfen.',
    'Run only after preflight, then save the best cell.': 'Erst nach Preflight ausf\u00fchren, dann beste Zelle speichern.',
    'Output Profile': 'Ausgabeprofil',
    'Preflight Checklist': 'Preflight-Checkliste',
    'safe': 'sicher',
    'Output': 'Ausgabe',
    'previewed': 'vorgepr\u00fcft',
    'Air assist': 'Air Assist',
    'review': 'pr\u00fcfen',
    'Journal': 'Journal',
    'candidate': 'Kandidat',
    'Settings hash': 'Einstellungs-Hash',
    'Last result': 'Letztes Ergebnis',
    '3000 mm/min at 12%': '3000 mm/min bei 12%',
    'Next action': 'N\u00e4chster Schritt',
    'macro photo before preset': 'Makrofoto vor Preset',
    'Air assist is not confirmed.': 'Air Assist ist nicht best\u00e4tigt.',
    'NC S-scale must be checked before use.': 'NC-S-Skala muss vor Nutzung gepr\u00fcft werden.',
    'Macro photo missing before preset promotion.': 'Makrofoto fehlt vor Preset-Freigabe.',
    'Parametric generator job': 'Parametrischer Generator-Job',
    'Parametric Design Generator': 'Parametrischer Design Generator',
    'Create a simple nameplate or pattern design from shape, size, text, motif, operation intent, and output target parameters.': 'Ein einfaches Namensschild- oder Musterdesign aus Form, Gr\u00f6\u00dfe, Text, Motiv, Bearbeitungsziel und Ausgabeziel erstellen.',
    'Generate a simple Romy nameplate preview from parameters.': 'Eine einfache Romy-Namensschild-Vorschau aus Parametern erzeugen.',
    'Parametric Nameplate': 'Parametrisches Namensschild',
    'A job for quick personalized parts that do not need a full CAD/CAM workflow.': 'Ein Job f\u00fcr schnelle personalisierte Teile ohne kompletten CAD/CAM-Workflow.',
    'Uses: Pattern Generator, SVG Preview, V-bit Calculator, Cost Calculator.': 'Nutzt: Pattern Generator, SVG-Vorschau, V-Bit-Rechner, Kostenrechner.',
    'Nameplate generator preview': 'Namensschild-Generator-Vorschau',
    'parameter draft': 'Parameter-Entwurf',
    'Basswood 2 mm': 'Lindenholz 2 mm',
    'Blank': 'Rohling',
    'Text': 'Text',
    'Romy': 'Romy',
    'Symbol': 'Symbol',
    'Star': 'Stern',
    'Parametric design settings': 'Parametrische Design-Einstellungen',
    'Workpiece shape': 'Werkst\u00fcckform',
    'rectangle / circle': 'Rechteck / Kreis',
    'Width / height': 'Breite / H\u00f6he',
    '120 x 55 mm': '120 x 55 mm',
    'Diameter': 'Durchmesser',
    '80 mm option': '80-mm-Option',
    'Thickness': 'Dicke',
    '3 mm': '3 mm',
    'Name text': 'Namenstext',
    'Text position': 'Textposition',
    'lower third': 'unteres Drittel',
    'Motif / pattern': 'Motiv / Muster',
    'star, stripes, radial, diagonal': 'Stern, Streifen, radial, diagonal',
    'Operation intent': 'Bearbeitungsziel',
    'laser only or CNC outline + laser detail': 'nur Laser oder CNC-Kontur + Laser-Detail',
    'Output target': 'Ausgabeziel',
    'SVG preview, future layers': 'SVG-Vorschau, sp\u00e4tere Ebenen',
    'Machine output': 'Maschinenausgabe',
    'not generated yet': 'noch nicht erzeugt',
    'Set shape, size, and material thickness.': 'Form, Gr\u00f6\u00dfe und Materialdicke festlegen.',
    'Place the name and motif from parameters.': 'Name und Motiv aus Parametern platzieren.',
    'Preview text fit, safe margin, and pattern readability.': 'Text-Fit, Sicherheitsrand und Musterlesbarkeit pr\u00fcfen.',
    'Keep output as SVG preview/future layers until real backend support exists.': 'Ausgabe als SVG-Vorschau/sp\u00e4tere Ebenen behalten, bis echte Backend-Unterst\u00fctzung existiert.',
    'Parametric Pattern Generator': 'Parametrischer Muster-Generator',
    'Text Fit Check': 'Text-Fit-Pr\u00fcfung',
    'SVG Preview': 'SVG-Vorschau',
    'Text fit': 'Text-Fit',
    'ok': 'ok',
    'Motif': 'Motiv',
    'star': 'Stern',
    'SVG preview': 'SVG-Vorschau',
    'ready': 'bereit',
    'Machine files': 'Maschinendateien',
    'not real yet': 'noch nicht echt',
    'Design hash': 'Design-Hash',
    'Reusable template': 'Wiederverwendbare Vorlage',
    'nameplate 120 x 55': 'Namensschild 120 x 55',
    'compare rectangle and circle blanks': 'Rechteck- und Kreisrohlinge vergleichen',
    'Generated design preview is not machine-control output.': 'Die erzeugte Designvorschau ist keine Maschinensteuerungs-Ausgabe.',
    'Future CNC/laser layers must be previewed before use.': 'Sp\u00e4tere CNC-/Laser-Ebenen m\u00fcssen vor Nutzung gepr\u00fcft werden.',
    'Text should remain readable at final scale.': 'Text soll in Zielgr\u00f6\u00dfe lesbar bleiben.',
    'helper view': 'Helferansicht'
  };

  function localizedText(text) {
    if (activeLanguage !== 'de') return text;
    return staticTextDe[text] || text;
  }

  function localPair([label, value]) {
    return [localizedText(label), localizedText(value)];
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
      node.nodeValue = source.replace(trimmed, localizedText(trimmed));
    });
  }

  function refreshLanguage(language) {
    activeLanguage = language;
    renderJob();
    applyStaticLanguage();
  }

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
    tiles.appendChild(svgEl('text', { x: 210, y: 330, class: 'helper-preview-text', 'text-anchor': 'middle' }, localizedText('helper view')));
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
    el('railJobIdea').textContent = localizedText(job.railIdea);
    el('railJobWhy').textContent = localizedText(job.railWhy);
    el('railJobTools').textContent = localizedText(job.railTools);
    el('jobKicker').textContent = localizedText(job.kicker);
    el('jobTitle').textContent = localizedText(job.title);
    el('jobSummary').textContent = localizedText(job.summary);
    el('jobGoal').textContent = localizedText(job.goal);
    el('settingsLabel').textContent = localizedText(job.settingsLabel);
    el('previewTitle').textContent = localizedText(job.preview);
    el('bounds').textContent = localizedText(job.status);
    el('briefFacts').innerHTML = html(job.brief.map(localPair), ([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`);
    el('settingsGrid').innerHTML = html(job.settings.map(localPair), ([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`);
    el('jobPlan').innerHTML = html(job.plan, item => `<li>${localizedText(item)}</li>`);
    el('jobTools').innerHTML = html(job.tools, item => `<span>${localizedText(item)}</span>`);
    el('readinessGrid').innerHTML = html(job.readiness.map(localPair), ([label, value]) => `<span><b>${label}</b><strong>${value}</strong></span>`);
    el('memoryGrid').innerHTML = html(job.memory.map(localPair), ([label, value]) => `<div><b>${label}</b><strong>${value}</strong></div>`);
    el('warningList').innerHTML = html(job.warnings, item => `<li>${localizedText(item)}</li>`);
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
    el('mockMessage').textContent = localizedText('Static prototype only: no files are generated or sent.');
  });

  activeLanguage = V2I18n.getLanguage();
  renderJob();
  V2I18n.initLanguage(translations, refreshLanguage);
  applyStaticLanguage();
})();

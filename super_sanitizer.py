import re
from collections import Counter, defaultdict

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Module
content = content.replace('<script>', '<script type="module">', 1)

match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if match:
    script_start = match.start(1)
    script_end = match.end(1)
    script_content = match.group(1)

    # Find all declarations
    # This is hard. Let's try to match:
    # 1. function NAME
    # 2. async function NAME
    # 3. let/const/var NAME1, NAME2 = val, NAME3;

    decls = []

    # Functions
    for m in re.finditer(r'\b(?:async\s+)?function\s+([a-zA-Z0-9_]+)\b', script_content):
        decls.append({'name': m.group(1), 'start': m.start(1), 'end': m.end(1)})

    # Variables (let, const, var)
    # We match the keyword then the rest of the line until ;
    for m in re.finditer(r'^\s*(let|const|var)\s+([^;]+);', script_content, re.M):
        keyword = m.group(1)
        rest = m.group(2)
        # Find all names in 'rest'. Names are followed by =, ,, or end of string.
        # This is a bit loose but should capture most.
        for sm in re.finditer(r'\b([a-zA-Z0-9_]+)\b(?:\s*[=,]|(?:\s*$))', rest):
            name = sm.group(1)
            # Offset in script_content
            name_start = m.start(2) + sm.start(1)
            name_end = m.start(2) + sm.end(1)
            decls.append({'name': name, 'start': name_start, 'end': name_end})

    decls.sort(key=lambda x: x['start'])

    name_counts = Counter(d['name'] for d in decls)
    dups = {n for n, c in name_counts.items() if c > 1}

    # Process from end to start
    decls.sort(key=lambda x: x['start'], reverse=True)
    seen = Counter()
    s_list = list(script_content)

    for d in decls:
        name = d['name']
        if name in dups:
            occurrence_idx = name_counts[name] - seen[name] - 1
            seen[name] += 1
            if occurrence_idx < name_counts[name] - 1:
                new_name = f"{name}_old_{occurrence_idx}"
                s_list[d['start']:d['end']] = list(new_name)

    script_content = "".join(s_list)

    # 2. Exposure
    exposed_functions = [
        "addTipoCap", "approveUser", "aprobarActa", "aprobarActaDirect", "authTab",
        "changePassword", "clearFirma", "clearFirmaCanvas", "closeModal",
        "delTipoCap", "deleteCap", "deletePlan", "doLogin", "doLogout", "doRegister",
        "downloadPDF", "editCap", "editPlan", "exportCSV", "initInfPeriodo",
        "loadPrestConfig", "markNotifRead", "onCapNomSelect", "onDashTipoChange",
        "onPlanAreaChange", "onPrestExcelChange", "onUsersExcelChange",
        "openCapModal", "openChangePass", "openCreateUserModal", "openEditPerfil",
        "openFirmaCanvas", "openModal", "openPlanModal", "openPrestModal", "printActa",
        "rejectUser", "renderCalendario", "renderCaps", "renderDash", "renderInformes",
        "renderPlan", "saveCap", "saveCreateUser", "saveEditPerfil", "saveFirmaFromCanvas",
        "saveFooterConfig", "saveMetas", "savePlan", "savePrestador", "seedMunicipios",
        "seedPrestadores", "seedTiposCap", "showView", "switchTab", "updateCUAreas",
        "updateCapAreaFilter", "updateCapModalAreas", "updatePlanAreaFilter",
        "updateRegAreas", "uploadFirma", "uploadProfilePhoto", "verActa"
    ]

    exposure_script = "\n// --- Global Exposure ---\n"
    exposure_script += 'const ADMIN_NAME = "Administrador ODS";\n'
    for func in exposed_functions:
        exposure_script += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

    vars_to_expose = ["allCaps", "allPlans", "allUsers", "allActores", "tiposCap", "metas"]
    for v in vars_to_expose:
        if v in script_content and '_old_' not in v:
             exposure_script += f"try {{ Object.defineProperty(window, '{v}', {{ get: () => {v}, set: (val) => {{ {v} = val; }}, configurable: true }}); }} catch(e) {{}}\n"

    script_content += exposure_script
    content = content[:script_start] + script_content + content[script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

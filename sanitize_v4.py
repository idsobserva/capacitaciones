import re
from collections import Counter

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change to module
content = content.replace('<script>', '<script type="module">', 1)

match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if match:
    script_start = match.start(1)
    script_end = match.end(1)
    script_content = match.group(1)

    # Find ALL top-level declarations
    # This regex looks for declarations that are either at the start of a line
    # or preceded by only whitespace.
    decl_regex = re.compile(r'^\s*(async\s+function|function|let|const|var)\s+([a-zA-Z0-9_]+)\b', re.M)

    all_decls = []
    for m in decl_regex.finditer(script_content):
        all_decls.append({
            'name': m.group(2),
            'start': m.start(2),
            'end': m.end(2)
        })

    # Group by name
    name_counts = Counter(d['name'] for d in all_decls)
    dups = {n for n, c in name_counts.items() if c > 1}

    # Process replacements from end to start
    all_decls.sort(key=lambda x: x['start'], reverse=True)

    seen = Counter()
    s_list = list(script_content)

    for d in all_decls:
        name = d['name']
        if name in dups:
            occurrence_idx = name_counts[name] - seen[name] - 1
            seen[name] += 1
            if occurrence_idx < name_counts[name] - 1:
                # This is NOT the last one, rename it
                new_name = f"{name}_old_{occurrence_idx}"
                s_list[d['start']:d['end']] = list(new_name)

    script_content = "".join(s_list)

    # 2. Global Exposure for on* attributes
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
    if "const ADMIN_NAME" not in script_content and "var ADMIN_NAME" not in script_content:
        exposure_script += 'const ADMIN_NAME = "Administrador ODS";\n'

    for func in exposed_functions:
        exposure_script += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

    vars_to_expose = ["allCaps", "allPlans", "allUsers", "allActores", "tiposCap", "metas"]
    for v in vars_to_expose:
        if v in script_content:
            exposure_script += f"try {{ Object.defineProperty(window, '{v}', {{ get: () => {v}, set: (val) => {{ {v} = val; }}, configurable: true }}); }} catch(e) {{}}\n"

    script_content += exposure_script

    content = content[:script_start] + script_content + content[script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

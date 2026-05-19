import re

def get_brace_content(text, start_pos):
    brace_start = text.find('{', start_pos)
    if brace_start == -1: return None, start_pos
    count = 1
    i = brace_start + 1
    while count > 0 and i < len(text):
        if text[i] == '{': count += 1
        elif text[i] == '}': count -= 1
        i += 1
    return text[start_pos:i], i

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Convert to module
content = content.replace('<script>', '<script type="module">', 1)

match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if match:
    script_start = match.start(1)
    script_end = match.end(1)
    script_content = match.group(1)

    # Find all function declarations
    # Keyword (group 1), Name (group 2)
    func_pattern = re.compile(r'^\s*(async\s+function|function)\s+([a-zA-Z0-9_]+)\b', re.M)
    funcs = []
    for m in func_pattern.finditer(script_content):
        funcs.append({'name': m.group(2), 'start': m.start()})

    # Identify duplicates
    from collections import Counter
    name_counts = Counter(f['name'] for f in funcs)

    # Process from end to start to avoid offset issues
    # But wait, I'll just replace the body of the ones I want to remove with spaces
    for name, count in name_counts.items():
        if count > 1:
            occurrences = [f for f in funcs if f['name'] == name]
            # Keep the last one
            for occ in occurrences[:-1]:
                # Find the end of this function body
                _, end_pos = get_brace_content(script_content, occ['start'])
                # Replace with spaces
                script_content = script_content[:occ['start']] + (" " * (end_pos - occ['start'])) + script_content[end_pos:]

    # Do the same for top-level variable declarations (let/const/var at start of line)
    var_pattern = re.compile(r'^\s*(let|const|var)\s+([a-zA-Z0-9_]+)\b', re.M)
    vars_found = []
    for m in var_pattern.finditer(script_content):
        vars_found.append({'name': m.group(2), 'start': m.start(), 'end': m.end()})

    var_counts = Counter(v['name'] for v in vars_found)
    for name, count in var_counts.items():
        if count > 1:
            occurrences = [v for v in vars_found if v['name'] == name]
            for occ in occurrences[:-1]:
                # Find end of statement (next ;)
                end_stmt = script_content.find(';', occ['start'])
                if end_stmt != -1:
                    script_content = script_content[:occ['start']] + (" " * (end_stmt - occ['start'] + 1)) + script_content[end_stmt+1:]

    # Exposure
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
        exposure_script += f"try {{ Object.defineProperty(window, '{v}', {{ get: () => {v}, set: (val) => {{ {v} = val; }}, configurable: true }}); }} catch(e) {{}}\n"

    # Remove thousands of try-catch blocks
    script_content = re.sub(r'try\s*{\s*(window|Object\.defineProperty).*?\}\s*catch\s*\(e\)\s*{\s*}', '', script_content, flags=re.DOTALL)
    script_content = re.sub(r'try\s*{\s*}\s*catch\s*\(e\)\s*{\s*}', '', script_content)

    script_content += exposure_script
    content = content[:script_start] + script_content + content[script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

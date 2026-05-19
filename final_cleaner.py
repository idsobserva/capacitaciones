import re
from collections import defaultdict

def remove_function_body(content, start_pos):
    brace_start = content.find('{', start_pos)
    if brace_start == -1: return content, start_pos
    count = 1
    i = brace_start + 1
    while count > 0 and i < len(content):
        if content[i] == '{': count += 1
        elif content[i] == '}': count -= 1
        i += 1
    return content[:start_pos] + (" " * (i - start_pos)) + content[i:], i

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<script>', '<script type="module">', 1)

match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
if match:
    script_start = match.start(1)
    script_end = match.end(1)
    script_content = match.group(1)

    # 1. Targeted removal of redundant try-catch at the end
    script_content = re.sub(r'try\s*{\s*(window|Object\.defineProperty).*?\}\s*catch\s*\(e\)\s*{\s*}', '', script_content, flags=re.DOTALL)
    script_content = re.sub(r'try\s*{\s*}\s*catch\s*\(e\)\s*{\s*}', '', script_content)

    # 2. Find all declarations
    decl_regex = re.compile(r'^\s*(async\s+function|function|let|const|var)\s+([a-zA-Z0-9_]+)\b', re.M)
    all_decls = []
    for m in decl_regex.finditer(script_content):
        all_decls.append({
            'type': m.group(1),
            'name': m.group(2),
            'start': m.start(),
            'name_start': m.start(2),
            'name_end': m.end(2)
        })

    name_map = defaultdict(list)
    for d in all_decls:
        name_map[d['name']].append(d)

    for name, decls in name_map.items():
        if len(decls) > 1:
            to_remove = decls[:-1]
            for d in to_remove:
                if 'function' in d['type']:
                    script_content, _ = remove_function_body(script_content, d['start'])
                else:
                    # Comment out the line
                    line_end = script_content.find('\n', d['start'])
                    if line_end != -1:
                        script_content = script_content[:d['start']] + "// " + script_content[d['start']:]

    # 3. Add Global Exposure
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

    script_content += exposure_script

    content = content[:script_start] + script_content + content[script_end:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

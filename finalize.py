import re
from collections import Counter

def get_script_content(html):
    match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if not match:
        match = re.search(r'<script type="module">(.*?)</script>', html, re.DOTALL)
    if not match: return None, None, None
    return match.group(1), match.start(), match.end()

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

script, start, end = get_script_content(html)
if script:
    # Use a simpler but more robust way to find declarations
    # We'll split the script by lines and identify declarations
    lines = script.split('\n')

    # Track names to keep (last one)
    name_to_last_idx = {}

    # Basic declaration pattern: ^\s*(let|const|var|function|async function) NAME
    decl_pattern = re.compile(r'^\s*(?:async\s+)?(?:function|let|const|var)\s+([a-zA-Z0-9_]+)\b')

    for idx, line in enumerate(lines):
        match = decl_pattern.match(line)
        if match:
            name = match.group(1)
            name_to_last_idx[name] = idx

    # Also handle multiple declarations on one line: let a = 1, b = 2;
    # But usually the most important ones are on their own line or at the start.

    # Rename all but the last one
    for idx, line in enumerate(lines):
        match = decl_pattern.match(line)
        if match:
            name = match.group(1)
            if name_to_last_idx[name] != idx:
                # This is NOT the last one, rename it
                # We need to replace only the declaration part
                lines[idx] = re.sub(r'\b' + name + r'\b', f"{name}_old_{idx}", line, count=1)

    script = '\n'.join(lines)

    # Exposure Block
    # We want EVERYTHING that is a function or a global var to be on window
    # To keep it simple, we'll expose the list of known handlers
    exposed_functions = [
        "addActor", "addPerfilToUser", "addTipoCap", "approveUser", "aprobarActa",
        "aprobarActaDirect", "authTab", "changePassword", "clearFirma",
        "clearFirmaCanvas", "clearListaImage", "closeModal", "delActor",
        "delPrestador", "delTipoCap", "deleteCap", "deletePlan", "deleteUser",
        "doLogin", "doLogout", "doRegister", "downloadPDF", "editCap", "editPlan",
        "exportCSV", "filterIPSCheckboxes", "filterMunCheckboxes", "initInfPeriodo",
        "loadPrestConfig", "markNotifRead", "onCapNomSelect", "onDashTipoChange",
        "onListaImageChange", "onMunCapChange", "onMunPlanChange", "onPerfilCapChange",
        "onPerfilPlanChange", "onPlanAreaChange", "onPlanActorChange", "onPrestExcelChange",
        "onUsersExcelChange", "openCapModal", "openChangePass", "openCreateUserModal",
        "openEditPerfil", "openFirmaCanvas", "openModal", "openPlanModal",
        "openPrestModal", "printActa", "rejectUser", "renderCalendario",
        "renderCaps", "renderDash", "renderInformes", "renderPlan", "rmCMun",
        "rmPMun", "rmPerfilCap", "rmPerfilPlan", "saveCap", "saveCreateUser",
        "saveEditPerfil", "saveFirmaFromCanvas", "saveFooterConfig", "saveMetas",
        "savePlan", "savePrestador", "seedMunicipios", "seedPrestadores",
        "seedTiposCap", "showView", "switchTab", "toggleUserStatus", "updateCUAreas",
        "updateCapAreaFilter", "updateCapModalAreas", "updatePlanAreaFilter",
        "updateRegAreas", "uploadFirma", "uploadProfilePhoto", "verActa"
    ]

    exposure_script = "\n// --- Global Exposure ---\n"
    exposure_script += 'const ADMIN_NAME = "Administrador ODS";\n'
    for func in exposed_functions:
        exposure_script += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

    exposed_vars = ["allCaps", "allPlans", "allUsers", "allActores", "tiposCap", "metas"]
    for var in exposed_vars:
        exposure_script += f"try {{ Object.defineProperty(window, '{var}', {{ get: () => {var}, set: (val) => {{ {var} = val; }}, configurable: True }}); }} catch(e) {{}}\n"

    script += exposure_script

    new_html = html[:start] + '<script type="module">' + script + '</script>' + html[end:]

    # Final cleanup of any potential leftover tags if start/end logic failed
    # Actually the start/end should be correct.

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

print("Done")

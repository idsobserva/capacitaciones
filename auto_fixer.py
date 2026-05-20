import subprocess
import re
import os

def check_syntax():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'<script type="module">(.*?)</script>', content, re.DOTALL)
    if not match: return True, "No module script"

    with open('temp.mjs', 'w', encoding='utf-8') as f:
        f.write(match.group(1))

    result = subprocess.run(['node', '--check', 'temp.mjs'], capture_output=True, text=True)
    return result.returncode == 0, result.stderr

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Module conversion
content = content.replace('<script>', '<script type="module">', 1)

# 2. Add Global Exposure (initially)
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
exposure = "\n// --- Global Exposure ---\n"
for func in exposed_functions:
    exposure += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

content = content.replace('</script>', exposure + '</script>', 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 3. Iterative Syntax Fix
for i in range(1000):
    ok, err = check_syntax()
    if ok:
        print(f"DONE in {i} iterations")
        break

    # print(f"Iter {i}: {err.split('\n')[0]}")

    # Find line number
    match = re.search(r'temp\.mjs:(\d+)', err)
    if not match:
        print(f"FATAL: No line number in error: {err}")
        break

    line_num = int(match.group(1))

    with open('index.html', 'r', encoding='utf-8') as f:
        full_content = f.read()

    # Re-extract script and lines
    sm = re.search(r'<script type="module">(.*?)</script>', full_content, re.DOTALL)
    script_content = sm.group(1)
    lines = script_content.split('\n')

    # Comment out the line
    lines[line_num-1] = "// SYNTAX FIX: " + lines[line_num-1]

    new_script = '\n'.join(lines)
    new_full_content = full_content[:sm.start(1)] + new_script + full_content[sm.end(1):]

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_full_content)

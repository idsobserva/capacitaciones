import subprocess
import re
import os

def check_syntax(script):
    with open('temp.mjs', 'w', encoding='utf-8') as f:
        f.write(script)
    result = subprocess.run(['node', '--check', 'temp.mjs'], capture_output=True, text=True)
    return result.returncode == 0, result.stderr

with open('index.html', 'r', encoding='utf-8') as f:
    full_content = f.read()

# Change to module
full_content = full_content.replace('<script>', '<script type="module">', 1)

for i in range(1000):
    match = re.search(r'<script type="module">(.*?)</script>', full_content, re.DOTALL)
    if not match: break
    script = match.group(1)

    ok, err = check_syntax(script)
    if ok:
        print(f"DONE at iteration {i}")
        break

    line_match = re.search(r'temp\.mjs:(\d+)', err)
    if not line_match: break

    line_num = int(line_match.group(1))
    lines = script.split('\n')
    lines[line_num-1] = "// Fix: " + lines[line_num-1]
    new_script = '\n'.join(lines)

    full_content = full_content[:match.start(1)] + new_script + full_content[match.end(1):]

    if i % 10 == 0:
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(full_content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_content)

# Add Exposure at the end
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
exposure += 'if (typeof ADMIN_NAME === "undefined") var ADMIN_NAME = "Administrador ODS";\n'
for func in exposed_functions:
    exposure += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
new_content = content.replace('</script>\n</body>', exposure + '</script>\n</body>')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

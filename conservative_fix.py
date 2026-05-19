import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Module
content = content.replace('<script>', '<script type="module">', 1)

# 2. Add Global Exposure at the end of the script
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

content = content.replace('</script>\n</body>', exposure_script + '</script>\n</body>')

# 3. Rename ONLY the Syntax-Breaking Duplicates manually
# Identifier 'imageToBase64' has already been declared
# We'll rename the first occurrence to imageToBase64_0

def rename_first(text, name):
    return text.replace(f"function {name}", f"function {name}_0", 1).replace(f"const {name}", f"const {name}_0", 1).replace(f"let {name}", f"let {name}_0", 1).replace(f"var {name}", f"var {name}_0", 1)

# Let's use a more robust rename for specific names
breaking = ["imageToBase64", "uploadImage", "updateTopbarAvatar", "renderPerfilView", "_epPerfiles", "_ipsCache", "getIPSForMun", "loadFooterConfig", "applyFooterConfig", "prefillFooterModal", "postSetupInit", "buildQ", "renderActas", "selPerfilesCap", "selPerfilesPlan"]

for b in breaking:
    # Use regex to only match declarations
    pattern = re.compile(r'\b(function|let|const|var|async\s+function)\s+(' + b + r')\b')
    matches = list(pattern.finditer(content))
    if len(matches) > 1:
        # Rename ALL but the LAST one
        for i, m in enumerate(reversed(matches[:-1])):
            idx = len(matches) - 2 - i
            content = content[:m.start(2)] + f"{b}_old_{idx}" + content[m.end(2):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

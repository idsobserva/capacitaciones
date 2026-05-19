import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the empty <script> tag at 1474
content = content.replace('<script>\n\n\n\n\n\n\n\n\n\n\n\n\n', '', 1)

# 2. Fix the nested <script type="module"> if I added it inside another one
# But it seems I added it before the import.
# Let's just make sure there is ONLY ONE <script type="module"> start.

# 3. Define the exposure list
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
for func in exposed_functions:
    exposure_script += f"try {{ window.{func} = {func}; }} catch(e) {{}}\n"

exposed_vars = ["allCaps", "allPlans", "allUsers", "allActores", "tiposCap", "metas"]
for var in exposed_vars:
    exposure_script += f"try {{ Object.defineProperty(window, '{var}', {{ get: () => {var}, set: (val) => {{ {var} = val; }}, configurable: true }}); }} catch(e) {{}}\n"

# Remove any previous exposure blocks I might have added to avoid duplicates
content = re.sub(r'// --- Global Exposure ---.*?</script>', '</script>', content, flags=re.DOTALL)

# Insert before </body>
content = content.replace('</body>', exposure_script + '</script>\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

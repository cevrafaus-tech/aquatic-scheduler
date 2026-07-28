import streamlit as st
import pandas as pd
import datetime
import random
from supabase import create_client, Client

st.set_page_config(page_title="Aquatic Facilities Scheduler Enterprise", layout="wide")

# ==========================================
# ADVANCED INTERFACE STYLING (IMPROVED UI & CONTRAST)
# ==========================================
st.markdown("""
<style>
    /* Botones de celdas: Tipografía optimizada a 12px con alto contraste */
    div.stButton > button {
        width: 100%;
        border-radius: 6px !important;
        padding: 6px 4px !important;
        height: auto !important;
        line-height: 1.45 !important;
        text-align: center !important;
        white-space: pre-line !important;
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }

    div.stButton > button p {
        font-size: 12px !important;
        font-weight: 600 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        margin: 0 !important;
        line-height: 1.4 !important;
        text-align: center !important;
    }

    div.stButton > button:hover {
        background-color: #f3f4f6 !important;
        border-color: #1a73e8 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Tipografía mejorada */
    .role-text { color: #1a73e8; font-weight: 700; font-size: 12px !important; font-family: sans-serif; display: inline-block; margin-top: 6px; }
    .name-text { color: #1f2937; font-weight: 700; font-size: 12px !important; font-family: sans-serif; display: inline-block; margin-top: 6px; }
    .header-text { color: #111827; font-weight: 700; font-size: 12px !important; font-family: sans-serif; text-align: center; display: block; }
    .header-text-left { color: #111827; font-weight: 700; font-size: 12px !important; font-family: sans-serif; text-align: left; display: block; }
    
    /* Titulares y bloques de alarmas posicionales */
    .matrix-title { background-color: #1e293b; color: #ffffff; font-size: 13px; font-weight: 700; padding: 10px; text-align: left; margin-top: 24px; border-radius: 4px; }
    .shift-group-header { background-color: #e0f2fe; font-weight: 700; font-size: 12px; color: #0369a1; text-align: left; padding: 6px 10px; border: 1px solid #bae6fd; }
    .role-row-header { background-color: #ffffff; font-weight: 600; font-size: 12px; text-align: left; padding: 6px 6px 6px 20px; color: #374151; border: 1px solid #e5e7eb; }
    .pos-cell { font-weight: 700; font-size: 11px; text-align: center; padding: 6px 4px; border: 1px solid #e5e7eb; border-radius: 3px; }

    /* Tarjetas de diseño para la Vista Móvil */
    .mobile-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #1a73e8;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .mobile-card-title { font-weight: 700; font-size: 14px; color: #111827; }
    .mobile-card-role { font-weight: 600; font-size: 12px; color: #1a73e8; }
    .mobile-card-detail { font-size: 12px; color: #4b5563; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUPABASE CONNECTION SETUP
# ==========================================
try:
    raw_url = st.secrets["SUPABASE_URL"].strip()
    if "/rest/v1" in raw_url:
        raw_url = raw_url.split("/rest/v1")[0]
    
    SUPABASE_URL = raw_url.rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("### 🔌 Error de Configuración de Supabase")
    st.info("Verifica que las variables SUPABASE_URL y SUPABASE_KEY estén bien escritas en Secrets.")
    st.stop()

# ==========================================
# HELPER: CÁLCULO DE FECHAS DE SEMANAS (2026)
# ==========================================
def obtener_rango_fechas_semana(num_semana, ao=2026):
    primera_fecha = datetime.date(ao, 1, 1)
    dias_hasta_domingo = (6 - primera_fecha.weekday()) % 7
    primer_domingo = primera_fecha + datetime.timedelta(days=dias_hasta_domingo)
    
    inicio_semana = primer_domingo + datetime.timedelta(weeks=num_semana - 1)
    fin_semana = inicio_semana + datetime.timedelta(days=6)
    
    return f"Week {num_semana} ({inicio_semana.strftime('%b %d')} - {fin_semana.strftime('%b %d')})"

lista_semanas_2026 = [obtener_rango_fechas_semana(i) for i in range(1, 53)]

# ==========================================
# BACKEND SUPABASE PERSISTENCE FUNCTIONS
# ==========================================
def cargar_personal_desde_supabase():
    try:
        response = supabase.table("directorio_personal").select("employee_number, name, lastname, role, phone, email").execute()
        df = pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error cargando directorio de personal: {e}")
        return []
    
    if df.empty:
        personal_semilla = [
            {"employee_number": "10243", "name": "Barry", "lastname": "Tucker", "role": "Pool Supervisor", "phone": "305-555-0192", "email": "btucker@miamigov.com"},
            {"employee_number": "10244", "name": "Romina", "lastname": "Berdun", "role": "Aquatic Specialist", "phone": "305-555-0143", "email": "rberdun@miamigov.com"},
            {"employee_number": "44321", "name": "Rocco", "lastname": "Moreno", "role": "Lifeguard II", "phone": "305-555-0111", "email": "rmoreno@miamigov.com"},
            {"employee_number": "55432", "name": "Frank", "lastname": "Fernandez", "role": "Lifeguard II", "phone": "305-555-0122", "email": "ffernandez@miamigov.com"},
            {"employee_number": "88765", "name": "Rafael", "lastname": "Rodriguez", "role": "Lifeguard II", "phone": "305-555-0155", "email": "rrodriguez@miamigov.com"},
            {"employee_number": "99876", "name": "Noam", "lastname": "Reeve", "role": "Seasonal Lifeguard II", "phone": "305-555-0177", "email": "nreeve@miamigov.com"},
            {"employee_number": "22334", "name": "Daymi", "lastname": "Gonzalez", "role": "WSI", "phone": "305-555-0188", "email": "dgonzalez@miamigov.com"},
            {"employee_number": "33445", "name": "Kevin", "lastname": "Antia", "role": "WSI", "phone": "305-555-0199", "email": "kantia@miamigov.com"},
            {"employee_number": "55667", "name": "Stephanie", "lastname": "Kleiban", "role": "WSI", "phone": "305-555-0133", "email": "skleiban@miamigov.com"},
            {"employee_number": "77889", "name": "Miles", "lastname": "Rover", "role": "WSI", "phone": "305-555-0166", "email": "mrover@miamigov.com"},
            {"employee_number": "11223", "name": "Ashley", "lastname": "Valle", "role": "LG1", "phone": "305-555-0211", "email": "avalle@miamigov.com"},
            {"employee_number": "99112", "name": "Adrianna", "lastname": "Crivelli", "role": "Collection Clerk", "phone": "305-555-0222", "email": "acrivelli@miamigov.com"},
        ]
        try:
            for p in personal_semilla:
                supabase.table("directorio_personal").insert(p).execute()
        except: pass
        return personal_semilla
    return df.to_dict(orient='records')

def guardar_guardia_en_supabase(g):
    try:
        supabase.table("directorio_personal").insert(g).execute()
        return True
    except: return False

def callback_guardar_nuevo_guardia():
    val_name = st.session_state.get("input_new_name", "").strip()
    val_last = st.session_state.get("input_new_last", "").strip()
    val_role = st.session_state.get("input_new_role", "Lifeguard II")
    
    if val_name and val_last and val_role:
        full_key = f"{val_name} {val_last}"
        if 'empleados' not in st.session_state: st.session_state.empleados = []
        existe_duplicado = any(e['name'].strip().lower() == val_name.lower() and e['lastname'].strip().lower() == val_last.lower() for e in st.session_state.empleados)
        if existe_duplicado:
            st.session_state["mensaje_error_crud"] = f"❌ Error: El empleado '{full_key}' ya existe."
            return
        val_num = st.session_state.get("input_new_num", "").strip() or f"TEMP-{random.randint(10000, 99999)}"
        nuevo_guard = {"employee_number": val_num, "name": val_name, "lastname": val_last, "role": val_role, "phone": "", "email": ""}
        st.session_state.empleados.append(nuevo_guard)
        st.session_state.matriz_horario[full_key] = {d: {"rotation": "OFF", "hours": "", "location": "Shenandoah"} for d in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
        guardar_guardia_en_supabase(nuevo_guard)
        st.session_state["input_new_name"] = ""
        st.session_state["input_new_last"] = ""
        st.session_state["input_new_num"] = ""

# ==========================================
# STATE INITIALIZATION
# ==========================================
if 'empleados' not in st.session_state: st.session_state.empleados = cargar_personal_desde_supabase()
if 'matriz_horario' not in st.session_state: st.session_state.matriz_horario = {}

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
rotations = ["AM Rotation", "PM Rotation", "Noon Rotation", "All Day", "APP LWOP"]
locations = ["Grapeland", "Miller", "Shenandoah", "Gibson", "Range", "Jose Marti", "Curtis", "Manolo Reyes", "Virrick", "Williams"]
horas_validadas = ["05:00 AM", "05:30 AM", "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM", "09:30 PM", "10:00 PM"]

if "edit_target_emp" not in st.session_state: st.session_state.edit_target_emp = None
if "edit_target_day" not in st.session_state: st.session_state.edit_target_day = "Sunday"
if "show_editor" not in st.session_state: st.session_state.show_editor = False

# ==========================================
# SIDEBAR: ADMINISTRATION PANEL
# ==========================================
st.sidebar.header("📋 Administration Panel")

# CONMUTADOR DE VISTA RESPONSIVE
vista_modo = st.sidebar.radio("📱 Display Mode / Modo de Vista", ["🖥️ Desktop Grid", "📱 Mobile Cards"], index=0)

# CALLBACK AL CAMBIAR LA SEMANA
def callback_cambio_semana_activa():
    semana_sel = st.session_state.selector_semana_global
    try:
        response = supabase.table("asignaciones").select("empleado, dia, rotation, hours, location").eq("semana", semana_sel).execute()
        rows = response.data
    except Exception:
        rows = []
    
    st.session_state.matriz_horario = {}
    for emp in st.session_state.empleados:
        f_id = f"{emp['name']} {emp['lastname']}"
        st.session_state.matriz_horario[f_id] = {day: {"rotation": "OFF", "hours": "", "location": "Shenandoah"} for day in days}
        
    for r in rows:
        emp_name = r["empleado"]
        d_name = r["dia"]
        if emp_name in st.session_state.matriz_horario:
            st.session_state.matriz_horario[emp_name][d_name] = {"rotation": r["rotation"], "hours": r["hours"], "location": r["location"]}

semana_activa = st.sidebar.selectbox("Active Schedule Week", lista_semanas_2026, index=25, key="selector_semana_global", on_change=callback_cambio_semana_activa)

if not st.session_state.matriz_horario:
    callback_cambio_semana_activa()

# 1. Personnel CRUD Management
with st.sidebar.expander("👤 1. Manage Staff Members (CRUD)", expanded=False):
    crud_mode = st.radio("Action", ["Add New"], horizontal=True)
    if crud_mode == "Add New":
        st.text_input("First Name *", key="input_new_name")
        st.text_input("Last Name *", key="input_new_last")
        st.selectbox("Official Role *", ["Pool Supervisor", "Aquatic Specialist", "Lifeguard II", "Seasonal Lifeguard II", "WSI", "LG1", "Collection Clerk"], key="input_new_role")
        st.button("💾 Save New Guard", on_click=callback_guardar_nuevo_guardia)

# 2. Database History Menu
with st.sidebar.expander("🗄️ 2. Database History Menu", expanded=False):
    if st.button("💾 Save Active Week to Supabase"):
        try:
            supabase.table("asignaciones").delete().eq("semana", semana_activa).execute()
            bulk_inserts = []
            for emp in st.session_state.empleados:
                f_id = f"{emp['name']} {emp['lastname']}"
                for day in days:
                    c = st.session_state.matriz_horario[f_id][day]
                    bulk_inserts.append({
                        "semana": semana_activa, "empleado": f_id, "rol": emp["role"],
                        "dia": day, "rotation": c["rotation"], "hours": c["hours"], "location": c["location"]
                    })
            if bulk_inserts:
                supabase.table("asignaciones").insert(bulk_inserts).execute()
            st.success("Archived in Supabase cloud!")
        except Exception as e:
            st.error(f"Cloud Save Error: {e}")

    st.write("---")
    try:
        response_dist = supabase.table("asignaciones").select("semana").execute()
        df_semanas = pd.DataFrame(response_dist.data)
        
        if not df_semanas.empty:
            lista_semanas_db = df_semanas["semana"].unique().tolist()
            semana_consultar = st.selectbox("Select Saved Week to Load", lista_semanas_db, key="historial_dropdown_weeks")
            if st.button("📂 Return / Load Selected Week"):
                response_week = supabase.table("asignaciones").select("empleado, dia, rotation, hours, location").eq("semana", semana_consultar).execute()
                for r in response_week.data:
                    emp_name = r["empleado"]
                    d_name = r["dia"]
                    if emp_name in st.session_state.matriz_horario:
                        st.session_state.matriz_horario[emp_name][d_name] = {"rotation": r["rotation"], "hours": r["hours"], "location": r["location"]}
                st.success("Week loaded successfully!")
                st.rerun()
        else:
            st.info("No saved weeks found in cloud database yet.")
    except Exception: pass

# 3. Individual Shift Management
if st.session_state.show_editor and st.session_state.edit_target_emp:
    with st.sidebar.expander("⏳ 3. Assign / Edit Individual Shift", expanded=True):
        current_staff_keys = [f"{e['name']} {e['lastname']}" for e in st.session_state.empleados]
        default_emp_idx = current_staff_keys.index(st.session_state.edit_target_emp) if st.session_state.edit_target_emp in current_staff_keys else 0
        selected_emp = st.selectbox("Select Staff Member", current_staff_keys, index=default_emp_idx)
        selected_day = st.selectbox("Select Day", days, index=days.index(st.session_state.edit_target_day))
        
        current_data = st.session_state.matriz_horario[selected_emp][selected_day]
        selected_rot = st.selectbox("Shift / Rotation Label", rotations, index=rotations.index(current_data['rotation']) if current_data['rotation'] in rotations else 0)
        
        col_start, col_end = st.columns(2)
        with col_start: start_time = st.selectbox("Start Time", horas_validadas, index=12)
        with col_end: end_time = st.selectbox("End Time", horas_validadas, index=29)
        selected_loc = st.selectbox("Individual Location", locations, index=locations.index(current_data['location']) if current_data['location'] in locations else 2)
        
        mark_off = st.checkbox("Mark Employee as OFF Duty / LWOP", value=False)

        col_save, col_close = st.columns(2)
        with col_save:
            if st.button("📌 Apply Shift"):
                if mark_off: 
                    st.session_state.matriz_horario[selected_emp][selected_day] = {"rotation": "OFF", "hours": "", "location": selected_loc}
                else: 
                    st.session_state.matriz_horario[selected_emp][selected_day] = {"rotation": selected_rot, "hours": f"{start_time} - {end_time}", "location": selected_loc}
                st.success("Updated!")
                st.rerun()
        with col_close:
            if st.button("🔒 Close Editor"):
                st.session_state.show_editor = False
                st.rerun()

# 4. Staff Count Metrics
columnas_reporte = ["AM Rotation", "PM Rotation", "Noon Rotation", "All Day", "APP LWOP", "OFF"]
with st.sidebar.expander("📊 4. Staff Count Metrics", expanded=False):
    metric_day = st.selectbox("View Metrics For Day:", days)
    roles_sistema = ["Pool Supervisor", "Aquatic Specialist", "Lifeguard II", "Seasonal Lifeguard II", "WSI", "LG1", "Collection Clerk"]
    matrix_metrics = {role: {col: 0 for col in columnas_reporte} for role in roles_sistema}
    for emp in st.session_state.empleados:
        f_id = f"{emp['name']} {emp['lastname']}"
        role = emp["role"]
        if f_id in st.session_state.matriz_horario:
            status_rotation = st.session_state.matriz_horario[f_id][metric_day]["rotation"]
            if status_rotation in matrix_metrics[role]: matrix_metrics[role][status_rotation] += 1
            else: matrix_metrics[role]["OFF"] += 1
    df_metrics_detailed = pd.DataFrame.from_dict(matrix_metrics, orient='index')
    df_totales_metrics = df_metrics_detailed.sum(axis=0).to_frame().T
    df_totales_metrics.index = ["TOTAL STAFF"]
    st.dataframe(pd.concat([df_metrics_detailed, df_totales_metrics]), use_container_width=True)

# ==========================================
# TIME UTILITIES & SHIFT MATH ENGINE
# ==========================================
def calcular_delta_horas_exactas(rotacion_label, string_rango):
    if rotacion_label in ["OFF", "APP LWOP"] or not string_rango or "-" not in string_rango: return 0.0
    try:
        parts = string_rango.split("-")
        min_inicio = datetime.datetime.strptime(parts[0].strip(), "%I:%M %p").hour * 60 + datetime.datetime.strptime(parts[0].strip(), "%I:%M %p").minute
        min_fin = datetime.datetime.strptime(parts[1].strip(), "%I:%M %p").hour * 60 + datetime.datetime.strptime(parts[1].strip(), "%I:%M %p").minute
        horas_brutas = (min_fin - min_inicio) / 60.0 if min_fin > min_inicio else ((1440 - min_inicio) + min_fin) / 60.0
        return horas_brutas - 1.0 if horas_brutas > 6.0 else horas_brutas
    except Exception: return 0.0

def calcular_cobertura_real_por_horas(target_day):
    es_wknd = target_day in ["Sunday", "Saturday"]
    if es_wknd: estructura = {"All Day": {"req": {"LG1": 8, "WSI": 0, "Lifeguard II": 1}, "act": {"LG1": 0, "WSI": 0, "Lifeguard II": 0}, "limits": (510, 1050)}}
    else: estructura = {
        "AM Rotation": {"req": {"LG1": 4, "WSI": 3, "Lifeguard II": 1}, "act": {"LG1": 0, "WSI": 0, "Lifeguard II": 0}, "limits": (360, 720)},
        "Noon Rotation": {"req": {"LG1": 3, "WSI": 0, "Lifeguard II": 1}, "act": {"LG1": 0, "WSI": 0, "Lifeguard II": 0}, "limits": (720, 930)},
        "PM Rotation": {"req": {"LG1": 5, "WSI": 3, "Lifeguard II": 1}, "act": {"LG1": 0, "WSI": 0, "Lifeguard II": 0}, "limits": (930, 1290)}
    }
    for emp in st.session_state.empleados:
        f_id = f"{emp['name']} {emp['lastname']}"
        role_raw = emp["role"]
        rol_key = "LG1" if role_raw == "LG1" else "WSI" if role_raw == "WSI" else "Lifeguard II" if role_raw in ["Lifeguard II", "Seasonal Lifeguard II"] else None
        if rol_key and f_id in st.session_state.matriz_horario:
            cell = st.session_state.matriz_horario[f_id][target_day]
            if cell["rotation"] not in ["OFF", "APP LWOP"] and "-" in cell["hours"]:
                start_min = datetime.datetime.strptime(cell["hours"].split("-")[0].strip(), "%I:%M %p").hour * 60 + datetime.datetime.strptime(cell["hours"].split("-")[0].strip(), "%I:%M %p").minute
                end_min = datetime.datetime.strptime(cell["hours"].split("-")[1].strip(), "%I:%M %p").hour * 60 + datetime.datetime.strptime(cell["hours"].split("-")[1].strip(), "%I:%M %p").minute
                for t_name, t_data in estructura.items():
                    if start_min < t_data["limits"][1] and end_min > t_data["limits"][0]: t_data["act"][rol_key] += 1
    return estructura

cobertura_horaria_semanal = {day: calcular_cobertura_real_por_horas(day) for day in days}

prioridad_roles = {"Pool Supervisor": 1, "Aquatic Specialist": 2, "Lifeguard II": 3, "Seasonal Lifeguard II": 4, "WSI": 5, "LG1": 6, "Collection Clerk": 7}
empleados_ordenados = sorted(st.session_state.empleados, key=lambda x: prioridad_roles.get(x["role"], 99))

# ==========================================
# MODO DE VISTA 1: DESKTOP GRID (MATRIZ DE ESCRITORIO)
# ==========================================
if vista_modo == "🖥️ Desktop Grid":
    st.markdown(f"### 📅 Master Staff Schedule — {semana_activa}")

    row_cols_layout = [1.8, 1.5, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.0]
    cols_header = st.columns(row_cols_layout)

    cols_header[0].markdown("<span class='header-text-left'>Role Hierarchy</span>", unsafe_allow_html=True)
    cols_header[1].markdown("<span class='header-text-left'>Full Name</span>", unsafe_allow_html=True)

    for i, day in enumerate(days): 
        cols_header[i+2].markdown(f"<span class='header-text'>{day[:3]}</span>", unsafe_allow_html=True)

    cols_header[9].markdown("<span class='header-text'>Total</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 6px 0 14px 0; border-color:#e5e7eb;'>", unsafe_allow_html=True)

    totales_por_dia = {day: 0 for day in days}
    gran_total_horas = 0.0

    for idx_emp, emp in enumerate(empleados_ordenados):
        f_id = f"{emp['name']} {emp['lastname']}"
        if f_id in st.session_state.matriz_horario:
            row_cols = st.columns(row_cols_layout)
            
            row_cols[0].markdown(f"<span class='role-text'>{emp['role']}</span>", unsafe_allow_html=True)
            row_cols[1].markdown(f"<span class='name-text'>{f_id}</span>", unsafe_allow_html=True)
            
            tot_horas_empleado = 0.0
            for i_day, day in enumerate(days):
                cell = st.session_state.matriz_horario[f_id][day]
                horas_dia = calcular_delta_horas_exactas(cell["rotation"], cell["hours"])
                
                if cell["rotation"] == "OFF": 
                    btn_label = "OFF"
                elif cell["rotation"] == "APP LWOP": 
                    btn_label = ":red[APP LWOP]"
                else:
                    btn_label = (
                        f":green[{cell['rotation']}]\n"
                        f":blue[{cell['hours']}]\n"
                        f":orange[@{cell['location']}]\n"
                        f"{horas_dia:g} Hrs"
                    )
                    tot_horas_empleado += horas_dia
                    totales_por_dia[day] += 1
                
                if row_cols[i_day+2].button(btn_label, key=f"cell_dt_{idx_emp}_{i_day}", use_container_width=True):
                    st.session_state.edit_target_emp = f_id
                    st.session_state.edit_target_day = day
                    st.session_state.show_editor = True
                    st.rerun()
                    
            row_cols[9].markdown(f"<span class='header-text' style='margin-top:6px;'>{tot_horas_empleado:g} Hrs</span>", unsafe_allow_html=True)
            gran_total_horas += tot_horas_empleado

    st.markdown("<hr style='margin: 10px 0 6px 0; border-color:#e5e7eb;'>", unsafe_allow_html=True)

    row_totals = st.columns(row_cols_layout)
    row_totals[1].markdown("<span class='header-text-left'>Total Active Staff:</span>", unsafe_allow_html=True)

    for i_day, day in enumerate(days): 
        row_totals[i_day+2].markdown(f"<span class='header-text'>{totales_por_dia[day]} Guards</span>", unsafe_allow_html=True)

    row_totals[9].markdown(f"<span class='header-text'>{gran_total_horas:g} Hrs</span>", unsafe_allow_html=True)

# ==========================================
# MODO DE VISTA 2: MOBILE CARDS (VISTA TÁCTIL MÓVIL)
# ==========================================
else:
    st.markdown(f"### 📱 Mobile Daily Schedule — {semana_activa}")
    
    # Filtro rápido de día para teléfonos móviles
    selected_mobile_day = st.radio("Select Day / Seleccionar Día", days, horizontal=True)
    st.write("---")
    
    activos_hoy = 0
    horas_hoy = 0.0
    
    for idx_emp, emp in enumerate(empleados_ordenados):
        f_id = f"{emp['name']} {emp['lastname']}"
        if f_id in st.session_state.matriz_horario:
            cell = st.session_state.matriz_horario[f_id][selected_mobile_day]
            horas_dia = calcular_delta_horas_exactas(cell["rotation"], cell["hours"])
            
            with st.container():
                col_info, col_action = st.columns([2.5, 1.2])
                
                with col_info:
                    st.markdown(f"""
                    <div class="mobile-card">
                        <div class="mobile-card-title">{f_id}</div>
                        <div class="mobile-card-role">{emp['role']}</div>
                        <div class="mobile-card-detail">
                            <b>Status:</b> {cell['rotation']}<br>
                            <b>Hours:</b> {cell['hours'] if cell['hours'] else 'N/A'} ({horas_dia:g} Hrs)<br>
                            <b>Location:</b> @{cell['location']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_action:
                    st.write("")
                    btn_mobile_label = "✏️ Edit Shift" if cell["rotation"] != "OFF" else "➕ Assign"
                    if st.button(btn_mobile_label, key=f"cell_mb_{idx_emp}_{selected_mobile_day}", use_container_width=True):
                        st.session_state.edit_target_emp = f_id
                        st.session_state.edit_target_day = selected_mobile_day
                        st.session_state.show_editor = True
                        st.rerun()
            
            if cell["rotation"] not in ["OFF", "APP LWOP"]:
                activos_hoy += 1
                horas_hoy += horas_dia

    st.info(f"📊 **Summary for {selected_mobile_day}:** {activos_hoy} Active Staff On Duty | {horas_hoy:g} Total Scheduled Hours")

# ==========================================
# SECCIÓN: MATRIZ DE ALARMAS POSICIONALES (AMBAS VISTAS)
# ==========================================
st.markdown("<div class='matrix-title'>📋 LIVE SHIFT POSITIONAL ALERTS (ROLE & ROTATION CHECKS)</div>", unsafe_allow_html=True)

turnos_orden = ["AM Rotation", "Noon Rotation", "PM Rotation", "All Day"]
roles_criticos = ["LG1", "WSI", "Lifeguard II"]

for turno in turnos_orden:
    cols_turno = st.columns([4.0] + [1.3] * 7 + [1.0])
    cols_turno[0].markdown(f"<div class='shift-group-header'>⏳ {turno.upper()}</div>", unsafe_allow_html=True)
    for i_day, day in enumerate(days):
        datos_dia = cobertura_horaria_semanal[day]
        if turno in datos_dia: cols_turno[i_day+1].markdown("<div style='background-color:#e0f2fe; font-size:11px; font-weight:bold; color:#0369a1; text-align:center; padding:6px 0; border:1px solid #bae6fd;'>Active</div>", unsafe_allow_html=True)
        else: cols_turno[i_day+1].markdown("<div style='background-color:#f8f9fa; color:#cbd5e1; font-size:11px; font-style:italic; text-align:center; padding:6px 0; border:1px solid #e5e7eb;'>N/A</div>", unsafe_allow_html=True)
    
    for rol in roles_criticos:
        cols_rol = st.columns([4.0] + [1.3] * 7 + [1.0])
        cols_rol[0].markdown(f"<div class='role-row-header'>• {rol} <span style='font-size:11px; color:#6b7280;'>[Act / Min]</span></div>", unsafe_allow_html=True)
        for i_day, day in enumerate(days):
            datos_dia = cobertura_horaria_semanal[day]
            if turno not in datos_dia:
                cols_rol[i_day+1].markdown("<div class='pos-cell' style='background:#f8f9fa; color:#e2e8f0;'>—</div>", unsafe_allow_html=True)
                continue
            info_turno = datos_dia[turno]
            if rol not in info_turno["req"] or (info_turno["req"][rol] == 0 and info_turno["act"][rol] == 0):
                cols_rol[i_day+1].markdown("<div class='pos-cell' style='background:#ffffff; color:#9ca3af;'>0 / 0</div>", unsafe_allow_html=True)
                continue
            act, req = info_turno["act"][rol], info_turno["req"][rol]
            
            if act < req: color_bg, color_txt, label = "#fef2f2", "#dc2626", f"🔴 {act}/{req} Deficit"
            elif act == req: color_bg, color_txt, label = "#fefce8", "#ca8a04", f"🟡 {act}/{req} Limit"
            else: color_bg, color_txt, label = "#f0fdf4", "#16a34a", f"🟢 {act}/{req} Surplus"
            
            cols_rol[i_day+1].markdown(f"<div class='pos-cell' style='background-color:{color_bg}; color:{color_txt};'>{label}</div>", unsafe_allow_html=True)

# ==========================================
# CONVERTIDOR DE MATRIZ A CSV
# ==========================================
csv_rows = [["Employee ID", "Official Role", "Full Name", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Total Weekly Hours"]]
for emp in empleados_ordenados:
    f_id = f"{emp['name']} {emp['lastname']}"
    if f_id in st.session_state.matriz_horario:
        row_data = [emp["employee_number"], emp["role"], f_id]
        tot_horas_empleado = 0.0
        for day in days:
            cell = st.session_state.matriz_horario[f_id][day]
            if cell["rotation"] in ["OFF", "APP LWOP"]: row_data.append(cell["rotation"])
            else:
                horas_dia = calcular_delta_horas_exactas(cell["rotation"], cell["hours"])
                tot_horas_empleado += horas_dia
                row_data.append(f"{cell['rotation']} ({cell['hours']}) @ {cell['location']} [{horas_dia:g} Hrs]")
        row_data.append(f"{tot_horas_empleado:g}")
        csv_rows.append(row_data)

df_export = pd.DataFrame(csv_rows[1:], columns=csv_rows[0])
csv_buffer = df_export.to_csv(index=False).encode('utf-8-sig')

st.write("")
st.download_button(label="📥 DOWNLOAD WEEKLY MATRIX (CSV FOR EXCEL)", data=csv_buffer, file_name=f"Schedule_{semana_activa.split(' ')[0]}_{semana_activa.split(' ')[1]}.csv", mime="text/csv")
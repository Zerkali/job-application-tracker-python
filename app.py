from datetime import date
import pandas as pd
import streamlit as st
import database as db

st.set_page_config(page_title='Job Application Tracker', page_icon='📋', layout='wide')
db.init_db()
st.title('Job Application Tracker')

if 'user_id' not in st.session_state:
    login_tab, register_tab = st.tabs(['Anmelden', 'Registrieren'])
    with login_tab:
        with st.form('login'):
            name = st.text_input('Benutzername')
            password = st.text_input('Passwort', type='password')
            if st.form_submit_button('Anmelden'):
                uid = db.login(name, password)
                if uid is None:
                    st.error('Ungültige Zugangsdaten.')
                else:
                    st.session_state.user_id = uid
                    st.rerun()
    with register_tab:
        with st.form('register'):
            name = st.text_input('Neuer Benutzername')
            password = st.text_input('Neues Passwort (mind. 8 Zeichen)', type='password')
            if st.form_submit_button('Registrieren'):
                try:
                    if db.register(name, password):
                        st.success('Konto erstellt. Bitte anmelden.')
                    else:
                        st.error('Benutzername bereits vergeben.')
                except ValueError as exc:
                    st.error(str(exc))
    st.stop()

uid = st.session_state.user_id
if st.sidebar.button('Abmelden'):
    del st.session_state.user_id
    st.rerun()
page = st.sidebar.radio('Navigation', ['Dashboard', 'Neue Bewerbung', 'Bewerbungen'])
rows = db.list_applications(uid)
columns = ['id','company','position','applied_on','status','notes']
frame = pd.DataFrame(rows, columns=columns)

def fields(item=None):
    item = item or {}
    company = st.text_input('Unternehmen', value=item.get('company',''))
    position = st.text_input('Stelle', value=item.get('position',''))
    applied = st.date_input('Datum', value=date.fromisoformat(item['applied_on']) if item else date.today())
    status = st.selectbox('Status', db.STATUSES, index=db.STATUSES.index(item.get('status','Offen')))
    notes = st.text_area('Notizen', value=item.get('notes',''))
    return company, position, applied, status, notes

if page == 'Dashboard':
    st.header('Übersicht')
    cols = st.columns(4)
    for col, label, count in zip(cols, ['Gesamt','Vorstellungsgespräche','Zusagen','Absagen'],
                                [len(frame), *(int((frame.status == s).sum()) for s in ['Vorstellungsgespräch','Zusage','Absage'])]):
        col.metric(label, count)
    if not frame.empty:
        st.subheader('Bewerbungen nach Status')
        st.bar_chart(frame.status.value_counts().reindex(db.STATUSES, fill_value=0))
        st.subheader('Bewerbungen pro Monat')
        st.line_chart(frame.groupby(frame.applied_on.str[:7]).size())
    else:
        st.info('Noch keine Bewerbungen vorhanden.')
elif page == 'Neue Bewerbung':
    st.header('Bewerbung hinzufügen')
    with st.form('add', clear_on_submit=True):
        values = fields()
        if st.form_submit_button('Speichern'):
            try:
                db.add_application(uid, *values)
                st.success('Bewerbung gespeichert.')
            except ValueError as exc:
                st.error(str(exc))
else:
    st.header('Meine Bewerbungen')
    query = st.text_input('Suche nach Unternehmen oder Stelle')
    statuses = st.multiselect('Status filtern', db.STATUSES)
    filtered = frame[frame.company.str.contains(query, case=False, regex=False) | frame.position.str.contains(query, case=False, regex=False)] if rows else frame
    if statuses:
        filtered = filtered[filtered.status.isin(statuses)]
    display = filtered.drop(columns='id').rename(columns={'company':'Unternehmen','position':'Stelle','applied_on':'Datum','status':'Status','notes':'Notizen'})
    st.dataframe(display, hide_index=True, use_container_width=True)
    # Prevent spreadsheet formula injection in exported text fields.
    safe = display.copy()
    for column in safe.columns:
        safe[column] = safe[column].map(lambda x: "'" + x if isinstance(x,str) and x.lstrip().startswith(('=','+','-','@')) else x)
    st.download_button('CSV herunterladen', safe.to_csv(index=False).encode('utf-8-sig'), 'bewerbungen.csv', 'text/csv')
    if not filtered.empty:
        selected = st.selectbox('Bewerbung auswählen', filtered.id.tolist(), format_func=lambda x: next(f"{r['company']} – {r['position']} (#{x})" for r in rows if r['id']==x))
        item = next(r for r in rows if r['id']==selected)
        with st.form(f'edit_{selected}'):
            values = fields(item)
            if st.form_submit_button('Änderungen speichern'):
                try:
                    db.update_application(uid, selected, *values)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        if st.checkbox('Löschen bestätigen', key=f'confirm_{selected}'):
            if st.button('Bewerbung löschen'):
                db.delete_application(uid, selected)
                st.rerun()

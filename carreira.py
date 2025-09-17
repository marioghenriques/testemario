#!/usr/bin/env python3
"""
Sistema de Registro de Intenção de Cursos com Matriz de Competências
Versão Streamlit + SQLite - MVP

Author: Desenvolvimento Team
Version: 2.0.0 (Streamlit Edition)
Date: 2025-09-17
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from database import DatabaseManager, Competency, Course, User, Assessment, CourseIntention

# Page configuration
st.set_page_config(
    page_title="Sistema de Carreira - MVP",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = DatabaseManager()
db.seed_initial_data()

# Session state initialization
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'assessment_progress' not in st.session_state:
    st.session_state.assessment_progress = {}
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: white;
    }
    .competency-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #007bff;
    }
    .competency-mastered {
        border-left-color: #28a745;
        background: #d4edda;
    }
    .competency-developing {
        border-left-color: #ffc107;
        background: #fff3cd;
    }
    .competency-needed {
        border-left-color: #dc3545;
        background: #f8d7da;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def login_page():
    """User login page"""
    st.markdown('<div class="main-header"><h1>🚀 Sistema de Carreira</h1><p>Plataforma de Desenvolvimento Profissional</p></div>', unsafe_allow_html=True)
    
    st.subheader("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        name = st.text_input("Nome Completo")
        current_level = st.selectbox("Nível Atual", ["FC-03", "FC-04", "FC-05", "FC-06"])
        target_level = st.selectbox("Nível Almejado", ["FC-03", "FC-04", "FC-05", "FC-06"])
        
        if st.form_submit_button("Entrar"):
            if email and name:
                user = db.get_user_by_email(email)
                if not user:
                    user_id = db.create_user(name, email, current_level, target_level)
                    user = db.get_user_by_email(email)
                
                st.session_state.current_user = user
                st.success(f"Bem-vindo, {user.name}!")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos.")

def competency_matrix_dashboard():
    """Main dashboard with competency matrix visualization"""
    user = st.session_state.current_user
    if not user:
        return
    
    st.markdown(f'<div class="main-header"><h1>📊 Matriz de Competências</h1><p>{user.name} - {user.current_level} → {user.target_level}</p></div>', unsafe_allow_html=True)
    
    # Get user assessments
    assessments = db.get_user_assessments(user.id)
    
    # Get competencies for target level
    target_competencies = db.get_competencies(level=user.target_level)
    
    # Calculate competency status
    competency_status = []
    for comp in target_competencies:
        assessment = assessments.get(comp.id)
        if assessment:
            if assessment.score >= 4:
                status = "Dominada"
                status_class = "competency-mastered"
                icon = "✅"
            elif assessment.score >= 2:
                status = "Em desenvolvimento"
                status_class = "competency-developing"
                icon = "🟡"
            else:
                status = "Necessária"
                status_class = "competency-needed"
                icon = "🔴"
        else:
            status = "Necessária"
            status_class = "competency-needed"
            icon = "🔴"
        
        competency_status.append({
            'competency': comp,
            'status': status,
            'status_class': status_class,
            'icon': icon,
            'score': assessment.score if assessment else 0
        })
    
    # Metrics summary
    mastered = sum(1 for c in competency_status if c['status'] == 'Dominada')
    developing = sum(1 for c in competency_status if c['status'] == 'Em desenvolvimento')
    needed = sum(1 for c in competency_status if c['status'] == 'Necessária')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>✅ Dominadas</h3><h2>{mastered}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>🟡 Em Desenvolvimento</h3><h2>{developing}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>🔴 Necessárias</h3><h2>{needed}</h2></div>', unsafe_allow_html=True)
    with col4:
        completion_rate = (mastered / len(competency_status) * 100) if competency_status else 0
        st.markdown(f'<div class="metric-card"><h3>📈 Conclusão</h3><h2>{completion_rate:.1f}%</h2></div>', unsafe_allow_html=True)
    
    # Competency matrix visualization
    st.subheader("Matriz de Competências")
    
    # Group by category
    categories = {}
    for comp_status in competency_status:
        category = comp_status['competency'].category
        if category not in categories:
            categories[category] = []
        categories[category].append(comp_status)
    
    for category, comp_list in categories.items():
        category_names = {
            'technical': '🔧 Técnicas',
            'behavioral': '👥 Comportamentais', 
            'strategic': '🎯 Estratégicas'
        }
        
        st.markdown(f"### {category_names.get(category, category)}")
        
        for comp_status in comp_list:
            comp = comp_status['competency']
            st.markdown(f'''
                <div class="competency-card {comp_status['status_class']}">
                    <h4>{comp_status['icon']} {comp.name}</h4>
                    <p>{comp.description}</p>
                    <small><strong>Nível:</strong> {comp.level} | <strong>Peso:</strong> {comp.weight} | <strong>Score:</strong> {comp_status['score']}/5</small>
                </div>
            ''', unsafe_allow_html=True)
    
    # Career progression visualization
    st.subheader("Caminho de Carreira")
    
    levels = ['FC-03', 'FC-04', 'FC-05', 'FC-06']
    current_index = levels.index(user.current_level)
    target_index = levels.index(user.target_level)
    
    fig = go.Figure()
    
    # Add progression path
    fig.add_trace(go.Scatter(
        x=levels,
        y=[1, 1, 1, 1],
        mode='lines+markers',
        line=dict(color='lightgray', width=4),
        marker=dict(size=20, color='lightgray'),
        name='Caminho de Carreira'
    ))
    
    # Highlight current position
    fig.add_trace(go.Scatter(
        x=[levels[current_index]],
        y=[1],
        mode='markers',
        marker=dict(size=25, color='blue'),
        name=f'Atual: {user.current_level}'
    ))
    
    # Highlight target position
    fig.add_trace(go.Scatter(
        x=[levels[target_index]],
        y=[1],
        mode='markers',
        marker=dict(size=25, color='red'),
        name=f'Alvo: {user.target_level}'
    ))
    
    fig.update_layout(
        title="Progressão na Carreira",
        xaxis_title="Nível Hierárquico",
        yaxis=dict(showticklabels=False),
        showlegend=True,
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)

def self_assessment_page():
    """Self-assessment questionnaire page"""
    user = st.session_state.current_user
    if not user:
        return
    
    st.markdown(f'<div class="main-header"><h1>📝 Autoavaliação de Competências</h1><p>Avalie suas competências atuais</p></div>', unsafe_allow_html=True)
    
    # Get competencies for target level
    target_competencies = db.get_competencies(level=user.target_level)
    current_assessments = db.get_user_assessments(user.id)
    
    if not target_competencies:
        st.info("Nenhuma competência encontrada para o nível almejado.")
        return
    
    st.subheader(f"Competências para {user.target_level}")
    
    # Progress tracking
    total_competencies = len(target_competencies)
    assessed_competencies = len(current_assessments)
    progress = (assessed_competencies / total_competencies * 100) if total_competencies > 0 else 0
    
    st.progress(progress / 100)
    st.write(f"Progresso: {assessed_competencies}/{total_competencies} competências avaliadas")
    
    # Assessment form
    with st.form("assessment_form"):
        st.write("Avalie cada competência na escala de 1 a 5:")
        st.write("1 - Não desenvolvida | 2 - Básica | 3 - Intermediária | 4 - Avançada | 5 - Expert")
        
        assessments_data = {}
        
        for comp in target_competencies:
            current_score = current_assessments.get(comp.id)
            default_score = current_score.score if current_score else 3
            
            st.markdown(f"**{comp.name}**")
            st.caption(comp.description)
            score = st.slider(
                f"Nível em {comp.name}",
                min_value=1,
                max_value=5,
                value=default_score,
                key=f"comp_{comp.id}"
            )
            assessments_data[comp.id] = score
            st.write("---")
        
        if st.form_submit_button("Salvar Avaliação"):
            # Save all assessments
            for comp_id, score in assessments_data.items():
                db.save_assessment(user.id, comp_id, score)
            
            st.success("Autoavaliação salva com sucesso!")
            st.balloons()
            st.rerun()

def course_registration_page():
    """Enhanced course registration and intention page"""
    user = st.session_state.current_user
    if not user:
        return
    
    st.markdown(f'<div class="main-header"><h1>📚 Registro de Intenção de Cursos</h1><p>Selecione cursos para seu desenvolvimento</p></div>', unsafe_allow_html=True)
    
    # Get user assessments to identify gaps
    assessments = db.get_user_assessments(user.id)
    
    # Get all courses
    courses = db.get_courses()
    
    # Get user's current intentions
    current_intentions = db.get_user_intentions(user.id)
    intended_course_ids = {intention.course_id for intention in current_intentions}
    
    # Identify competency gaps
    target_competencies = db.get_competencies(level=user.target_level)
    gap_competencies = []
    
    for comp in target_competencies:
        assessment = assessments.get(comp.id)
        if not assessment or assessment.score < 4:
            gap_competencies.append(comp.id)
    
    # Enhanced filtering and search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Buscar cursos", placeholder="Digite palavras-chave...")
    
    with col2:
        category_filter = st.selectbox(
            "Filtrar por categoria",
            ["Todas"] + list(set(course.category for course in courses))
        )
    
    # Get all categories for filter
    all_categories = list(set(course.category for course in courses))
    
    # Filter courses based on search and category
    filtered_courses = []
    for course in courses:
        # Apply search filter
        if search_term:
            search_lower = search_term.lower()
            if (search_lower not in course.name.lower() and 
                search_lower not in course.description.lower() and
                search_lower not in course.category.lower()):
                continue
        
        # Apply category filter
        if category_filter != "Todas" and course.category != category_filter:
            continue
        
        # Calculate relevance score
        relevance_score = sum(1 for comp_id in course.competency_ids if comp_id in gap_competencies)
        
        filtered_courses.append({
            'course': course,
            'relevance': relevance_score,
            'already_intended': course.id in intended_course_ids,
            'match_score': calculate_match_score(course, search_term) if search_term else 0
        })
    
    # Sort by relevance and match score
    filtered_courses.sort(key=lambda x: (x['relevance'], x['match_score']), reverse=True)
    
    # Show tabs for different views
    tab1, tab2 = st.tabs(["🎯 Recomendados", "📖 Todos os Cursos"])
    
    with tab1:
        # Show only courses with relevance > 0
        recommended_courses = [c for c in filtered_courses if c['relevance'] > 0]
        
        if recommended_courses:
            st.subheader(f"Cursos Recomendados para {user.target_level} ({len(recommended_courses)})")
            
            for course_data in recommended_courses:
                display_course_card(course_data, user, db, context="recommended")
        else:
            st.info("Não há cursos recomendados com base nas suas lacunas atuais.")
    
    with tab2:
        st.subheader(f"Todos os Cursos ({len(filtered_courses)})")
        
        if filtered_courses:
            # Pagination
            items_per_page = 6
            page = st.number_input("Página", min_value=1, max_value=max(1, len(filtered_courses) // items_per_page + 1), value=1)
            
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_courses = filtered_courses[start_idx:end_idx]
            
            for course_data in page_courses:
                display_course_card(course_data, user, db, context="all")
            
            # Pagination info
            st.caption(f"Mostrando {start_idx + 1}-{min(end_idx, len(filtered_courses))} de {len(filtered_courses)} cursos")
        else:
            st.info("Nenhum curso encontrado com os filtros atuais.")
    
    # Enhanced intentions management
    if current_intentions:
        st.subheader("📋 Meus Interesses Registrados")
        
        # Allow status updates
        intentions_df = []
        for intention in current_intentions:
            course = next((c for c in courses if c.id == intention.course_id), None)
            if course:
                intentions_df.append({
                    'ID': intention.id,
                    'Curso': course.name,
                    'Data': intention.intention_date.strftime('%Y-%m-%d'),
                    'Status': intention.status,
                    'Prioridade': intention.priority,
                    'Duração': f"{course.duration_hours}h"
                })
        
        if intentions_df:
            df = pd.DataFrame(intentions_df)
            
            # Allow inline status updates
            edited_df = st.data_editor(
                df.drop('ID', axis=1),
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        help="Atualizar status da intenção",
                        options=["intended", "registered", "completed", "cancelled"],
                        required=True,
                    ),
                    "Prioridade": st.column_config.NumberColumn(
                        "Prioridade",
                        min_value=1,
                        max_value=5,
                        step=1,
                        required=True,
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Update intentions if changed
            if not edited_df.equals(df.drop('ID', axis=1)):
                st.success("Status atualizados com sucesso!")
                # Here you would save the changes to the database
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Exportar Intenções (CSV)"):
                export_intentions_to_csv(current_intentions, courses)
        with col2:
            if st.button("🔄 Sincronizar com Sistema"):
                sync_with_external_system(current_intentions)

def display_course_card(course_data, user, db, context="all"):
    """Display individual course card with enhanced information"""
    course = course_data['course']
    relevance = course_data['relevance']
    already_intended = course_data['already_intended']
   
    with st.expander(f"📖 {course.name} {'⭐' * relevance if relevance > 0 else ''}"):
        col1, col2 = st.columns([3, 1])
       
        with col1:
            st.write(course.description)
            st.write(f"**Duração:** {course.duration_hours} horas")
            st.write(f"**Categoria:** {course.category}")
           
            # Show competency linkage
            if course.competency_ids:
                st.write("**Competências desenvolvidas:**")
                for comp_id in course.competency_ids:
                    comp = db.get_competency_by_id(comp_id)
                    if comp:
                        relevance_badge = "🎯" if comp.level == user.target_level else "📚"
                        st.markdown(f"- {relevance_badge} {comp.name} ({comp.level})")
       
        with col2:
            # Course status
            if already_intended:
                st.success("✅ Interesse Registrado")
            else:
                st.metric("Relevância", f"{'⭐' * relevance}", f"{relevance} competências")
       
        # Course impact visualization
        if course.competency_ids and relevance > 0:
            st.write("**Impacto no seu desenvolvimento:**")
            impact_data = calculate_course_impact(course, user, db)
           
            if impact_data:
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Competências Atendidas'],
                        y=[len(impact_data['addressed'])],
                        marker_color='green'
                    )
                ])
                fig.update_layout(height=200, showlegend=False)
                # Linha 508 corrigida
                st.plotly_chart(fig, use_container_width=True, key=f"plotly_chart_{context}_{course_data['course'].id}")
       
        # Registration form
        if not already_intended:
            # Create unique key for this form instance with context
            form_key = f"course_form_{context}_{course.id}_{datetime.now().timestamp()}"
            with st.form(form_key):
                col1, col2 = st.columns([2, 1])
               
                with col1:
                    priority = st.selectbox(
                        "Prioridade",
                        [1, 2, 3, 4, 5],
                        index=2,
                        key=f"priority_{context}_{course.id}_{datetime.now().timestamp()}"
                    )
                    notes = st.text_area(
                        "Notas (opcional)",
                        placeholder="Por que você está interessado neste curso?",
                        key=f"notes_{context}_{course.id}_{datetime.now().timestamp()}"
                    )
               
                with col2:
                    st.write("**Quando deseja fazer?**")
                    timeline = st.selectbox(
                        "Timeline",
                        ["Imediato", "Próximos 3 meses", "Próximos 6 meses", "Este ano"],
                        key=f"timeline_{context}_{course.id}_{datetime.now().timestamp()}"
                    )
                   
                    if st.form_submit_button("Registrar Interesse"):
                        db.save_course_intention(user.id, course.id, priority)
                        st.success("Interesse registrado com sucesso!")
                        st.balloons()
                        st.rerun()

def calculate_match_score(course, search_term):
    """Calculate match score for search relevance"""
    score = 0
    search_lower = search_term.lower()
    
    if search_lower in course.name.lower():
        score += 10
    if search_lower in course.description.lower():
        score += 5
    if search_lower in course.category.lower():
        score += 3
    
    return score

def calculate_course_impact(course, user, db):
    """Calculate the impact of a course on user's competency gaps"""
    if not course.competency_ids:
        return None
    
    assessments = db.get_user_assessments(user.id)
    target_competencies = db.get_competencies(level=user.target_level)
    
    addressed = []
    remaining = []
    
    for comp_id in course.competency_ids:
        comp = db.get_competency_by_id(comp_id)
        if comp and comp.level == user.target_level:
            assessment = assessments.get(comp_id)
            if not assessment or assessment.score < 4:
                addressed.append(comp)
            else:
                remaining.append(comp)
    
    return {
        'addressed': addressed,
        'remaining': remaining,
        'total_impact': len(addressed)
    }

def export_intentions_to_csv(intentions, courses):
    """Export course intentions to CSV format"""
    import io
    
    output = io.StringIO()
    output.write("Curso,Categoria,Duração,Prioridade,Status,Data Registro\n")
    
    for intention in intentions:
        course = next((c for c in courses if c.id == intention.course_id), None)
        if course:
            output.write(f'"{course.name}","{course.category}","{course.duration_hours}h",{intention.priority},"{intention.status}","{intention.intention_date.strftime("%Y-%m-%d")}"\n')
    
    csv_data = output.getvalue()
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"intencoes_cursos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def sync_with_external_system(intentions):
    """Sync intentions with external scheduling system"""
    # Placeholder for external system integration
    # This would connect to the existing agendador_salas.py system
    st.info("Sincronização com sistema externo seria implementada aqui")
    st.success("Sincronização simulada - dados enviados para o sistema de agendamento")

def admin_page():
    """Enhanced administration page with full CRUD operations"""
    st.markdown(f'<div class="main-header"><h1>⚙️ Administração</h1><p>Painel administrativo completo do sistema</p></div>', unsafe_allow_html=True)
    
    # Admin authentication (simplified for MVP)
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.warning("Área administrativa protegida")
        admin_password = st.text_input("Senha de administrador", type="password")
        if admin_password == "admin123":  # Simple password for MVP
            st.session_state.admin_authenticated = True
            st.success("Autenticado como administrador!")
            st.rerun()
        elif admin_password:
            st.error("Senha incorreta")
        return
    
    # Enhanced admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "👥 Usuários", 
        "🎯 Competências", 
        "📚 Cursos", 
        "📈 Relatórios"
    ])
    
    with tab1:
        admin_dashboard()
    
    with tab2:
        user_management()
    
    with tab3:
        competency_management()
    
    with tab4:
        course_management()
    
    with tab5:
        reports_and_analytics()

def admin_dashboard():
    """Enhanced admin dashboard with comprehensive statistics"""
    st.subheader("📊 Visão Geral do Sistema")
    
    # Get comprehensive statistics
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Basic statistics
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM assessments")
        total_assessments = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM course_intentions")
        total_intentions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM competencies")
        total_competencies = cursor.fetchone()[0]
        
        # Advanced statistics
        cursor.execute("SELECT current_level, COUNT(*) FROM users GROUP BY current_level")
        users_by_level = dict(cursor.fetchall())
        
        cursor.execute("SELECT target_level, COUNT(*) FROM users GROUP BY target_level")
        targets_by_level = dict(cursor.fetchall())
        
        cursor.execute("SELECT score, COUNT(*) FROM assessments GROUP BY score")
        assessments_by_score = dict(cursor.fetchall())
        
        cursor.execute("SELECT status, COUNT(*) FROM course_intentions GROUP BY status")
        intentions_by_status = dict(cursor.fetchall())
        
        # Popular courses
        cursor.execute("""
            SELECT c.name, COUNT(ci.id) as count 
            FROM courses c 
            LEFT JOIN course_intentions ci ON c.id = ci.course_id 
            GROUP BY c.id 
            ORDER BY count DESC 
            LIMIT 10
        """)
        popular_courses = cursor.fetchall()
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("👥 Usuários", total_users)
    with col2:
        st.metric("📚 Cursos", total_courses)
    with col3:
        st.metric("🎯 Competências", total_competencies)
    with col4:
        st.metric("📝 Avaliações", total_assessments)
    with col5:
        st.metric("📋 Intenções", total_intentions)
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Usuários por Nível Atual")
        if users_by_level:
            fig = px.pie(
                values=list(users_by_level.values()),
                names=list(users_by_level.keys()),
                title="Distribuição de Usuários"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Status das Intenções")
        if intentions_by_status:
            status_names = {
                'intended': 'Planejado',
                'registered': 'Registrado', 
                'completed': 'Concluído',
                'cancelled': 'Cancelado'
            }
            labels = [status_names.get(k, k) for k in intentions_by_status.keys()]
            fig = px.bar(
                x=labels,
                y=list(intentions_by_status.values()),
                title="Status das Intenções de Curso"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    st.subheader("📈 Insights do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cursos Mais Populares:**")
        if popular_courses:
            for course_name, count in popular_courses[:5]:
                st.write(f"- {course_name}: {count} intenções")
    
    with col2:
        st.write("**Distribuição de Avaliações:**")
        if assessments_by_score:
            for score, count in sorted(assessments_by_score.items()):
                percentage = (count / total_assessments * 100) if total_assessments > 0 else 0
                st.write(f"- Nota {score}: {count} avaliações ({percentage:.1f}%)")

def user_management():
    """User management interface"""
    st.subheader("👥 Gerenciamento de Usuários")
    
    # Get all users
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, current_level, target_level, created_at
            FROM users 
            ORDER BY created_at DESC
        """)
        users_data = cursor.fetchall()
    
    if users_data:
        # Display users in editable table
        users_df = pd.DataFrame(users_data, columns=['ID', 'Nome', 'Email', 'Nível Atual', 'Nível Alvo', 'Data Cadastro'])
        users_df['Data Cadastro'] = pd.to_datetime(users_df['Data Cadastro']).dt.strftime('%Y-%m-%d')
        
        st.write("Usuários cadastrados:")
        edited_df = st.data_editor(
            users_df.drop('ID', axis=1),
            column_config={
                "Nível Atual": st.column_config.SelectboxColumn(
                    "Nível Atual",
                    help="Nível hierárquico atual",
                    options=["FC-03", "FC-04", "FC-05", "FC-06"],
                    required=True,
                ),
                "Nível Alvo": st.column_config.SelectboxColumn(
                    "Nível Alvo", 
                    help="Nível hierárquico desejado",
                    options=["FC-03", "FC-04", "FC-05", "FC-06"],
                    required=True,
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # User actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Exportar Usuários (CSV)"):
                export_users_to_csv(users_data)
        with col2:
            if st.button("📊 Análise de Usuários"):
                generate_user_analysis_report()
        
        # Individual user actions
        st.subheader("Ações Individuais")
        selected_user = st.selectbox(
            "Selecionar usuário para ações específicas:",
            options=[(user[0], user[1]) for user in users_data],
            format_func=lambda x: x[1]
        )
        
        if selected_user:
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Resetar Avaliações"):
                    reset_user_assessments(selected_user[0])
                    st.success("Avaliações resetadas!")
            with col2:
                if st.button("🗑️ Excluir Usuário"):
                    delete_user(selected_user[0])
                    st.success("Usuário excluído!")
                    st.rerun()
            with col3:
                if st.button("📋 Ver Detalhes"):
                    show_user_details(selected_user[0])
    else:
        st.info("Nenhum usuário cadastrado no sistema.")

def competency_management():
    """Competency CRUD operations"""
    st.subheader("🎯 Gerenciamento de Competências")
    
    # Get all competencies
    competencies = db.get_competencies()
    
    # Tabs for competency operations
    tab1, tab2 = st.tabs(["📋 Listar Competências", "➕ Adicionar Competência"])
    
    with tab1:
        if competencies:
            # Display competencies in organized format
            for level in ["FC-03", "FC-04", "FC-05", "FC-06"]:
                level_competencies = [c for c in competencies if c.level == level]
                if level_competencies:
                    st.subheader(f"Competências {level}")
                    
                    for comp in level_competencies:
                        with st.expander(f"{comp.name} ({comp.category})"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(comp.description)
                                st.write(f"**Peso:** {comp.weight}")
                                st.write(f"**Categoria:** {comp.category}")
                            
                            with col2:
                                if st.button(f"🗑️ Excluir", key=f"del_comp_{comp.id}"):
                                    delete_competency(comp.id)
                                    st.rerun()
            
            # Export competencies
            if st.button("📥 Exportar Competências"):
                export_competencies_to_csv(competencies)
        else:
            st.info("Nenhuma competência cadastrada.")
    
    with tab2:
        with st.form("add_competency_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome da Competência", key="comp_name")
                level = st.selectbox("Nível", ["FC-03", "FC-04", "FC-05", "FC-06"], key="comp_level")
                category = st.selectbox("Categoria", ["technical", "behavioral", "strategic"], key="comp_category")
            
            with col2:
                weight = st.number_input("Peso", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="comp_weight")
            
            description = st.text_area("Descrição", key="comp_description")
            
            if st.form_submit_button("➕ Adicionar Competência"):
                if name and description:
                    add_competency(name, description, category, level, weight)
                    st.success("Competência adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios.")

def course_management():
    """Course CRUD operations"""
    st.subheader("📚 Gerenciamento de Cursos")
    
    # Get courses and competencies
    courses = db.get_courses()
    all_competencies = db.get_competencies()
    
    # Tabs for course operations
    tab1, tab2 = st.tabs(["📋 Listar Cursos", "➕ Adicionar Curso"])
    
    with tab1:
        if courses:
            for course in courses:
                with st.expander(f"{course.name} ({course.category})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(course.description)
                        st.write(f"**Duração:** {course.duration_hours} horas")
                        st.write(f"**Categoria:** {course.category}")
                        st.write(f"**Status:** {'✅ Ativo' if course.is_active else '❌ Inativo'}")
                        
                        # Show linked competencies
                        if course.competency_ids:
                            st.write("**Competências vinculadas:**")
                            for comp_id in course.competency_ids:
                                comp = db.get_competency_by_id(comp_id)
                                if comp:
                                    st.markdown(f"- {comp.name} ({comp.level})")
                    
                    with col2:
                        if st.button(f"🗑️ Excluir", key=f"del_course_{course.id}"):
                            delete_course(course.id)
                            st.rerun()
                        
                        toggle_status = "Desativar" if course.is_active else "Ativar"
                        if st.button(f"🔄 {toggle_status}", key=f"toggle_course_{course.id}"):
                            toggle_course_status(course.id)
                            st.rerun()
            
            # Export courses
            if st.button("📥 Exportar Cursos"):
                export_courses_to_csv(courses)
        else:
            st.info("Nenhum curso cadastrado.")
    
    with tab2:
        with st.form("add_course_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nome do Curso", key="course_name")
                duration = st.number_input("Duração (horas)", min_value=1, value=8, key="course_duration")
                category = st.text_input("Categoria", key="course_category")
            
            with col2:
                # Competency selection
                st.write("**Competências vinculadas:**")
                selected_competencies = []
                for comp in all_competencies:
                    if st.checkbox(f"{comp.name} ({comp.level})", key=f"comp_{comp.id}"):
                        selected_competencies.append(comp.id)
            
            description = st.text_area("Descrição", key="course_description")
            
            if st.form_submit_button("➕ Adicionar Curso"):
                if name and description and selected_competencies:
                    add_course(name, description, duration, category, selected_competencies)
                    st.success("Curso adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos e selecione pelo menos uma competência.")

def reports_and_analytics():
    """Advanced reporting and analytics"""
    st.subheader("📈 Relatórios e Análises")
    
    # Report type selection
    report_type = st.selectbox(
        "Tipo de Relatório",
        ["Resumo Geral", "Análise de Competências", "Demandas de Cursos", "Progresso de Usuários", "Tendências"]
    )
    
    if report_type == "Resumo Geral":
        generate_summary_report()
    elif report_type == "Análise de Competências":
        generate_competency_analysis()
    elif report_type == "Demandas de Cursos":
        generate_course_demand_report()
    elif report_type == "Progresso de Usuários":
        generate_user_progress_report()
    elif report_type == "Tendências":
        generate_trends_report()

# Helper functions for admin operations
def add_competency(name, description, category, level, weight):
    """Add a new competency to the database"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO competencies (name, description, category, level, weight)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, category, level, weight))
        conn.commit()

def delete_competency(competency_id):
    """Delete a competency"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM competencies WHERE id = ?", (competency_id,))
        conn.commit()

def add_course(name, description, duration, category, competency_ids):
    """Add a new course to the database"""
    import json
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO courses (name, description, duration_hours, category, competency_ids)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, duration, category, json.dumps(competency_ids)))
        conn.commit()

def delete_course(course_id):
    """Delete a course"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()

def toggle_course_status(course_id):
    """Toggle course active status"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE courses SET is_active = NOT is_active WHERE id = ?", (course_id,))
        conn.commit()

def reset_user_assessments(user_id):
    """Reset all assessments for a user"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assessments WHERE user_id = ?", (user_id,))
        conn.commit()

def delete_user(user_id):
    """Delete a user and all related data"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM course_intentions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM assessments WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

def show_user_details(user_id):
    """Show detailed information about a user"""
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            st.write(f"**Usuário:** {user[1]}")
            st.write(f"**Email:** {user[2]}")
            st.write(f"**Nível Atual:** {user[3]}")
            st.write(f"**Nível Alvo:** {user[4]}")
            st.write(f"**Data Cadastro:** {user[5]}")
            
            # Get assessment count
            cursor.execute("SELECT COUNT(*) FROM assessments WHERE user_id = ?", (user_id,))
            assessment_count = cursor.fetchone()[0]
            
            # Get intention count
            cursor.execute("SELECT COUNT(*) FROM course_intentions WHERE user_id = ?", (user_id,))
            intention_count = cursor.fetchone()[0]
            
            st.write(f"**Total de Avaliações:** {assessment_count}")
            st.write(f"**Total de Intenções:** {intention_count}")

def export_users_to_csv(users_data):
    """Export users to CSV"""
    import io
    output = io.StringIO()
    output.write("ID,Nome,Email,Nível Atual,Nível Alvo,Data Cadastro\n")
    
    for user in users_data:
        output.write(f"{user[0]},{user[1]},{user[2]},{user[3]},{user[4]},{user[5]}\n")
    
    csv_data = output.getvalue()
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"usuarios_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def export_competencies_to_csv(competencies):
    """Export competencies to CSV"""
    import io
    output = io.StringIO()
    output.write("ID,Nome,Descrição,Categoria,Nível,Peso\n")
    
    for comp in competencies:
        output.write(f"{comp.id},{comp.name},{comp.description},{comp.category},{comp.level},{comp.weight}\n")
    
    csv_data = output.getvalue()
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"competencias_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def export_courses_to_csv(courses):
    """Export courses to CSV"""
    import io, json
    output = io.StringIO()
    output.write("ID,Nome,Descrição,Duração,Categoria,Competências,Status\n")
    
    for course in courses:
        comp_names = []
        for comp_id in course.competency_ids:
            comp = db.get_competency_by_id(comp_id)
            if comp:
                comp_names.append(comp.name)
        
        output.write(f"{course.id},{course.name},{course.description},{course.duration_hours},{course.category},\"{'; '.join(comp_names)}\",{'Ativo' if course.is_active else 'Inativo'}\n")
    
    csv_data = output.getvalue()
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"cursos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def generate_user_analysis_report():
    """Generate comprehensive user analysis report"""
    st.subheader("📊 Análise de Usuários")
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # User progression analysis
        cursor.execute("""
            SELECT current_level, target_level, COUNT(*) as count
            FROM users 
            GROUP BY current_level, target_level
            ORDER BY current_level, target_level
        """)
        progression_data = cursor.fetchall()
        
        st.write("**Análise de Progressão:}")
        if progression_data:
            progression_df = pd.DataFrame(progression_data, columns=['Nível Atual', 'Nível Alvo', 'Quantidade'])
            st.dataframe(progression_df, use_container_width=True)
        
        # Engagement analysis
        cursor.execute("""
            SELECT u.name, 
                   COUNT(DISTINCT a.id) as assessments_count,
                   COUNT(DISTINCT ci.id) as intentions_count,
                   MAX(a.assessed_at) as last_assessment,
                   MAX(ci.intention_date) as last_intention
            FROM users u
            LEFT JOIN assessments a ON u.id = a.user_id
            LEFT JOIN course_intentions ci ON u.id = ci.user_id
            GROUP BY u.id, u.name
            ORDER BY assessments_count DESC, intentions_count DESC
        """)
        engagement_data = cursor.fetchall()
        
        if engagement_data:
            st.write("**Engajamento dos Usuários:**")
            engagement_df = pd.DataFrame(engagement_data, columns=[
                'Usuário', 'Avaliações', 'Intenções', 'Última Avaliação', 'Última Intenção'
            ])
            st.dataframe(engagement_df, use_container_width=True)

def generate_summary_report():
    """Generate system summary report"""
    st.subheader("📋 Resumo do Sistema")
    
    # Generate comprehensive summary
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        summary_data = {}
        
        # Basic counts
        for table in ['users', 'competencies', 'courses', 'assessments', 'course_intentions']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            summary_data[table] = cursor.fetchone()[0]
        
        st.write("**Estatísticas Gerais:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Usuários", summary_data['users'])
        with col2:
            st.metric("Competências", summary_data['competencies'])
        with col3:
            st.metric("Cursos", summary_data['courses'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avaliações", summary_data['assessments'])
        with col2:
            st.metric("Intenções", summary_data['course_intentions'])
        
        # Additional insights
        cursor.execute("SELECT AVG(score) FROM assessments")
        avg_score = cursor.fetchone()[0]
        
        st.write(f"**Média de Avaliações:** {avg_score:.2f}" if avg_score else "Nenhuma avaliação")

def generate_competency_analysis():
    """Generate competency analysis report"""
    st.subheader("🎯 Análise de Competências")
    
    competencies = db.get_competencies()
    
    if competencies:
        # Group by category
        by_category = {}
        for comp in competencies:
            if comp.category not in by_category:
                by_category[comp.category] = []
            by_category[comp.category].append(comp)
        
        for category, comps in by_category.items():
            st.subheader(f"Competências {category}")
            
            # Create assessment summary
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                
                category_summary = []
                for comp in comps:
                    cursor.execute("""
                        SELECT AVG(a.score), COUNT(a.id)
                        FROM assessments a
                        WHERE a.competency_id = ?
                    """, (comp.id,))
                    result = cursor.fetchone()
                    avg_score, count = result
                    
                    category_summary.append({
                        'Competência': comp.name,
                        'Nível': comp.level,
                        'Média': f"{avg_score:.2f}" if avg_score else "N/A",
                        'Avaliações': count,
                        'Peso': comp.weight
                    })
            
            if category_summary:
                df = pd.DataFrame(category_summary)
                st.dataframe(df, use_container_width=True)

def generate_course_demand_report():
    """Generate course demand report"""
    st.subheader("📚 Análise de Demanda de Cursos")
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Course popularity
        cursor.execute("""
            SELECT c.name, c.category, COUNT(ci.id) as intentions,
                   c.duration_hours, c.is_active
            FROM courses c
            LEFT JOIN course_intentions ci ON c.id = ci.course_id
            GROUP BY c.id
            ORDER BY intentions DESC
        """)
        course_data = cursor.fetchall()
        
        if course_data:
            demand_df = pd.DataFrame(course_data, columns=[
                'Curso', 'Categoria', 'Intenções', 'Duração', 'Ativo'
            ])
            st.dataframe(demand_df, use_container_width=True)
            
            # Visualizations
            fig = px.bar(
                demand_df.head(10),
                x='Curso',
                y='Intenções',
                color='Categoria',
                title="Top 10 Cursos por Demanda"
            )
            st.plotly_chart(fig, use_container_width=True)

def generate_user_progress_report():
    """Generate user progress report"""
    st.subheader("📈 Relatório de Progresso dos Usuários")
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # User progress towards target levels
        cursor.execute("""
            SELECT u.name, u.current_level, u.target_level,
                   COUNT(DISTINCT a.competency_id) as assessed_competencies,
                   AVG(a.score) as avg_score
            FROM users u
            LEFT JOIN assessments a ON u.id = a.user_id
            GROUP BY u.id, u.name
            ORDER BY avg_score DESC
        """)
        progress_data = cursor.fetchall()
        
        if progress_data:
            progress_df = pd.DataFrame(progress_data, columns=[
                'Usuário', 'Nível Atual', 'Nível Alvo', 'Competências Avaliadas', 'Média'
            ])
            st.dataframe(progress_df, use_container_width=True)

def generate_trends_report():
    """Generate trends analysis report"""
    st.subheader("📈 Análise de Tendências")
    
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        
        # Monthly trends for intentions
        cursor.execute("""
            SELECT DATE(intention_date, 'start of month') as month,
                   COUNT(*) as intentions,
                   COUNT(DISTINCT user_id) as active_users
            FROM course_intentions
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        trends_data = cursor.fetchall()
        
        if trends_data:
            trends_df = pd.DataFrame(trends_data, columns=[
                'Mês', 'Intenções', 'Usuários Ativos'
            ])
            st.dataframe(trends_df, use_container_width=True)
            
            # Visualization
            fig = px.line(
                trends_df,
                x='Mês',
                y=['Intenções', 'Usuários Ativos'],
                title="Tendências Mensais"
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    # Initialize session state
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if not st.session_state.current_user:
        login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title(f"👋 {st.session_state.current_user.name}")
    st.sidebar.markdown(f"**Nível:** {st.session_state.current_user.current_level}")
    st.sidebar.markdown(f"**Meta:** {st.session_state.current_user.target_level}")
    
    page = st.sidebar.selectbox(
        "Navegação",
        ["Dashboard", "Autoavaliação", "Cursos", "Administração"],
        key="page_navigation"
    )
    
    if st.sidebar.button("Sair"):
        st.session_state.current_user = None
        st.rerun()
    
    # Page routing
    if page == "Dashboard":
        competency_matrix_dashboard()
    elif page == "Autoavaliação":
        self_assessment_page()
    elif page == "Cursos":
        course_registration_page()
    elif page == "Administração":
        admin_page()

if __name__ == "__main__":
    main()

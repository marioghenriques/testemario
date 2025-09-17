#!/usr/bin/env python3
"""
Database Models for Career Development System
SQLite database schema for competency management and course registration
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Competency:
    id: int
    name: str
    description: str
    category: str  # technical, behavioral, strategic
    level: str  # FC-03, FC-04, FC-05, FC-06
    weight: float = 1.0
    
@dataclass
class Course:
    id: int
    name: str
    description: str
    duration_hours: int
    category: str
    competency_ids: List[int]
    is_active: bool = True
    
@dataclass
class User:
    id: int
    name: str
    email: str
    current_level: str  # FC-03, FC-04, FC-05, FC-06
    target_level: str
    created_at: datetime
    
@dataclass
class Assessment:
    id: int
    user_id: int
    competency_id: int
    score: int  # 1-5 scale
    assessed_at: datetime
    notes: str = ""
    
@dataclass
class CourseIntention:
    id: int
    user_id: int
    course_id: int
    intention_date: datetime
    status: str  # intended, registered, completed, cancelled
    priority: int  # 1-5

class DatabaseManager:
    def __init__(self, db_path: str = "career_development.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    current_level TEXT NOT NULL CHECK (current_level IN ('FC-03', 'FC-04', 'FC-05', 'FC-06')),
                    target_level TEXT NOT NULL CHECK (target_level IN ('FC-03', 'FC-04', 'FC-05', 'FC-06')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Competencies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS competencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL CHECK (category IN ('technical', 'behavioral', 'strategic')),
                    level TEXT NOT NULL CHECK (level IN ('FC-03', 'FC-04', 'FC-05', 'FC-06')),
                    weight REAL DEFAULT 1.0
                )
            ''')
            
            # Courses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    duration_hours INTEGER,
                    category TEXT,
                    competency_ids TEXT,  -- JSON array of competency IDs
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    competency_id INTEGER,
                    score INTEGER CHECK (score BETWEEN 1 AND 5),
                    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (competency_id) REFERENCES competencies (id),
                    UNIQUE(user_id, competency_id)
                )
            ''')
            
            # Course intentions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_intentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    course_id INTEGER,
                    intention_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'intended' CHECK (status IN ('intended', 'registered', 'completed', 'cancelled')),
                    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                )
            ''')
            
            conn.commit()
    
    def seed_initial_data(self):
        """Seed database with initial competencies and courses"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM competencies")
            if cursor.fetchone()[0] > 0:
                return
            
            # Seed competencies
            competencies = [
                # FC-03 Level
                ("Gestão de Tempo", "Capacidade de organizar e priorizar tarefas", "behavioral", "FC-03", 1.0),
                ("Comunicação Básica", "Habilidade de se comunicar de forma clara e objetiva", "behavioral", "FC-03", 1.0),
                ("Trabalho em Equipe", "Colaboração efetiva com colegas", "behavioral", "FC-03", 1.0),
                ("Conhecimento Técnico Operacional", "Domínio dos procedimentos operacionais básicos", "technical", "FC-03", 1.0),
                
                # FC-04 Level
                ("Liderança de Equipe", "Capacidade de liderar e motivar pequenos grupos", "behavioral", "FC-04", 1.2),
                ("Tomada de Decisão", "Habilidade de tomar decisões com informações limitadas", "strategic", "FC-04", 1.1),
                ("Gestão de Projetos", "Coordenação de projetos de pequeno e médio porte", "technical", "FC-04", 1.0),
                ("Resolução de Conflitos", "Mediação de conflitos interpessoais", "behavioral", "FC-04", 1.0),
                
                # FC-05 Level
                ("Visão Estratégica", "Capacidade de pensar estrategicamente sobre o negócio", "strategic", "FC-05", 1.5),
                ("Gestão de Pessoas", "Desenvolvimento e gestão de equipes multidisciplinares", "behavioral", "FC-05", 1.3),
                ("Análise de Dados", "Interpretação de dados para tomada de decisão", "technical", "FC-05", 1.2),
                ("Orçamento e Recursos", "Gestão de recursos financeiros e materiais", "technical", "FC-05", 1.1),
                
                # FC-06 Level
                ("Liderança Executiva", "Capacidade de liderar a nível executivo", "strategic", "FC-06", 1.8),
                ("Transformação Organizacional", "Liderança de mudanças organizacionais", "strategic", "FC-06", 1.6),
                ("Gestão de Stakeholders", "Gestão de relacionamentos com stakeholders chave", "behavioral", "FC-06", 1.4),
                ("Inovação e Estratégia", "Desenvolvimento de estratégias inovadoras", "strategic", "FC-06", 1.7)
            ]
            
            cursor.executemany('''
                INSERT INTO competencies (name, description, category, level, weight)
                VALUES (?, ?, ?, ?, ?)
            ''', competencies)
            
            # Seed courses
            courses = [
                ("Gestão de Tempo e Produtividade", "Técnicas para melhorar gestão do tempo e produtividade pessoal", 8, "productivity", [1, 2]),
                ("Comunicação Eficaz", "Desenvolvimento de habilidades de comunicação verbal e escrita", 16, "communication", [2]),
                ("Liderança Situacional", "Técnicas de liderança adaptável a diferentes contextos", 24, "leadership", [5, 6]),
                ("Tomada de Decisão Baseada em Dados", "Métodos para tomar decisões informadas", 12, "analytics", [6]),
                ("Gestão de Projetos Ágil", "Metodologias ágeis para gestão de projetos", 32, "project_management", [7]),
                ("Visão Estratégica e Planejamento", "Desenvolvimento de pensamento estratégico", 20, "strategy", [9, 17]),
                ("Gestão de Conflitos e Negociação", "Técnicas de mediação e negociação", 16, "leadership", [8]),
                ("Análise de Dados para Negócios", "Ferramentas e técnicas para análise de dados", 40, "analytics", [10]),
                ("Liderança Executiva", "Competências para liderança a nível executivo", 48, "leadership", [13, 14]),
                ("Transformação Digital e Inovação", "Liderança de processos de transformação digital", 36, "innovation", [15, 16])
            ]
            
            for course in courses:
                competency_ids_json = json.dumps(course[4])
                cursor.execute('''
                    INSERT INTO courses (name, description, duration_hours, category, competency_ids)
                    VALUES (?, ?, ?, ?, ?)
                ''', (course[0], course[1], course[2], course[3], competency_ids_json))
            
            conn.commit()
    
    def get_competencies(self, level: Optional[str] = None, category: Optional[str] = None) -> List[Competency]:
        """Get competencies, optionally filtered by level and/or category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, name, description, category, level, weight FROM competencies WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY level, category, name"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [Competency(*row) for row in rows]
    
    def get_competency_by_id(self, competency_id: int) -> Optional[Competency]:
        """Get a specific competency by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, category, level, weight 
                FROM competencies WHERE id = ?
            ''', (competency_id,))
            
            row = cursor.fetchone()
            if row:
                return Competency(*row)
            return None
    
    def get_user_assessments(self, user_id: int) -> Dict[int, Assessment]:
        """Get all assessments for a user, keyed by competency_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, competency_id, score, assessed_at, notes
                FROM assessments WHERE user_id = ?
            ''', (user_id,))
            
            rows = cursor.fetchall()
            assessments = {}
            for row in rows:
                assessment = Assessment(*row)
                assessments[assessment.competency_id] = assessment
            
            return assessments
    
    def save_assessment(self, user_id: int, competency_id: int, score: int, notes: str = ""):
        """Save or update an assessment"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO assessments (user_id, competency_id, score, notes)
                VALUES (?, ?, ?, ?)
            ''', (user_id, competency_id, score, notes))
            conn.commit()
    
    def get_courses(self) -> List[Course]:
        """Get all active courses"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, duration_hours, category, competency_ids, is_active
                FROM courses WHERE is_active = 1
            ''')
            
            rows = cursor.fetchall()
            courses = []
            for row in rows:
                competency_ids = json.loads(row[5]) if row[5] else []
                course = Course(row[0], row[1], row[2], row[3], row[4], competency_ids, row[6])
                courses.append(course)
            
            return courses
    
    def save_course_intention(self, user_id: int, course_id: int, priority: int = 3):
        """Save a course intention"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO course_intentions (user_id, course_id, priority)
                VALUES (?, ?, ?)
            ''', (user_id, course_id, priority))
            conn.commit()
    
    def get_user_intentions(self, user_id: int) -> List[CourseIntention]:
        """Get all course intentions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, user_id, course_id, intention_date, status, priority
                FROM course_intentions WHERE user_id = ?
                ORDER BY priority, intention_date
            ''', (user_id,))
            
            rows = cursor.fetchall()
            return [CourseIntention(*row) for row in rows]
    
    def create_user(self, name: str, email: str, current_level: str, target_level: str) -> int:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, email, current_level, target_level)
                VALUES (?, ?, ?, ?)
            ''', (name, email, current_level, target_level))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, email, current_level, target_level, created_at
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            if row:
                return User(*row)
            return None
    
    def add_competency(self, name, description, category, level, weight):
        """Add a new competency to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO competencies (name, description, category, level, weight)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, category, level, weight))
            conn.commit()
            return cursor.lastrowid
    
    def delete_competency(self, competency_id):
        """Delete a competency"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM competencies WHERE id = ?", (competency_id,))
            conn.commit()
    
    def add_course(self, name, description, duration, category, competency_ids):
        """Add a new course to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO courses (name, description, duration_hours, category, competency_ids)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, duration, category, json.dumps(competency_ids)))
            conn.commit()
            return cursor.lastrowid
    
    def delete_course(self, course_id):
        """Delete a course"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            conn.commit()
    
    def toggle_course_status(self, course_id):
        """Toggle course active status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE courses SET is_active = NOT is_active WHERE id = ?", (course_id,))
            conn.commit()
    
    def reset_user_assessments(self, user_id):
        """Reset all assessments for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assessments WHERE user_id = ?", (user_id,))
            conn.commit()
    
    def delete_user(self, user_id):
        """Delete a user and all related data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM course_intentions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM assessments WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
    
    def _get_connection(self):
        """Helper method to get database connection"""
        return sqlite3.connect(self.db_path)
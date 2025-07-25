import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

# Настройки страницы
st.set_page_config(
    page_title="HR Learning Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Функция для загрузки данных
@st.cache_data
def load_data():
    # Попробуем загрузить из GitHub
    try:
        url = "https://raw.githubusercontent.com/[ВАШ_ЛОГИН]/[НАЗВАНИЕ_РЕПОЗИТОРИЯ]/main/data/learning_data.xlsx"
        # Пример: url = "https://raw.githubusercontent.com/ivanov/learning-dashboard/main/data/learning_data.xlsx"
        
        response = requests.get(url)
        with open("temp_data.xlsx", "wb") as f:
            f.write(response.content)
        df = pd.read_excel("temp_data.xlsx")
        st.success("Данные успешно загружены из GitHub")
        return df
    except Exception as e:
        st.warning(f"Ошибка загрузки из GitHub: {e}. Используется локальный файл")
        try:
            return pd.read_excel("data/learning_data.xlsx")
        except:
            st.error("Локальный файл не найден. Загрузите файл данных")
            return pd.DataFrame()
    df = pd.read_excel(file, sheet_name="РЕЗУЛЬТАТЫ ПЕРВИЧНОГО ОБУЧЕНИЯ")
    
    # Обработка данных
    df = df.replace('-', np.nan)
    df['дата трудоустройства'] = pd.to_datetime(df['дата трудоустройства'], errors='coerce')
    df['дата начала обучения'] = pd.to_datetime(df['дата начала обучения'], errors='coerce')
    df['дата окончания обучения'] = pd.to_datetime(df['дата окончания обучения'], errors='coerce')
    
    # Рассчитываем длительность обучения
    df['длительность обучения (дни)'] = (df['дата окончания обучения'] - df['дата начала обучения']).dt.days
    
    return df

# Функция для стилизации
def apply_style():
    st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .st-b7 {
        background-color: #ffffff;
    }
    .st-at {
        background-color: #e9ecef;
    }
    .css-1aumxhk {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .css-1v0mbdj {
        border-radius: 10px;
    }
    .st-bq {
        border-radius: 10px;
    }
    .st-ae {
        border-radius: 10px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# Основная функция
def main():
    apply_style()
    
    st.title("📊 Аналитика прохождения обучения сотрудниками")
    st.markdown("---")
    
    # Загрузка файла
    uploaded_file = st.file_uploader("Загрузите файл с данными обучения", type=["xlsx"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # Блок информации о данных
        st.sidebar.markdown("### Информация о данных")
        st.sidebar.write(f"Всего сотрудников: {len(df)}")
        st.sidebar.write(f"Дата обновления: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Фильтры
        st.sidebar.markdown("### Фильтры")
        departments = ['Все'] + list(df['подразделение'].unique())
        selected_dept = st.sidebar.selectbox("Департамент", departments)
        
        if selected_dept != 'Все':
            dept_df = df[df['подразделение'] == selected_dept]
            teams = ['Все'] + list(dept_df['отдел'].dropna().unique())
            selected_team = st.sidebar.selectbox("Отдел", teams)
            
            if selected_team != 'Все':
                filtered_df = dept_df[dept_df['отдел'] == selected_team]
            else:
                filtered_df = dept_df
        else:
            filtered_df = df
        
        statuses = ['Все'] + list(df['статус прохождения обучения'].unique())
        selected_status = st.sidebar.selectbox("Статус обучения", statuses)
        
        if selected_status != 'Все':
            filtered_df = filtered_df[filtered_df['статус прохождения обучения'] == selected_status]
        
        # Основные метрики
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Всего сотрудников", len(filtered_df))
        
        with col2:
            completed = len(filtered_df[filtered_df['статус прохождения обучения'] == 'завершено'])
            st.metric("Завершили обучение", f"{completed} ({completed/len(filtered_df)*100:.1f}%)" if len(filtered_df) > 0 else "0")
        
        with col3:
            avg_score = filtered_df['Среднее значение'].mean()
            st.metric("Средний балл", f"{avg_score:.1f}" if not pd.isna(avg_score) else "N/A")
        
        st.markdown("---")
        
        # Визуализация 1: Статусы обучения
        st.subheader("Статусы прохождения обучения")
        status_counts = filtered_df['статус прохождения обучения'].value_counts().reset_index()
        status_counts.columns = ['Статус', 'Количество']
        
        fig1 = px.pie(status_counts, values='Количество', names='Статус', 
                     color='Статус',
                     color_discrete_map={
                         'завершено': '#2ecc71',
                         'в процессе': '#f39c12',
                         'не начато': '#e74c3c'
                     },
                     hole=0.4)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(showlegend=False)
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Визуализация 2: Результаты по модулям
        st.subheader("Результаты по модулям обучения")
        
        modules = [
            'ЦИКЛ ОБРАБОТКИ МП НА МПП', 
            'ХАРАКТЕРИСТИКА МЯСНОЙ ПРОДУКЦИИ',
            'ПОЛУТУШИ',
            'ИНДУСТРИАЛЬНЫЙ УПАКОВКА',
            'ПОТРЕБИТЕЛЬСКАЯ УПАКОВКА',
            'ДЮРОК',
            'ТРИММИНГ',
            'СУБПРОДУКТЫ',
            'Итоговое тестирование.'
        ]
        
        module_scores = []
        
        for module in modules:
            attempt1_col = f"{module} попытка 1 результат"
            attempt2_col = f"{module} попытка 2 результат"
            
            if attempt1_col in df.columns:
                scores = []
                for idx, row in filtered_df.iterrows():
                    if not pd.isna(row[attempt1_col]):
                        if row[attempt1_col] >= 85:
                            scores.append(row[attempt1_col])
                        elif not pd.isna(row.get(attempt2_col, np.nan)):
                            scores.append(row[attempt2_col])
                
                if scores:
                    module_scores.append({
                        'Модуль': module,
                        'Средний балл': np.mean(scores),
                        'Проходной процент': len([s for s in scores if s >= 85]) / len(scores) * 100
                    })
        
        if module_scores:
            module_df = pd.DataFrame(module_scores)
            
            fig2 = px.bar(module_df, x='Модуль', y='Средний балл',
                         color='Проходной процент',
                         color_continuous_scale='Viridis',
                         text='Средний балл')
            fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig2.update_layout(yaxis_range=[0,100])
            
            st.plotly_chart(fig2, use_container_width=True)
        
        # Визуализация 3: Динамика обучения
        st.subheader("Динамика обучения")
        
        if 'дата начала обучения' in filtered_df.columns and 'дата окончания обучения' in filtered_df.columns:
            timeline_df = filtered_df.copy()
            timeline_df['Месяц начала'] = timeline_df['дата начала обучения'].dt.to_period('M').dt.to_timestamp()
            
            monthly_data = timeline_df.groupby('Месяц начала').agg({
                'ФИО': 'count',
                'статус прохождения обучения': lambda x: (x == 'завершено').sum()
            }).reset_index()
            
            monthly_data.columns = ['Месяц', 'Всего начали', 'Завершили']
            monthly_data['Процент завершения'] = monthly_data['Завершили'] / monthly_data['Всего начали'] * 100
            
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=monthly_data['Месяц'],
                y=monthly_data['Всего начали'],
                name='Начали обучение',
                line=dict(color='#3498db', width=3)
            )
            
            fig3.add_trace(go.Scatter(
                x=monthly_data['Месяц'],
                y=monthly_data['Завершили'],
                name='Завершили обучение',
                line=dict(color='#2ecc71', width=3)
            )
            
            fig3.add_trace(go.Scatter(
                x=monthly_data['Месяц'],
                y=monthly_data['Процент завершения'],
                name='Процент завершения',
                line=dict(color='#f39c12', width=3),
                yaxis='y2'
            )
            
            fig3.update_layout(
                yaxis=dict(title='Количество сотрудников'),
                yaxis2=dict(title='Процент завершения (%)', overlaying='y', side='right'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # Визуализация 4: Посещение МПП (для коммерческого департамента)
        if selected_dept == 'Коммерческий департамент' or selected_dept == 'Все':
            st.subheader("Посещение МПП (Коммерческий департамент)")
            
            mpp_df = df[df['подразделение'] == 'Коммерческий департамент']
            
            if not mpp_df.empty:
                mpp_status = mpp_df['Посещение МПП'].value_counts().reset_index()
                mpp_status.columns = ['Статус', 'Количество']
                
                fig4 = px.bar(mpp_status, x='Статус', y='Количество',
                             color='Статус',
                             color_discrete_map={
                                 'пройдено': '#2ecc71',
                                 'запланировано': '#f39c12',
                                 '-': '#95a5a6'
                             })
                
                st.plotly_chart(fig4, use_container_width=True)
                
                total_assigned = len(mpp_df[mpp_df['Посещение МПП'] != '-'])
                completed_mpp = len(mpp_df[mpp_df['Посещение МПП'] == 'пройдено'])
                planned_mpp = len(mpp_df[mpp_df['Посещение МПП'] == 'запланировано'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Всего назначено", total_assigned)
                
                with col2:
                    st.metric("Завершили", f"{completed_mpp} ({completed_mpp/total_assigned*100:.1f}%)" if total_assigned > 0 else "0")
                
                with col3:
                    st.metric("Запланировано", planned_mpp)
        
        # Визуализация 5: Лучшие и худшие результаты
        st.subheader("Топ-5 результатов")
        
        if 'Среднее значение' in filtered_df.columns:
            top_df = filtered_df.sort_values('Среднее значение', ascending=False).head(5)
            bottom_df = filtered_df.sort_values('Среднее значение', ascending=True).head(5)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Лучшие результаты**")
                st.dataframe(top_df[['ФИО', 'отдел', 'Среднее значение']].reset_index(drop=True))
            
            with col2:
                st.markdown("**Худшие результаты**")
                st.dataframe(bottom_df[['ФИО', 'отдел', 'Среднее значение']].reset_index(drop=True))
        
        # Визуализация 6: Анализ попыток
        st.subheader("Анализ попыток прохождения тестов")
        
        attempts_data = []
        
        for module in modules:
            attempt1_col = f"{module} попытка 1 результат"
            attempt2_col = f"{module} попытка 2 результат"
            
            if attempt1_col in df.columns:
                first_attempt = filtered_df[attempt1_col].dropna()
                second_attempt = filtered_df[attempt2_col].dropna()
                
                if len(first_attempt) > 0:
                    passed_first = len(first_attempt[first_attempt >= 85])
                    passed_second = len(second_attempt[second_attempt >= 85]) if not second_attempt.empty else 0
                    
                    attempts_data.append({
                        'Модуль': module,
                        'Прошли с 1 попытки': passed_first,
                        'Прошли со 2 попытки': passed_second,
                        'Не прошли': len(first_attempt) - passed_first - passed_second
                    })
        
        if attempts_data:
            attempts_df = pd.DataFrame(attempts_data)
            attempts_df = attempts_df.melt(id_vars='Модуль', var_name='Попытка', value_name='Количество')
            
            fig5 = px.bar(attempts_df, x='Модуль', y='Количество', color='Попытка',
                         color_discrete_map={
                             'Прошли с 1 попытки': '#2ecc71',
                             'Прошли со 2 попытки': '#f39c12',
                             'Не прошли': '#e74c3c'
                         },
                         barmode='stack')
            
            st.plotly_chart(fig5, use_container_width=True)
        
        # Визуализация 7: Время обучения
        if 'длительность обучения (дни)' in filtered_df.columns:
            st.subheader("Длительность обучения")
            
            duration_df = filtered_df[filtered_df['длительность обучения (дни)'].notna()]
            
            if not duration_df.empty:
                avg_duration = duration_df['длительность обучения (дни)'].mean()
                
                fig6 = px.histogram(duration_df, x='длительность обучения (дни)',
                                   nbins=20,
                                   color_discrete_sequence=['#3498db'])
                fig6.add_vline(x=avg_duration, line_dash="dash", line_color="red",
                              annotation_text=f"Среднее: {avg_duration:.1f} дней", 
                              annotation_position="top")
                
                st.plotly_chart(fig6, use_container_width=True)
        
        # Детализированная таблица
        st.subheader("Детализированные данные")
        
        if 'дата начала обучения' in filtered_df.columns and 'дата окончания обучения' in filtered_df.columns:
            display_cols = ['ФИО', 'подразделение', 'отдел', 'дата начала обучения', 
                          'дата окончания обучения', 'длительность обучения (дни)', 
                          'Среднее значение', 'статус прохождения обучения']
            
            st.dataframe(filtered_df[display_cols].sort_values('Среднее значение', ascending=False))
        
    else:
        st.info("Пожалуйста, загрузите файл с данными обучения для отображения аналитики.")

if __name__ == "__main__":
    main()

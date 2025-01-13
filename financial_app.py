import streamlit as st
import pandas as pd
from in_outcome import calculate_finances, plot_financial_summary
import json
import plotly.graph_objects as go

st.set_page_config(page_title="财务自由计算器", layout="wide")

st.title("财务规划计算器 📊")

# 创建两列布局
col1, col2 = st.columns([1, 2])

MAX_LIVING_AGE = 150

with col1:
    st.subheader("输入参数")
    
    current_savings = st.number_input("当前存款", 
        min_value=0, 
        value=0, 
        step=10000,
        format="%d"
    )
    
    annual_income = st.number_input("年收入", 
        min_value=0, 
        value=500000, 
        step=10000,
        format="%d"
    )
    
    annual_expense = st.number_input("年支出",
        min_value=0,
        value=200000,
        step=10000,
        format="%d"
    )
    
    interest_rate = st.slider("年利率 (%)", 
        min_value=0.0,
        max_value=30.0,
        value=2.5,
        step=0.1
    ) / 100
    
    income_growth = st.slider("收入年增长率 (%)",
        min_value=0.0,
        max_value=30.0,
        value=10.0,
        step=0.1
    ) / 100
    
    expense_growth = st.slider("支出年增长率 (%)",
        min_value=0.0,
        max_value=30.0,
        value=2.2,
        step=0.1
    ) / 100
    
    birth_year = st.number_input("出生年份",
        min_value=1900,
        max_value=2024,
        value=1995
    )
    
    start_age = st.number_input("开始工作年龄",
        min_value=0,
        max_value=MAX_LIVING_AGE,
        value=25
    )
    
    retirement_age = st.number_input("退休年龄",
        min_value=start_age + 1,
        max_value=MAX_LIVING_AGE,
        value=40
    )

    special_income_for_year = {}
    # 特殊年份收入/支出输入
    with st.expander("特殊年份收入/支出调整"):
        st.write("为特定年份添加额外的收入或支出")
        special_year = st.number_input("年份",
            min_value=birth_year + start_age,
            max_value=birth_year + MAX_LIVING_AGE,
            value=birth_year + start_age
        )
        special_income = st.number_input("特殊年份收入",
            min_value=0,
            value=0,
            step=10000,
            format="%d"
        )
        special_expense = st.number_input("特殊年份支出",
            min_value=0,
            value=0,
            step=10000,
            format="%d"
        )
        if special_income != 0 or special_expense != 0:
            special_income_for_year[special_year] = {
                "income": special_income,
                "expense": special_expense
            }

# 创建输入参数字典
input_params = {
    "current_savings": current_savings,
    "annual_income": annual_income,
    "annual_expense": annual_expense,
    "interest_rate": interest_rate,
    "annual_income_growth": income_growth,
    "annual_expense_growth": expense_growth,
    "start_age": start_age,
    "retirement_age": retirement_age,
    "birth_year": birth_year,
    "special_income_for_year": special_income_for_year
}

# 计算结果
result_json = calculate_finances(input_params)
result = json.loads(result_json)
df = pd.DataFrame(result['financial_data'])
coverage_analysis = result['coverage_analysis']

with col2:
    # 添加关键指标展示
    st.subheader("关键指标")
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    # 找到退休年龄对应的数据
    retirement_data = df[df['Age'] == retirement_age]
    if not retirement_data.empty:
        retirement_index = retirement_data.index[0]
        retirement_interest = df['Interest Earned'].iloc[retirement_index]
        retirement_savings = df['Total Savings'].iloc[retirement_index]
    else:
        retirement_interest = df['Interest Earned'].iloc[-1] if not df.empty else 0
        retirement_savings = df['Total Savings'].iloc[-1] if not df.empty else 0

    # 获取最后一年的数据
    last_year_data = df.iloc[-1]
    last_age = last_year_data['Age']
    last_year_savings = last_year_data['Total Savings']
    last_year_interest = last_year_data['Interest Earned']

    # 计算总和
    total_income = df['Annual Income'].sum()
    total_expense = df['Annual Expenses'].sum()
    total_interest = df['Interest Earned'].sum()

    with metrics_col1:
        st.metric(
            label="总工资收入",
            value=f"¥{total_income:,.0f}"
        )
    with metrics_col2:
        st.metric(
            label="总支出",
            value=f"¥{total_expense:,.0f}"
        )
    with metrics_col3:
        st.metric(
            label="总利息收入",
            value=f"¥{total_interest:,.0f}"
        )
    with metrics_col4:
        st.metric(
            label="退休当年总储蓄",
            value=f"¥{retirement_savings:,.0f}"
        )

    # 添加一个新的行来显示关键年龄信息
    st.markdown("---")
    age_col1, age_col2, age_col3 = st.columns(3)
    
    with age_col1:
        st.metric(
            label="开始工作年龄",
            value=f"{start_age}岁({birth_year + start_age}年)"
        )
    with age_col2:
        st.metric(
            label="退休年龄",
            value=f"{retirement_age}岁({birth_year + retirement_age}年)"
        )
    with age_col3:
        st.metric(
            label="终止年龄",
            value=f"{last_age}岁({birth_year + last_age}年)"
        )

    st.subheader("财务预测图表")
    
    # 使用Plotly创建交互式图表
    fig = go.Figure()
    
    # 添加每个数据系列
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Annual Income'],
        name='当前年收入',
        mode='lines+markers',
        hovertemplate='年龄: %{x}岁<br>年收入: ¥%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Annual Expenses'],
        name='当前年支出',
        mode='lines+markers',
        hovertemplate='年龄: %{x}岁<br>年支出: ¥%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Total Savings'],
        name='总储蓄',
        mode='lines+markers',
        hovertemplate='年龄: %{x}岁<br>总储蓄: ¥%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Interest Earned'],
        name='利息收入',
        mode='lines+markers',
        hovertemplate='年龄: %{x}岁<br>利息收入: ¥%{y:,.0f}<extra></extra>'
    ))
    
    # 添加利息覆盖年数（使用次坐标轴）
    fig.add_trace(go.Scatter(
        x=df['Age'],
        y=df['Coverage_Years'],
        name='利息覆盖年数',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#ff7f0e', dash='dot'),
        hovertemplate='年龄: %{x}岁<br>覆盖年数: %{y:.1f}年<extra></extra>'
    ))
    
    # 更新图表布局
    fig.update_layout(
        title='财务概览',
        xaxis_title='年龄',
        yaxis_title='金额 (¥)',
        yaxis2=dict(
            title='覆盖年数',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示详细数据表格
    col_financial, col_coverage = st.columns([2, 1])
    
    with col_financial:
        st.subheader("财务数据明细")
        df_display = df.copy()
        df_display = df_display.drop('Year', axis=1)
        
        # 调整列的顺序和显示名称
        columns_order = [
            'Age', 
            'Annual Income', 
            'Annual Expenses', 
            'Total Savings', 
            'Interest Earned',
            'Net Cash Flow',
            'Interest Coverage Ratio',
            'Coverage_Years'
        ]
        
        column_names = {
            'Age': '年龄',
            'Annual Income': '年收入',
            'Annual Expenses': '年支出',
            'Total Savings': '总储蓄',
            'Interest Earned': '利息收入',
            'Net Cash Flow': '净现金流',
            'Interest Coverage Ratio': '利息覆盖率',
            'Coverage_Years': '储蓄覆盖年数'
        }
        
        df_display = df_display[columns_order]
        df_display.columns = [column_names[col] for col in columns_order]
        
        st.dataframe(
            df_display.style.format({
                '年收入': '{:,.0f}',
                '年支出': '{:,.0f}',
                '总储蓄': '{:,.0f}',
                '利息收入': '{:,.0f}',
                '净现金流': '{:,.0f}',
                '利息覆盖率': '{:.1%}',
                '储蓄覆盖年数': '{:.1f}'
            }).background_gradient(
                subset=['总储蓄', '利息收入', '净现金流'],
                cmap='RdYlGn'
            ),
            use_container_width=True
        )
    
    with col_coverage:
        st.subheader("利息覆盖分析")
        
        # 计算利息覆盖率
        last_year = df_display.iloc[-1]
        last_interest = last_year['利息收入']
        last_expense = last_year['年支出']
        coverage_ratio = last_interest / last_expense if last_expense > 0 else float('inf')
        
        # 从年龄列中提取最后一年的年龄信息
        last_age = last_year['年龄']
        st.write(f"### 最后一年状况 ({last_age})")
        
        st.write(f"总储蓄: ¥{last_year['总储蓄']:,.0f}")
        st.write(f"年支出: ¥{last_year['年支出']:,.0f}")
        st.write(f"利息收入: ¥{last_interest:,.0f}")
        st.write(f"利息覆盖率: {coverage_ratio:.1%}")
        st.write(f"支出增长率: {expense_growth:.1%}")
        
        # 添加利息耗尽预警
        if coverage_ratio < 1:
            st.warning(f"⚠️ 利息收入已不足以覆盖支出，每年需要动用 ¥{last_expense - last_interest:,.0f} 储蓄")
        elif coverage_ratio < 1.2:
            st.warning(f"⚠️ 利息收入接近支出水平，建议关注支出增长")
        else:
            st.success(f"✅ 利息收入充足，可覆盖 {coverage_ratio:.1%} 的支出")

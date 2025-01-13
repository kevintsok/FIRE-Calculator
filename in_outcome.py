import pandas as pd
import matplotlib.pyplot as plt
import json

def calculate_finances(input_params=None):
    # 如果没有提供输入参数，使用默认值
    if input_params is None:
        input_params = {
            "current_savings": 0,
            "annual_income": 700000,
            "annual_expense": 280000,
            "interest_rate": 0.03,
            "annual_income_growth": 0.10,
            "annual_expense_growth": 0.03,
            "start_age": 25,  # 开始工作年龄
            "retirement_age": 40,  # 退休年龄
            "special_income_for_year": {
                "3": -1270000,  # 2027 - 出生年份
                "5": 260000,  # 2029 - 出生年份
                "18": 260000  # 2042 - 出生年份
            }
        }
    else:
        # 如果输入是JSON字符串，转换为字典
        if isinstance(input_params, str):
            input_params = json.loads(input_params)

    annual_income = input_params["annual_income"]
    annual_expense = input_params["annual_expense"]
    total_savings = input_params["current_savings"]
    interest_rate = input_params["interest_rate"]
    annual_income_growth = input_params["annual_income_growth"]
    annual_expense_growth = input_params["annual_expense_growth"]
    special_income_for_year = input_params["special_income_for_year"]

    # 将年龄转换为年份
    birth_year = input_params.get("birth_year", 1995)
    start_year = birth_year + input_params["start_age"]
    retirement_year = birth_year + input_params["retirement_age"]
    years = []
    ages = []
    incomes = []
    expenses = []
    savings = []
    interests = []
    
    # 添加标志来追踪储蓄耗尽状态
    savings_depleted = False
    last_positive_savings_year = None
    retirement_age = input_params["retirement_age"]
    
    year = start_year
    age = input_params["start_age"]
    
    while True:
        years.append(year)
        ages.append(age)
        if age > input_params["start_age"]:
            if age < retirement_age:
                annual_income *= (1 + annual_income_growth)
            annual_expense *= (1 + annual_expense_growth)

        current_special_income = special_income_for_year.get(str(age), 0)
        if age >= retirement_age:
            current_annual_income = current_special_income
        else:
            current_annual_income = annual_income + current_special_income

        # 计算利息收入
        interest_from_savings = max(0, total_savings * interest_rate)
        total_income = current_annual_income + interest_from_savings
        
        # 计算年度储蓄变化
        annual_savings = total_income - annual_expense
        total_savings += annual_savings

        # 记录数据
        incomes.append(current_annual_income)
        expenses.append(annual_expense)
        savings.append(max(0, total_savings))
        interests.append(interest_from_savings)

        # 检查储蓄是否耗尽
        if total_savings <= 0:
            if not savings_depleted:
                savings_depleted = True
                last_positive_savings_year = year - 1
            if age > retirement_age and total_savings <= 0:
                break
                
        year += 1
        age += 1

    # 创建结果DataFrame
    result_df = pd.DataFrame({
        'Year': years,
        'Age': ages,
        'Annual Income': incomes,
        'Annual Expenses': expenses,
        'Total Savings': savings,
        'Interest Earned': interests,
        'Net Cash Flow': [i + j - e for i, j, e in zip(incomes, interests, expenses)],
        'Savings Change': [s2 - s1 for s1, s2 in zip([0] + savings[:-1], savings)],
        'Interest Coverage Ratio': [i/e if e > 0 else float('inf') for i, e in zip(interests, expenses)]
    })

    # 计算每年储蓄可以维持的年数
    yearly_coverage = []
    for year_idx in range(len(ages)):
        current_savings = savings[year_idx]
        current_expense = expenses[year_idx]
        current_interest = interests[year_idx]
        
        if current_expense <= 0:
            coverage_years = float('inf')
        else:
            # 计算当前储蓄可以维持的年数
            remaining_savings = current_savings
            future_expense = current_expense
            years_covered = 0
            
            while remaining_savings > 0:
                interest_earned = remaining_savings * interest_rate
                total_available = interest_earned + remaining_savings
                if total_available < future_expense:
                    years_covered += total_available / future_expense
                    break
                remaining_savings = total_available - future_expense
                future_expense *= (1 + annual_expense_growth)
                years_covered += 1
                
            coverage_years = years_covered
            
        yearly_coverage.append({
            'coverage_years': coverage_years
        })

    # 将结果合并到一个字典中
    result = {
        'financial_data': result_df.assign(
            Coverage_Years=[c['coverage_years'] for c in yearly_coverage]
        ).to_dict(orient='records'),
        'coverage_analysis': yearly_coverage,
        'savings_depletion_year': last_positive_savings_year if savings_depleted else None,
        'final_year': years[-1],
        'total_years_calculated': len(ages),
        'retirement_savings': float(result_df[result_df['Age'] == retirement_age]['Total Savings'].iloc[0]) if retirement_age in result_df['Age'].values else 0,
        'final_status': {
            'total_savings': float(result_df['Total Savings'].iloc[-1]),
            'annual_expense': float(result_df['Annual Expenses'].iloc[-1]),
            'interest_earned': float(result_df['Interest Earned'].iloc[-1]),
            'net_cash_flow': float(result_df['Net Cash Flow'].iloc[-1])
        }
    }
    
    return json.dumps(result)

def plot_financial_summary(financial_data):
    """
    绘制财务概览图表
    
    Args:
        financial_data: JSON字符串或DataFrame
    """
    # 如果输入是JSON字符串，转换为DataFrame
    if isinstance(financial_data, str):
        df = pd.read_json(financial_data)
    else:
        df = financial_data

    plt.figure(figsize=(14, 8))

    for column in ['Annual Income', 'Annual Expenses', 'Total Savings', 'Interest Earned']:
        plt.plot(df['Age'], df[column], label=column, marker='o')
        
        # 为每个数据点添加标注
        for x, y in zip(df['Age'], df[column]):
            plt.annotate(f'{y:,.0f}',
                        (x, y),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center',
                        fontsize=8)

    plt.title('Financial Overview')
    plt.xlabel('Age')
    plt.ylabel('Amount ($)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

def calculate_interest_coverage_years(financial_data):
    """
    计算当前利息收入可以支付多少年的未来支出
    
    Args:
        financial_data: JSON字符串或DataFrame格式的财务数据
    
    Returns:
        coverage_years: float, 利息收入可以支付的年数
        yearly_coverage_details: list, 每年的覆盖详情
    """
    if isinstance(financial_data, str):
        df = pd.read_json(financial_data)
    else:
        df = financial_data
    
    # 获取最后一年的利息收入和支出
    last_year_interest = df['Interest Earned'].iloc[-1]
    last_year_expense = df['Annual Expenses'].iloc[-1]
    
    # 获取年支出增长率
    expense_growth = df['Annual Expenses'].iloc[-1] / df['Annual Expenses'].iloc[-2] - 1
    
    # 计算未来每年的支出和利息覆盖情况
    coverage_years = 0
    remaining_interest = last_year_interest
    yearly_coverage_details = []
    future_expense = last_year_expense
    
    while remaining_interest > 0:
        future_expense *= (1 + expense_growth)
        coverage_ratio = remaining_interest / future_expense
        
        if coverage_ratio < 1:
            # 如果剩余利息不足以支付一整年的支出，计算可以支付的月数
            coverage_years += coverage_ratio
            yearly_coverage_details.append({
                'year': len(yearly_coverage_details) + 1,
                'expense': future_expense,
                'coverage_ratio': coverage_ratio,
                'months_covered': coverage_ratio * 12
            })
            break
        
        coverage_years += 1
        yearly_coverage_details.append({
            'year': len(yearly_coverage_details) + 1,
            'expense': future_expense,
            'coverage_ratio': coverage_ratio,
            'months_covered': 12
        })
        
        remaining_interest -= future_expense
    
    return coverage_years, yearly_coverage_details

# 示例使用
if __name__ == "__main__":
    # 使用默认参数计算
    result_json = calculate_finances()
    result = json.loads(result_json)
    print(result)
    
    # 绘制图表
    plot_financial_summary(json.dumps(result['financial_data']))


# deepseek-chat
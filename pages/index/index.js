Page({
  data: {
    // 输入数据
    currentSavings: 0,
    annualIncome: 500000,
    annualExpense: 200000,
    interestRate: 2.5,
    incomeGrowth: 10,
    expenseGrowth: 2.2,
    birthYear: 1995,
    startAge: 25,
    retirementAge: 40,
    
    // 年龄选择范围
    ageRange: Array.from({length: 100}, (_, i) => i + 1),
    
    // 特殊年份数据
    specialYears: []
  },

  // 绑定输入事件
  bindCurrentSavings(e) {
    this.setData({currentSavings: Number(e.detail.value)});
  },
  bindAnnualIncome(e) {
    this.setData({annualIncome: Number(e.detail.value)});
  },
  bindAnnualExpense(e) {
    this.setData({annualExpense: Number(e.detail.value)});
  },
  bindInterestRate(e) {
    this.setData({interestRate: e.detail.value});
  },
  bindIncomeGrowth(e) {
    this.setData({incomeGrowth: e.detail.value});
  },
  bindExpenseGrowth(e) {
    this.setData({expenseGrowth: e.detail.value});
  },
  bindBirthYear(e) {
    this.setData({birthYear: new Date(e.detail.value).getFullYear()});
  },
  bindStartAge(e) {
    this.setData({startAge: this.data.ageRange[e.detail.value]});
  },
  bindRetirementAge(e) {
    this.setData({retirementAge: this.data.ageRange[e.detail.value]});
  },

  // 特殊年份操作
  addSpecialYear() {
    const newYear = {
      year: this.data.birthYear + this.data.startAge,
      income: 0,
      expense: 0
    };
    this.setData({
      specialYears: [...this.data.specialYears, newYear]
    });
  },
  bindSpecialYear(e) {
    const index = e.currentTarget.dataset.index;
    const year = new Date(e.detail.value).getFullYear();
    this.setData({
      [`specialYears[${index}].year`]: year
    });
  },
  bindSpecialIncome(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({
      [`specialYears[${index}].income`]: Number(e.detail.value)
    });
  },
  bindSpecialExpense(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({
      [`specialYears[${index}].expense`]: Number(e.detail.value)
    });
  },
  deleteSpecialYear(e) {
    const index = e.currentTarget.dataset.index;
    const specialYears = this.data.specialYears.filter((_, i) => i !== index);
    this.setData({specialYears});
  },

  // 计算逻辑
  calculate() {
    const params = {
      current_savings: this.data.currentSavings,
      annual_income: this.data.annualIncome,
      annual_expense: this.data.annualExpense,
      interest_rate: this.data.interestRate / 100,
      annual_income_growth: this.data.incomeGrowth / 100,
      annual_expense_growth: this.data.expenseGrowth / 100,
      start_age: this.data.startAge,
      retirement_age: this.data.retirementAge,
      birth_year: this.data.birthYear,
      special_income_for_year: this.data.specialYears.reduce((acc, item) => {
        acc[item.year] = {
          income: item.income,
          expense: item.expense
        };
        return acc;
      }, {})
    };

    // 调用云函数进行计算
    wx.cloud.callFunction({
      name: 'calculateFinances',
      data: params,
      success: res => {
        wx.navigateTo({
          url: '/pages/result/result?data=' + JSON.stringify(res.result)
        });
      },
      fail: err => {
        wx.showToast({
          title: '计算失败',
          icon: 'none'
        });
        console.error(err);
      }
    });
  }
});

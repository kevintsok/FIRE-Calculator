Page({
  data: {
    retirementAge: 0,
    retirementSavings: 0,
    financialFreedomAge: 0,
    yearlyData: []
  },

  onLoad(options) {
    const resultData = JSON.parse(options.data);
    this.processResultData(resultData);
  },

  processResultData(data) {
    // 处理关键指标
    this.setData({
      retirementAge: data.retirement_age,
      retirementSavings: data.retirement_savings.toFixed(2),
      financialFreedomAge: data.financial_freedom_age
    });

    // 处理年度数据
    const yearlyData = [];
    for (let age = data.start_age; age <= data.retirement_age; age++) {
      yearlyData.push({
        age: age,
        income: data.yearly_income[age].toFixed(2),
        expense: data.yearly_expense[age].toFixed(2),
        savings: data.yearly_savings[age].toFixed(2)
      });
    }
    this.setData({ yearlyData });

    // 绘制图表
    this.drawChart(yearlyData);
  },

  drawChart(data) {
    const ctx = wx.createCanvasContext('financeChart');
    const chartWidth = 300;
    const chartHeight = 200;
    const padding = 20;
    const maxValue = Math.max(...data.map(d => Math.max(d.income, d.expense, d.savings)));

    // 绘制坐标轴
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, chartHeight - padding);
    ctx.lineTo(chartWidth - padding, chartHeight - padding);
    ctx.stroke();

    // 绘制数据点
    const xStep = (chartWidth - 2 * padding) / (data.length - 1);
    const yScale = (chartHeight - 2 * padding) / maxValue;

    // 收入曲线
    ctx.beginPath();
    ctx.setStrokeStyle('#07c160');
    data.forEach((d, i) => {
      const x = padding + i * xStep;
      const y = chartHeight - padding - d.income * yScale;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // 支出曲线
    ctx.beginPath();
    ctx.setStrokeStyle('#ff4d4f');
    data.forEach((d, i) => {
      const x = padding + i * xStep;
      const y = chartHeight - padding - d.expense * yScale;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // 储蓄曲线
    ctx.beginPath();
    ctx.setStrokeStyle('#1890ff');
    data.forEach((d, i) => {
      const x = padding + i * xStep;
      const y = chartHeight - padding - d.savings * yScale;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    ctx.draw();
  }
});

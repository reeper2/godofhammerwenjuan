// 复制为 config.js 并填入 Google Apps Script Web 应用地址
window.SURVEY_CONFIG = {
  // 部署 Code.gs 后获得的 URL（以 /exec 结尾）
  submitUrl: 'https://script.google.com/macros/s/你的部署ID/exec',
  // 与 Apps Script 脚本属性 ADMIN_KEY 一致
  adminKey: '请改成你的强密码',
  // 可选：Google 表格链接，方便管理员直接打开
  sheetUrl: 'https://docs.google.com/spreadsheets/d/你的表格ID/edit'
};

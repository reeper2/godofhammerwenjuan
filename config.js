// 阿里云 · 华东1（杭州），见 aliyun/部署说明.md
window.SURVEY_CONFIG = {
  aliyun: {
    // 函数计算 HTTP 触发器地址（杭州地域一般为 *.cn-hangzhou.fcapp.run）
    submitUrl: 'https://你的函数名.cn-hangzhou.fcapp.run',
    surveyToken: ''
  },
  // 部署 OSS 后填写，便于管理员打开控制台
  consoleUrl: 'https://oss.console.aliyun.com/bucket/oss-cn-hangzhou/你的bucket名称/object?path=survey-responses%2F'
};

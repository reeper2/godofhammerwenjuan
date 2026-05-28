/**
 * 问卷数据收集 — Google Apps Script
 * 部署为 Web 应用（执行身份：我；访问权限：任何人）后，将 URL 填入 config.js
 */
var SHEET_NAME = 'responses';
var ADMIN_KEY_PROP = 'ADMIN_KEY';

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['submitted_at', 'company_name', 'industry', 'ent_type', 'phone', 'email', 'raw_json']);
    sheet.getRange(1, 1, 1, 7).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function parseBody_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    throw new Error('empty body');
  }
  return JSON.parse(e.postData.contents);
}

function jsonOut_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var body = parseBody_(e);
    if (body.action !== 'submit') {
      return jsonOut_({ ok: false, error: 'unknown action' });
    }
    var data = body.payload;
    if (!data || typeof data !== 'object') {
      return jsonOut_({ ok: false, error: 'invalid payload' });
    }
    var sheet = getSheet_();
    sheet.appendRow([
      data.submittedAt || new Date().toISOString(),
      data.company_name || '',
      data.industry || '',
      data.entType || '',
      data.phone || '',
      data.email || '',
      JSON.stringify(data)
    ]);
    return jsonOut_({ ok: true });
  } catch (err) {
    return jsonOut_({ ok: false, error: String(err) });
  }
}

function doGet(e) {
  e = e || { parameter: {} };
  var action = e.parameter.action;
  if (action === 'health') {
    return jsonOut_({ ok: true });
  }
  if (action === 'list') {
    var key = e.parameter.key || '';
    var expected = PropertiesService.getScriptProperties().getProperty(ADMIN_KEY_PROP);
    if (!expected || key !== expected) {
      return jsonOut_({ ok: false, error: 'unauthorized' });
    }
    var sheet = getSheet_();
    var rows = sheet.getDataRange().getValues();
    if (rows.length <= 1) {
      return jsonOut_({ ok: true, submissions: [] });
    }
    var submissions = [];
    for (var i = 1; i < rows.length; i++) {
      try {
        submissions.push(JSON.parse(rows[i][6]));
      } catch (ignore) {
        submissions.push({ submittedAt: rows[i][0], company_name: rows[i][1], _parseError: true });
      }
    }
    return jsonOut_({ ok: true, submissions: submissions });
  }
  return jsonOut_({ ok: false, error: 'unknown action' });
}

/** 首次部署后在 Apps Script 编辑器运行一次，设置管理员密钥 */
function setupAdminKey() {
  PropertiesService.getScriptProperties().setProperty(ADMIN_KEY_PROP, '请改成你的强密码');
  Logger.log('ADMIN_KEY 已写入脚本属性，请到「项目设置 → 脚本属性」中修改');
}

// CurseForge 创建项目页结构探针：填表脚本某一步失败时，在该步骤的 F12 控制台运行，结果自动复制到剪贴板
// 只读取页面结构，不修改任何字段
(() => {
  // 截取元素的精简 HTML，去掉 svg 与长属性
  const slim = (el) => el.outerHTML.replace(/<svg[\s\S]*?<\/svg>/g, '<svg/>').replace(/\s(d|style|srcset|src)="[^"]*"/g, '').slice(0, 2500);
  const visible = (el) => el.getClientRects().length > 0;
  const norm = (t) => (t || '').replace(/[*\s]+/g, ' ').trim().toLowerCase();
  const out = { step: location.hash, translated: !!document.querySelector('[_msttexthash], [_mstmutation]') };

  // 按标签文字找到字段，向上取最近的包含控件的容器
  const labels = ['Class', 'Main category', 'Additional categories', 'Allow Comments', 'Project License', 'Project distribution', 'Description'];
  for (const name of labels) {
    const label = [...document.querySelectorAll('span, label, p, div, h3, h4, legend')].filter(visible)
      .find((el) => norm(el.textContent) === name.toLowerCase() || norm(el.textContent) === name.toLowerCase() + ' ?');
    if (!label) { out[name] = '当前步骤没有该标签'; continue; }
    let box = label;
    for (let i = 0; i < 5 && box.parentElement; i++) {
      box = box.parentElement;
      if (box.querySelector('input, select, textarea, [role="combobox"], [contenteditable="true"]')) break;
    }
    out[name] = { label: `${label.tagName}.${String(label.className).split(' ').slice(0, 3).join('.')}`, html: slim(box) };
  }

  // 页面上所有可见控件与弹层
  out.roles = [...new Set([...document.querySelectorAll('[role]')].map((el) => el.getAttribute('role')))];
  out.inputs = [...document.querySelectorAll('input, select, textarea, [contenteditable="true"]')].filter(visible)
    .map((el) => `${el.tagName}[type=${el.type}][role=${el.getAttribute('role')}][class=${String(el.className).slice(0, 120)}] value=${String(el.value ?? '').slice(0, 40)}`);
  out.buttons = [...document.querySelectorAll('button')].filter(visible).map((b) => `${(b.innerText || '').trim()} [${String(b.className).split(' ').filter((c) => c.startsWith('MuiButton-')).slice(0, 3).join(' ')}]${b.disabled ? ' disabled' : ''}`);
  out.dialogs = [...document.querySelectorAll('[role="dialog"]')].filter(visible).map(slim);

  const text = JSON.stringify(out, null, 1);
  copy(text);
  console.log(text);
  console.log('%c结构已复制到剪贴板', 'color:#2b8a3e;font-weight:bold');
})();

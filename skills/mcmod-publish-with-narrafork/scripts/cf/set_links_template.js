// __TITLE__：CurseForge 项目设置补填 Links（Source / Issues / Wiki）
// 用法：建项成功后打开作者后台的项目设置页，F12 粘贴运行或交给自动化工具注入
(async () => {
  const DATA = __DATA__;
  const report = [];
  const visible = (el) => !!el && el.getClientRects().length > 0;
  const norm = (text) => (text || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  const setValue = (el, value) => {
    const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, value);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    el.dispatchEvent(new Event('blur', { bubbles: true }));
  };

  // 先切到 Links 页签，没有就当作已经在当前页
  const linkTab = [...document.querySelectorAll('a, button, [role="tab"]')]
    .filter(visible)
    .find((el) => /^links$|^链接$/i.test(norm(el.innerText || el.textContent)));
  if (linkTab) {
    linkTab.click();
    await sleep(1200);
  }

  const fieldLabel = (el) => {
    const own = el.closest('label')?.innerText;
    if (own) return own;
    if (el.id) {
      const forLabel = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
      if (forLabel) return forLabel.innerText;
    }
    let node = el.parentElement;
    for (let i = 0; i < 3 && node; i++, node = node.parentElement) {
      const text = node.querySelector('label, p, span');
      if (text && !text.contains(el)) return text.innerText;
    }
    return el.placeholder || el.name || '';
  };

  const inputs = [...document.querySelectorAll('input[type="text"], input[type="url"], input:not([type])')]
    .filter(visible);

  for (const [key, pattern] of Object.entries({ source: /source|源码/i, issues: /issue/i, wiki: /wiki/i })) {
    const url = DATA[key];
    if (!url) continue;
    const input = inputs.find((el) => pattern.test(norm(fieldLabel(el))));
    if (!input) {
      report.push({ 字段: key, 结果: '没找到输入框，请手动填', 值: url });
      continue;
    }
    setValue(input, url);
    report.push({ 字段: key, 结果: input.value === url ? '已填写' : '写入后被拒绝', 值: url });
  }

  console.table(report);
  console.log('%c检查后自己点保存按钮', 'color:#0a0;font-weight:bold');
  if (!report.length) {
    console.log('%c当前页没有可填的链接字段，确认已在项目设置里', 'color:#c92a2a;font-weight:bold');
  }
})();

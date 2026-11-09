(async () => {
  const D = __DATA__;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const warn = [];
  const labelOf = el => {
    const l = document.querySelector(`label[for="${el.id}"]`);
    return (l ? l.innerText : el.parentElement.innerText).trim();
  };
  const setVal = (el, v) => {
    el.value = v;
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  };
  const checkByLabel = (name, text) => {
    const el = [...document.querySelectorAll(`input[name="${name}"]`)].find(e => labelOf(e) === text);
    if (!el) { warn.push(`${name} 找不到选项：${text}`); return null; }
    if (!el.checked) el.click();
    return el;
  };
  const setTags = (id, value) => {
    if (!value) return;
    const el = document.getElementById(id);
    if (!el) { warn.push(`找不到 #${id}`); return; }
    if ($(el).data('tagsinput')) {
      $(el).tagsinput('removeAll');
      $(el).tagsinput('add', value);
    } else {
      setVal(el, value);
    }
    if (el.value !== value) warn.push(`#${id} 写入失败，当前值：${el.value}`);
  };

  setVal(document.querySelector('[data-multi-id=name]'), D.name);
  setVal(document.querySelector('[data-multi-id=ename]'), D.ename || '');
  if (D.sname) setVal(document.querySelector('[data-multi-id=sname]'), D.sname);

  for (const p of D.platforms) checkByLabel('class-platform', p);
  for (const loader of Object.keys(D.versions)) {
    const api = checkByLabel('class-api', loader);
    if (!api) continue;
    await sleep(800);
    const part = api.id.replace('class-data-api-', '');
    for (const v of D.versions[loader]) checkByLabel(`class-mcversion-${part}`, v);
  }

  const CORE = {'科技': '1,1', '魔法': '1,2', '冒险': '1,3', '农业': '1,4', '装饰': '1,5', '实用': '1,23', '辅助': '1,24', '魔改': '1,21', 'LIB': '1,7', '前置': '1,7'};
  const cats = [D.core, ...D.elements];
  for (const c of cats) {
    let a;
    if (/^\d+,\d+$/.test(c)) a = document.querySelector(`a[data-multi-id=category][data-multi-value="${c}"]`);
    else if (CORE[c] && c === D.core) a = document.querySelector(`a[data-multi-id=category][data-multi-value="${CORE[c]}"]`);
    else a = [...document.querySelectorAll('a[data-multi-id=category][data-category-type="1"]')].find(e => e.innerText.trim() === c);
    if (!a) { warn.push(`找不到模组元素：${c}`); continue; }
    if (a.dataset.categorySelected !== 'true') { a.click(); await sleep(150); }
  }

  for (const [head, href, text] of D.links) {
    document.querySelector('#link-frame .link-add').click();
    await sleep(400);
    const rows = document.querySelectorAll('#link-frame .link-row');
    const row = rows[rows.length - 1];
    const sel = row.querySelector('select.link-head-select');
    $(sel).selectpicker('val', head);
    $(sel).trigger('change');
    setVal(row.querySelector('.link-text-href'), href);
    setVal(row.querySelector('.link-text-text'), text || '');
  }

  setVal(document.getElementById('class-intro'), D.intro);
  setTags('class-modid', D.modid);
  setTags('class-cfprojectid', D.cfprojectid);
  setTags('class-mrprojectid', D.mrprojectid);
  setTags('class-tags', D.tags);
  setTags('class-keys', D.keys);
  checkByLabel('class-mode-1', D.client);
  checkByLabel('class-mode-2', D.server);
  checkByLabel('class-status', D.status);
  checkByLabel('class-source', D.source);

  for (const au of D.authors) {
    if (document.querySelector(`#edit-page-3 .author-row[data-id="${au.id}"], .author-list .author-row[data-id="${au.id}"]`)) continue;
    document.querySelector('.author-link').click();
    await sleep(300);
    const box = document.querySelector('.common-select-form .common-select');
    setVal(box.querySelector('.find-key'), String(au.id));
    box.querySelector('.find-btn').click();
    let tr = null;
    for (let i = 0; i < 30 && !tr; i++) { await sleep(200); tr = box.querySelector(`tr[data-id="${au.id}"]`); }
    if (!tr) { warn.push(`搜索不到作者 ${au.name}（ID ${au.id}）`); continue; }
    tr.click();
    await sleep(500);
    const row = document.querySelector(`.author-list .author-row[data-id="${au.id}"]`);
    if (!row) { warn.push(`作者 ${au.name} 添加失败`); continue; }
    if (au.roles && au.roles.length) {
      const sel = row.querySelector('select.author-head-select');
      $(sel).selectpicker('val', au.roles);
      $(sel).trigger('change');
    }
  }

  // 正文里的 {{img:键}} 先通过编辑器的图片上传接口传到百科，再替换成 <img>
  let content = D.content;
  for (const [key, img] of Object.entries(D.images || {})) {
    const token = `{{img:${key}}}`;
    let tag = `【请手动插入图片：${img.file}】`;
    try {
      const action = editor.getActionUrl(editor.getOpt('imageActionName'));
      const fd = new FormData();
      const bin = Uint8Array.from(atob(img.data), c => c.charCodeAt(0));
      fd.append(editor.getOpt('imageFieldName') || 'upfile', new File([bin], img.file, {type: 'image/png'}));
      const res = await (await fetch(action, {method: 'POST', body: fd, credentials: 'include'})).json();
      if (res.state === 'SUCCESS') tag = `<img src="${(editor.getOpt('imageUrlPrefix') || '') + res.url}" alt="${img.file}"/>`;
      else warn.push(`图片 ${img.file} 上传失败：${res.state}`);
    } catch (e) {
      warn.push(`图片 ${img.file} 上传失败：${e}`);
    }
    content = content.split(token).join(tag);
    await sleep(500);
  }
  editor.setContent(content);

  if (D.cover && D.injectCover) {
    const bin = Uint8Array.from(atob(D.cover), c => c.charCodeAt(0));
    const dt = new DataTransfer();
    dt.items.add(new File([bin], 'cover.png', {type: 'image/png'}));
    const input = document.getElementById('cover-select-button');
    input.files = dt.files;
    input.dispatchEvent(new Event('change', {bubbles: true}));
    await sleep(1500);
    // 注入后页面会弹出裁剪框，点「更新封面」把裁剪结果写回表单
    const update = document.getElementById('cover-update-button');
    if (update && !update.classList.contains('hidden')) {
      update.click();
      await sleep(1500);
      const preview = document.getElementById('class-cover-preview-img');
      const src = preview ? preview.src : '';
      if (/^data:image/.test(src)) console.log('%c封面已注入并确认裁剪', 'color:#0a0;font-weight:bold');
      else warn.push('封面注入后没确认成功，请手动点「更新封面」');
    } else {
      warn.push('封面注入后没等到「更新封面」按钮，请手动处理裁剪框');
    }
  }

  const check = {
    名称: document.querySelector('[data-multi-id=name]').value,
    简介: document.getElementById('class-intro').value,
    MODID: document.getElementById('class-modid').value,
    CurseForge: document.getElementById('class-cfprojectid').value,
    Modrinth: document.getElementById('class-mrprojectid').value,
    作者: [...document.querySelectorAll('.author-list .author-row')].map(r => (r.querySelector('a b') || r).innerText.trim()).join(' / '),
  };
  console.table(check);
  if (!check.MODID) warn.push('MODID 为空，必须手动补填');
  if (warn.length) console.warn('需要手动处理：\n' + warn.join('\n'));
  console.log('%c填写完成。' + (D.injectCover ? '封面已自动注入并确认裁剪；' : '封面请点「上传封面」手动选择：' + D.coverPath + '；') + '检查三页内容后自己点「完成添加」。', 'color:#0a0;font-size:14px');
})();

(async () => {
  const DRY_RUN = __DRY_RUN__;
  const ENTRIES = __ENTRIES__;
  const REMARK = __REMARK__;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const setIf = (sel, val) => { if ($(sel).length) $(sel).val(val); };
  const results = [];
  for (const e of ENTRIES) {
    const category = String(e.category || 1);
    const tab = document.querySelector('.item-category a[data-multi-value="' + category + '"]');
    if (!tab) {
      console.warn('[mcmod-batch] 找不到资料分类', category, e.name);
      break;
    }
    if (tab.getAttribute('data-category-selected') !== 'true') {
      $(tab).trigger('click');
      await sleep(1500);
    }
    $('#edit-submit-button').attr('redo-id', e.redo ? String(e.redo) : '');
    document.querySelector('input[placeholder="主要名称.."]').value = e.name;
    document.querySelector('input[placeholder="次要名称.."]').value = e.ename || '';
    if ($('#item-type-select').length) $('#item-type-select').selectpicker('val', '');
    $('#item-type-custom').val(e.type || '').show();
    editor.setContent(e.content || '');
    setIf('#item-regname', e.regname || '');
    setIf('#item-damage', e.damage || '');
    setIf('#item-maxstack', e.maxstack || '');
    setIf('#item-oredict', e.oredict || '');
    setIf('#item-metadata', e.metadata || '');
    $('#icon-32x').val(e.icon32 || '');
    $('#icon-128x').val(e.icon128 || '');
    if (e.icon32) $('#item-icon-32x-preview-img').attr('src', e.icon32);
    if (e.icon128) $('#item-icon-128x-preview-img').attr('src', e.icon128);
    $('input[placeholder="改动附言.."]').val(REMARK);
    const data = getEditorData(DRY_RUN);
    if (DRY_RUN) {
      results.push({ name: e.name, data });
      continue;
    }
    const resp = await new Promise(resolve => {
      $.ajax({
        url: '//' + strEventUrl + '/action/edit/doEdit/',
        type: 'post',
        async: true,
        data: { data: JSON.stringify(data) },
        xhrFields: { withCredentials: true },
        crossDomain: true,
        complete: x => resolve(x.responseText)
      });
    });
    let state = -1;
    let url = '';
    try {
      const j = JSON.parse(resp);
      state = j.state;
      url = j.url || '';
    } catch (err) {}
    results.push({ name: e.name, state, url });
    console.log('[mcmod-batch]', e.name, state, url);
    if (state !== 0) break;
    await sleep(4000);
  }
  window.__mcmodBatchResults = results;
  return results;
})();

const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const script = fs.readFileSync('layouts/full-desktop.js', 'utf8');
function environment(missing=false, fail=false) {
    const widgets = [];
    const old = {screen:0, removed:false, remove(){this.removed=true;}};
    const secondary = {screen:1, removed:false, remove(){this.removed=true;}};
    const allPanels = [old, secondary];
    const ids = ['launcher','sidebar','places'].map(x=>'org.beyondthespire.dreamui.'+x).concat(['taskmanager','systemtray','digitalclock','showdesktop'].map(x=>'org.kde.plasma.'+x));
    const context = {
        knownWidgetTypes: missing ? [] : ids,
        panels:()=>allPanels.filter(p=>!p.removed),
        desktopForScreen:()=>({widgets:()=>widgets.filter(w=>!w.removed),addWidget(id){const w={type:id,remove(){this.removed=true;}};widgets.push(w);return w;}}),
        screenGeometry:()=>({width:1366,height:768}), print:()=>{},
        Panel:function(){this.screen=0;this.remove=()=>this.removed=true;this.addWidget=()=>{if(fail)throw Error('test failure');return {};};allPanels.push(this);}
    };
    return {context,old,secondary,widgets,allPanels};
}
for(const [missing,fail] of [[true,false],[false,true]]){
    const e=environment(missing,fail);
    assert.throws(()=>vm.runInNewContext(script,e.context));
    assert(!e.old.removed);assert(!e.secondary.removed);
    assert.equal(e.allPanels.filter(p=>!p.removed).length,2);
}
const e=environment();
vm.runInNewContext(script,e.context);
assert(e.old.removed);assert(!e.secondary.removed);assert.equal(e.widgets.length,2);
vm.runInNewContext(script,e.context);
assert.equal(e.widgets.length,2);assert.equal(e.allPanels.filter(p=>!p.removed).length,2);
console.log('Layout preflight, failure preservation, and repeat-install checks passed.');

const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('_includes/Nav.html','utf8');assert.match(html,/<button[^>]*aria-expanded="false"/);
let focused=false;const make=()=>({listeners:{},attrs:{},classList:{toggle(){},remove(){}},addEventListener(k,f){this.listeners[k]=f},setAttribute(k,v){this.attrs[k]=v},focus(){focused=true},contains(t){return t===this}});
const button=make(),drop=make(),menu=make(); const doc=make();doc.querySelector=s=>s==='.hamburger'?button:s==='.dropdown'?drop:menu;
vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],{document:doc});
button.listeners.click({stopPropagation(){}});assert.equal(button.attrs['aria-expanded'],'true');
doc.listeners.keydown({key:'Escape',preventDefault(){}});assert.equal(button.attrs['aria-expanded'],'false');assert(focused);
button.listeners.click({stopPropagation(){}});doc.listeners.click({target:{closest(){return null}}});assert.equal(button.attrs['aria-expanded'],'false');

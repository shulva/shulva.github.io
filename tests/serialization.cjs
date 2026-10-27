// Execute the template's JS value expressions with Ruby stdlib JSON as the
// jsonify contract. Full Liquid/Jekyll rendering remains a separate build gate.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),cp=require('child_process');
const template=fs.readFileSync('_includes/Content.html','utf8');
const values={title:'引号" \\ 换行\n</script><script>alert(1)</script>',url:'/中文/"\\\n</script>',excerpt:'摘要 "\\\n</ScRiPt>'};
const block=template.match(/\{\s*title:([\s\S]*?)\}\{%- unless/)[0].split('}{%- unless')[0]+'}';
const rendered=block.replace(/{{([\s\S]*?)}}/g,(_,expr)=>{
 let val=expr.includes('note.title')?values.title:expr.includes('note.url')?values.url:values.excerpt;
 if(expr.includes('jsonify'))val=cp.execFileSync('ruby',['-rjson','-e','print JSON.generate(STDIN.read)'],{input:val,encoding:'utf8'});
 if(expr.includes("replace: '<', '\\u003c'")) val=val.replace(/</g,'\\u003c');
 if(expr.includes('escape')&&!expr.includes('jsonify'))val=val.replace(/"/g,'&quot;');
 return val;
});
assert(!/<\/script/i.test(rendered));const result=vm.runInNewContext('('+rendered+')');for(const k of Object.keys(values))assert.equal(result[k],values[k]);

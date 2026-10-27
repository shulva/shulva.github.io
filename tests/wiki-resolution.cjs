const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(require('path').join(__dirname,'../_includes/Content.html'),'utf8');
const match=html.match(/function findNoteByTitle\(title\) \{([\s\S]*?)\n    \}/);
const context={availableNotes:[{title:'显示标题',name:'filename',path:'folder/filename',url:'/notes/folder/filename'}]};vm.createContext(context);vm.runInContext(match[0],context);
for(const name of ['显示标题','filename','folder/filename.md','filename#section','filename|别名','filename#section|别名'])assert.equal(context.findNoteByTitle(name)?.url,'/notes/folder/filename');
assert.equal(context.findNoteByTitle('unknown'),undefined);

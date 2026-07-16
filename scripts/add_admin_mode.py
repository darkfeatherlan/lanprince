from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the visible admin section.
s = re.sub(
    r'\s*<section id="admin">.*?</section>\s*',
    '\n',
    s,
    count=1,
    flags=re.S,
)

# Keep protected forms hidden until admin mode is enabled.
s = s.replace('<form class="form" id="diaryForm">', '<form class="form admin-only" id="diaryForm">', 1)
s = s.replace('<form class="form" id="recordForm">', '<form class="form admin-only" id="recordForm">', 1)

# Use the existing diary button as a concealed long-press trigger.
s = s.replace(
    '<a class="btn" href="#diary">寫今天的日記</a>',
    '<a class="btn" id="diaryEntryBtn" href="#diary">寫今天的日記</a>',
    1,
)

# Ensure protected requests include the stored password.
s = s.replace("{type:'diary',date:", "{type:'diary',password:getAdminPassword(),date:", 1)
s = s.replace("{type:'record',date:", "{type:'record',password:getAdminPassword(),date:", 1)

js_anchor = "const todayISO=new Date().toLocaleDateString('en-CA');"
new_admin_js = r'''
const ADMIN_KEY='lanPrinceAdminSessionV1';
function getAdminSession(){try{return JSON.parse(localStorage.getItem(ADMIN_KEY)||'null')}catch{return null}}
function getAdminPassword(){const x=getAdminSession();return x&&x.expires>Date.now()?x.password:''}
function setAdminMode(on){document.body.classList.toggle('admin-on',on)}
function restoreAdmin(){const x=getAdminSession();if(x&&x.expires>Date.now())setAdminMode(true);else localStorage.removeItem(ADMIN_KEY)}
function openHiddenAdmin(){
  if(document.body.classList.contains('admin-on')){
    if(confirm('要離開編輯模式嗎？')){localStorage.removeItem(ADMIN_KEY);setAdminMode(false)}
    return;
  }
  const password=prompt('請輸入密碼');
  if(!password)return;
  localStorage.setItem(ADMIN_KEY,JSON.stringify({password,expires:Date.now()+30*864e5}));
  setAdminMode(true);
  document.getElementById('diary').scrollIntoView({behavior:'smooth'});
}
const diaryEntryBtn=document.getElementById('diaryEntryBtn');
let adminPressTimer=null;
let adminLongPressed=false;
function startAdminPress(e){adminLongPressed=false;clearTimeout(adminPressTimer);adminPressTimer=setTimeout(()=>{adminLongPressed=true;openHiddenAdmin()},1500)}
function cancelAdminPress(){clearTimeout(adminPressTimer)}
diaryEntryBtn.addEventListener('pointerdown',startAdminPress);
diaryEntryBtn.addEventListener('pointerup',cancelAdminPress);
diaryEntryBtn.addEventListener('pointerleave',cancelAdminPress);
diaryEntryBtn.addEventListener('pointercancel',cancelAdminPress);
diaryEntryBtn.addEventListener('click',e=>{if(adminLongPressed){e.preventDefault();adminLongPressed=false}});
restoreAdmin();
'''

# Replace the previous admin JavaScript block when present.
s = re.sub(
    r"const ADMIN_KEY='lanPrinceAdminSessionV1';.*?restoreAdmin\(\);\s*",
    new_admin_js,
    s,
    count=1,
    flags=re.S,
)
if "const ADMIN_KEY='lanPrinceAdminSessionV1';" not in s:
    s = s.replace(js_anchor, new_admin_js + js_anchor, 1)

p.write_text(s, encoding='utf-8')

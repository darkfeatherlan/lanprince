from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 移除明顯的管理模式區塊
s = re.sub(r'\s*<section id="admin">.*?</section>\s*', '\n', s, count=1, flags=re.S)

# 保持受保護表單預設隱藏
s = s.replace('<form class="form" id="diaryForm">', '<form class="form admin-only" id="diaryForm">', 1)
s = s.replace('<form class="form" id="recordForm">', '<form class="form admin-only" id="recordForm">', 1)

# 移除原本日記按鈕的隱藏入口 id，恢復一般連結
s = s.replace('<a class="btn" id="diaryEntryBtn" href="#diary">寫今天的日記</a>', '<a class="btn" href="#diary">寫今天的日記</a>', 1)

# 將預產期資訊設為秘密入口
s = s.replace(
    '<div class="fact"><strong>預產期</strong><small>2026 / 11 / 23</small></div>',
    '<div class="fact" id="dueDateSecret"><strong>預產期</strong><small>2026 / 11 / 23</small></div>',
    1,
)

# 確保受保護請求帶入密碼
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
const dueDateSecret=document.getElementById('dueDateSecret');
let dueTapCount=0;
let dueTapTimer=null;
if(dueDateSecret){
  dueDateSecret.addEventListener('click',()=>{
    dueTapCount+=1;
    clearTimeout(dueTapTimer);
    dueTapTimer=setTimeout(()=>{dueTapCount=0},2000);
    if(dueTapCount>=7){
      dueTapCount=0;
      clearTimeout(dueTapTimer);
      openHiddenAdmin();
    }
  });
}
restoreAdmin();
'''

# 取代既有管理模式 JavaScript
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

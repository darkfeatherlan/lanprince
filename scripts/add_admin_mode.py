from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css_marker = '</style>'
css = '''
<style>
.admin-only{display:none!important}
body.admin-on .admin-only{display:grid!important}
.admin-box{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.admin-box input{max-width:260px}
@media(max-width:560px){.admin-box{display:grid}.admin-box input,.admin-box .btn{width:100%;max-width:100%}}
</style>
'''
if 'body.admin-on .admin-only' not in s:
    s = s.replace(css_marker, css_marker + css, 1)

admin_section = '''
<section id="admin"><div class="wrap panel"><div class="kicker">ADMIN MODE</div><h2>管理模式</h2><p class="muted">一般訪客只能瀏覽日記與產檢；輸入管理密碼後才會顯示新增表單。親友祝福維持公開。</p><div class="admin-box"><input type="password" id="adminPassword" placeholder="管理密碼" autocomplete="current-password"><button class="btn" type="button" id="adminLoginBtn">進入管理模式</button><button class="btn alt" type="button" id="adminLogoutBtn" style="display:none">離開管理模式</button><span class="status" id="adminStatus"></span></div></div></section>
'''
anchor = '<section id="diary">'
if 'id="adminLoginBtn"' not in s:
    s = s.replace(anchor, admin_section + anchor, 1)

s = s.replace('<form class="form" id="diaryForm">','<form class="form admin-only" id="diaryForm">',1)
s = s.replace('<form class="form" id="recordForm">','<form class="form admin-only" id="recordForm">',1)
s = s.replace("{type:'diary',date:","{type:'diary',password:getAdminPassword(),date:",1)
s = s.replace("{type:'record',date:","{type:'record',password:getAdminPassword(),date:",1)

js_anchor = "const todayISO=new Date().toLocaleDateString('en-CA');"
admin_js = r'''
const ADMIN_KEY='lanPrinceAdminSessionV1';
function getAdminSession(){try{return JSON.parse(localStorage.getItem(ADMIN_KEY)||'null')}catch{return null}}
function getAdminPassword(){const x=getAdminSession();return x&&x.expires>Date.now()?x.password:''}
function setAdminMode(on){document.body.classList.toggle('admin-on',on);$('adminLogoutBtn').style.display=on?'inline-flex':'none';$('adminLoginBtn').style.display=on?'none':'inline-flex';$('adminPassword').style.display=on?'none':'block';$('adminStatus').textContent=on?'已進入管理模式':''}
function restoreAdmin(){const x=getAdminSession();if(x&&x.expires>Date.now())setAdminMode(true);else localStorage.removeItem(ADMIN_KEY)}
$('adminLoginBtn').onclick=()=>{const password=$('adminPassword').value.trim();if(!password){$('adminStatus').textContent='請輸入管理密碼';$('adminStatus').className='status bad';return}localStorage.setItem(ADMIN_KEY,JSON.stringify({password,expires:Date.now()+30*864e5}));$('adminStatus').className='status ok';setAdminMode(true)};
$('adminLogoutBtn').onclick=()=>{localStorage.removeItem(ADMIN_KEY);$('adminPassword').value='';setAdminMode(false)};
restoreAdmin();
'''
if 'const ADMIN_KEY=' not in s:
    s = s.replace(js_anchor, admin_js + js_anchor, 1)

p.write_text(s, encoding='utf-8')

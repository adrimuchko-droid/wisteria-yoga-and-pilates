import re, os, threading, http.server, socketserver, functools, glob
from playwright.sync_api import sync_playwright
D=os.path.abspath('site'); os.makedirs('shots',exist_ok=True)
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=D)
class Q(H.func):
    def log_message(s,*a):pass
H=functools.partial(Q,directory=D)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(('127.0.0.1',8765),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
B='http://127.0.0.1:8765/'
# static link/anchor check
bad=[]
for f in glob.glob(D+'/**/*.html',recursive=True):
    s=open(f,encoding='utf-8').read(); ids=set(re.findall(r'id="([^"]+)"',s)); d=os.path.dirname(f)
    for h in re.findall(r'(?:href|src)="([^"]+)"',s):
        if h.startswith(('http','mailto','tel','#')) and not h.startswith('#'): continue
        if h=='#': continue
        p,_,a=h.partition('#')
        tgt=os.path.normpath(os.path.join(d,p)) if p else f
        if not os.path.exists(tgt): bad.append((f,h))
        elif a and os.path.splitext(tgt)[1]=='.html' and a not in set(re.findall(r'id="([^"]+)"',open(tgt,encoding='utf-8').read())): bad.append((f,h))
print('broken links:',bad)
with sync_playwright() as p:
    br=p.chromium.launch()
    errs=[]
    for name,vp in (('desk',{'width':1360,'height':900}),('mob',{'width':390,'height':800})):
        pg=br.new_page(viewport=vp); pg.on('pageerror',lambda e:errs.append(str(e)))
        for path in ('index.html','schedule.html','vouchers.html','en/index.html','en/contact.html'):
            pg.goto(B+path); pg.wait_for_timeout(500)
            ov=pg.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            if ov: errs.append(f'h-overflow {name} {path}')
            pg.screenshot(path=f'shots/{name}-{path.replace("/","_")}.png',full_page=(path in('index.html','vouchers.html')))
        pg.close()
    pg=br.new_page(viewport={'width':390,'height':800}); pg.goto(B+'index.html')
    pg.click('.burger'); print('menu open',pg.is_visible('nav#nav')); 
    pg.click('#cc [data-cc=no]'); print('cc hidden',not pg.is_visible('#cc'))
    pg.goto(B+'schedule.html#zapis'); pg.click('#enrol button[type=submit]'); 
    pg.fill('#enrol-name','Test');pg.fill('#enrol-email','a@b.pl');pg.select_option('#enrol-interest',index=1);pg.select_option('#enrol-level',index=1);pg.check('#enrol-c')
    pg.click('#enrol button[type=submit]'); pg.wait_for_timeout(300); print('form msg:',pg.inner_text('#enrol .msg'))
    pg.goto(B+'contact.html'); pg.click('[data-map-load]'); pg.wait_for_timeout(300); print('map iframe',pg.locator('.map iframe').count())
    pg.click('[data-hl-toggle]'); print('clean',pg.evaluate('document.body.classList.contains("clean")'))
    pg.goto(B+'index.html'); pg.click('.lang a'); print('switch ->',pg.url); pg.click('.lang a'); print('back ->',pg.url)
    print('fonts',pg.evaluate('document.fonts.check("20px Parisienne")'),'errors',errs)
    br.close()

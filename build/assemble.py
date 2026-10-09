import os as _os
B = _os.path.dirname(_os.path.abspath(__file__)) + '/'
import json, os, re, hashlib
D=B; OUT=_os.path.dirname(B.rstrip('/')) + '/'; os.makedirs(OUT, exist_ok=True)
net=open(D+'network.json').read(); geom=open(D+'geom.json').read(); router=open(D+'router.js').read()
router=router.replace("if (typeof module !== 'undefined') module.exports = Router;","")
html=open(D+'app.template.html').read()
html=html.replace('/*NET*/null', net).replace('/*GEOM*/null', geom).replace('/*ROUTER*/', router)
open(OUT+'index.html','w').write(html)
ver=hashlib.sha1(html.encode()).hexdigest()[:10]
open(OUT+'sw.js','w').write(open(D+'sw.template.js').read().replace('__VER__', ver))
json.dump({"name":"Underway","short_name":"Underway","start_url":"./","scope":"./","display":"standalone","orientation":"portrait",
 "background_color":"#0e1619","theme_color":"#0e1619","icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},
 open(OUT+'manifest.webmanifest','w'), indent=1)
import shutil
for f in ('pdf.min.js','pdf.worker.min.js','pdfjs-LICENSE.txt'): shutil.copy(D+'vendor/'+f, OUT+f)
print('index.html', len(html)//1024, 'KB, version', ver)

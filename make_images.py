from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
p=Path('/home/cua/workspace/2026-10-10-budget-reservations/images')
bg='#0d0b20'; panel='#19152e'; cyan='#63eee1'; violet='#a995ff'; white='#f4f0ff'; muted='#b1aacb'; red='#ff829e'
def font(n,bold=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf',n)
def base(title,sub):
 im=Image.new('RGB',(1600,900),bg);d=ImageDraw.Draw(im)
 for x in range(0,1600,80):d.line((x,0,x,900),fill='#15112b')
 d.text((70,45),'BHJR  /  AI ENGINEERING',fill=cyan,font=font(20,True))
 d.text((70,100),title,fill=white,font=font(48,True))
 d.text((70,170),sub,fill=muted,font=font(25))
 return im,d
def box(d,rect,lines,color=cyan):
 d.rounded_rectangle(rect,24,fill=panel,outline=color,width=2)
 x,y,_,_=rect
 for i,s in enumerate(lines):d.text((x+30,y+28+i*55),s,fill=color if i==0 else white,font=font(28,i==0))
def arrow(d,a,b):
 d.line((*a,*b),fill=violet,width=5);x,y=b;d.polygon([(x,y),(x-15,y-10),(x-15,y+10)],fill=violet)
im,d=base('Your budget check has a race condition.','Two calls. One budget. Both checks pass.')
box(d,(70,290,720,640),['CHECK THEN AWAIT','Call A sees 100. Wants 60.','Call B sees 100. Wants 60.','Both start spending.'],red)
box(d,(850,290,1530,640),['RESERVE BEFORE AWAIT','A holds 60. Available: 40.','B wants 60. Admission denied.','Timeout keeps A\'s hold.'])
d.text((90,720),'120 / 100',fill=red,font=font(70,True));d.text((860,720),'60 held + 40 free',fill=cyan,font=font(52,True))
d.text((70,840),'A tiny TypeScript reservation ledger  |  Synthetic units  |  No model call',fill=muted,font=font(21));im.save(p/'cover.png')
im,d=base('The check is already stale.','A deterministic microtask interleaving reproduces the problem.')
for x,label in [(80,'Call A'),(800,'Call B')]:
 box(d,(x,270,x+640,480),[label,'spent = 0','0 + 60 <= 100: yes'],violet)
 box(d,(x,560,x+640,740),['After await','Charge 60 units'],red)
 d.line((x+320,480,x+320,560),fill=violet,width=4)
d.text((80,795),'Final charge: 120 units. Budget: 100. Both were admitted.',fill=red,font=font(34,True));im.save(p/'race.png')
im,d=base('Capacity is held before work starts.','Invariant under valid caps: spent + active holds <= limit')
box(d,(70,300,740,620),['LIMIT = 100','A reserves 60 synchronously.','Available falls to 40.','B\'s 60-unit request is denied.'])
box(d,(840,300,1530,620),['RECEIPT = 35','Move A from held to settled.','Spent = 35. Held = 0.','Available = 65.'],violet)
arrow(d,(745,460),(830,460))
d.rounded_rectangle((70,710,1530,785),18,fill=panel)
d.rounded_rectangle((70,710,581,785),18,fill=violet)
d.text((95,733),'35 spent',fill=bg,font=font(23,True));d.text((920,733),'65 available',fill=cyan,font=font(23,True));im.save(p/'capacity.png')
im,d=base('A timeout does not release the hold.','Release requires proof dispatch never began. A timer is not proof.')
box(d,(70,300,450,520),['HELD','Reserve 60','Free: 40'])
box(d,(610,300,1030,520),['UNKNOWN','No trusted receipt','Still held: 60'],red)
box(d,(1180,300,1530,520),['SETTLED','Receipt: 35','Free: 65'],violet)
arrow(d,(460,400),(600,400));arrow(d,(1040,400),(1170,400))
box(d,(70,620,810,815),['RELEASE BEFORE DISPATCH','Only when no dispatch began.','Restores capacity; key stays terminal.'])
d.text((885,640),'Unknown is a state.',fill=white,font=font(34,True));d.text((885,700),'Not a refund policy.',fill=red,font=font(34,True));im.save(p/'timeout.png')

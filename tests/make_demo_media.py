"""Optional developer utility: original synthetic screenshot, not a product photo."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]

if __name__=='__main__':
    font=Path('C:/Windows/Fonts/msyh.ttc')
    if not font.exists(): raise SystemExit('Pass a Chinese font by editing this developer-only fixture utility; not needed at runtime.')
    im=Image.new('RGB',(900,700),'#f0f4f0'); d=ImageDraw.Draw(im)
    f=lambda size:ImageFont.truetype(str(font),size)
    d.text((42,30),'原创合成商品资料卡 / 仅供测试',font=f(32),fill='#176659')
    d.text((42,95),'桌面理线夹 · 6枚装',font=f(42),fill='#182d36')
    for i in range(6):
        x=80+i*125; d.rounded_rectangle((x,200,x+95,310),radius=24,fill='#abc2b8',outline='#426958',width=3)
        d.ellipse((x+27,222,x+69,267),fill='#f0f4f0',outline='#426958',width=3)
        d.line((x+48,200,x+48,226),fill='#426958',width=5)
    for y,t in [(370,'资料文字：硅胶；单孔；用于整理线材'),(425,'进货成本、售价、孔径、资质：未提供'),(480,'长期牢固、无残胶效果：未测试'),(575,'图形为原创示意，不是真实商品摄影或市场数据')]:
        d.text((42,y),t,font=f(26),fill='#182d36')
    dest=ROOT/'examples/media'; dest.mkdir(parents=True,exist_ok=True); im.save(dest/'product-card.png')
    print(dest/'product-card.png')

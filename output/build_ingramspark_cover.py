import sys, pikepdf
from pikepdf import Name, Dictionary, Stream, Array
tpl, jpg, out = sys.argv[1:4]
pdf = pikepdf.open(tpl)
page = pdf.pages[0]
H = 864.0
# template content as a Form XObject (to re-draw the barcode on top)
tpl_bytes = b"\n".join(c.read_bytes() for c in (page.Contents if isinstance(page.Contents, Array) else [page.Contents]))
form = Stream(pdf, tpl_bytes)
form.Type = Name.XObject; form.Subtype = Name.Form
form.BBox = page.MediaBox; form.Resources = page.Resources
form_ref = pdf.make_indirect(form)
with open(jpg, 'rb') as f: data = f.read()
img = Stream(pdf, data)
img.Type = Name.XObject; img.Subtype = Name.Image
img.Width = 4006; img.Height = 2960
img.ColorSpace = Name.DeviceCMYK; img.BitsPerComponent = 8
img.Filter = Name.DCTDecode
img_ref = pdf.make_indirect(img)
res = page.Resources
if Name.XObject not in res: res.XObject = Dictionary()
res.XObject.CoverArt = img_ref
res.XObject.TplForm = form_ref
# bleed area: x 178.703..1080, top 0..666 (PDF y 198..864)
x0, w = 178.703, 1080 - 178.703
y0, h = H - 666.0, 666.0
# barcode white box (top coords 470.772,562.075 - 597.132,634.075)
bx0, bx1 = 470.772, 597.132
by0, by1 = H - 634.075, H - 562.075
ops = (f"q {w:.3f} 0 0 {h:.3f} {x0:.3f} {y0:.3f} cm /CoverArt Do Q\n"
       f"q {bx0:.3f} {by0:.3f} {bx1-bx0:.3f} {by1-by0:.3f} re W n /TplForm Do Q\n").encode()
page.contents_add(Stream(pdf, ops), prepend=False)
pdf.docinfo['/Title'] = 'The 5-Step Book Launch for Experts - Paperback Cover (IngramSpark)'
pdf.docinfo['/Author'] = 'Karina G. Sanchez'
pdf.save(out)

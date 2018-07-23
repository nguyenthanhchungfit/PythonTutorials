from PIL import Image
im = Image.open('avt.jpg')
im.thumbnail((100, 100))
im.save('copy_avt.jpg', 'JPEG')
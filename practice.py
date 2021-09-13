from PIL import Image
from resizeimage import resizeimage

with Image.open('/Users/mingyuzhong/Documents/tracker/resource/image.png') as im:
    # height = im.width//im.height*5
    # width = im.width
    cover = resizeimage.resize_height(im,80)
    cover.save('resource/320_30_logo.png', im.SHARPEN)
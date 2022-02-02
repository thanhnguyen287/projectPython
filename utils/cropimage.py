from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    #Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    #If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

if __name__ == "__main__":
    for i in range(271,301):
        bg = Image.open(f"u_all_axeman_attackA_x2_{i}.png")  # The image to be cropped
        new_im = trim(bg)
        new_im.save(f"{i}.png")

# import Image
# import numpy as np
#
# image=Image.open('L_2d.png')
# image.load()
#
# image_data = np.asarray(image)
# image_data_bw = image_data.max(axis=2)
# non_empty_columns = np.where(image_data_bw.max(axis=0)>0)[0]
# non_empty_rows = np.where(image_data_bw.max(axis=1)>0)[0]
# cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
#
# image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]
#
# new_image = Image.fromarray(image_data_new)
# new_image.save('L_2d_cropped.png')
# import Image
#





# image=Image.open('L_2d.png')
#
# imageBox = image.getbbox()
# cropped=image.crop(imageBox)
# cropped.save('L_2d_cropped.png')

# When you search for boundaries by mask=imageComponents[3], you search only by blue channel.


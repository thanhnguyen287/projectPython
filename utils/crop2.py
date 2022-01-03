from PIL import Image
for i in range(1,75):
    image=Image.open(f'{i}.png')

    imageBox = image.getbbox()
    cropped=image.crop(imageBox)
    cropped.save(f'crop{i}.png')
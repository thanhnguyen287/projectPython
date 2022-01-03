from PIL import Image

"""This program add transparent border, increase size without affecting the inner sprite"""
# i = Image.open("Village")
for i in range(1,76):
    old = Image.open(f'Villagerwalk{i:03d}.png') 
    # old = Image.open(f'{i}.png')
    old_size = old.size

    new_size = (82, 71) #new size here
    new = Image.new("RGBA", new_size)   #RGBA for transparent
    new.paste(old, ((new_size[0]-old_size[0])//2,
                    (new_size[1]-old_size[1])//2))
    new.save(f'{i}_new.png')
# Another version but I prefer my own:
# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)

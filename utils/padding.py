from PIL import Image

"""This program add transparent border, increase size without affecting the inner sprite"""
i = Image.open("i")
for i in range(271,301):
    old = Image.open(f'{i}.png')
    # old = Image.open(f'{i}.png')
    old_size = old.size

    new_size = (86, 100) #new size here
    new = Image.new("RGBA", new_size)   #RGBA for transparent
    new.paste(old, ((new_size[0]-old_size[0])//2,
                    (new_size[1]-old_size[1])//2))
    new.save(f'u_all_axeman_attackA_x2_{i}.png')
# Another version but I prefer my own:
# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)

num = 0xffcc00

print(num)


# <A:255,R:255,G:186,B:87>
def color2arbg(color):
    color_tmp = "<A:255,R:{r},G:{g},B:{b}>"
    red = (0xff0000 & color) >> 16
    green = (0x00ff00 & color) >> 8
    blue = 0x0000ff & color
    print(red, green, blue)
    color_tmp = color_tmp.replace('{r}', str(red))
    color_tmp = color_tmp.replace('{g}', str(green))
    color_tmp = color_tmp.replace('{b}', str(blue))
    return color_tmp


print(color2arbg(0x767676))

str01 = '0000000000000000000000000000000000000000000001111111111111111000000000000000000000000000000000'
print(len(str01))

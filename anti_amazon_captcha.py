# -*- coding: utf-8 -*-
#####################################################
# try to deal with Amazon captcha                   #
#                                                   #
# William Kuo                                       #
# Date: Mar 5 2020                                  #
#####################################################
import pytesseract
from PIL import Image


def anti_amazon_captcha(image_path):
    image = Image.open(image_path).convert('LA')
    width, height = image.size

    # use image histogram and threshold to separate 6 letter
    col_mean_list = list()
    for x in range(0, width):
        total = 0
        for y in range(0, height):
            total += image.getpixel((x, y))[0]
        col_mean = total / height
        col_mean_list.append(col_mean)

    threshold = 241
    separator_index_list = list()
    while len(separator_index_list) != 7:
        if len(separator_index_list) > 7:
            threshold += 1
        elif len(separator_index_list) < 7:
            threshold -= 1
        elif threshold >= 255 or threshold <= 0:
            return 'can not crop correct number of letters'

        col_mean_index_list = list()
        for i, col_mean in enumerate(col_mean_list):
            if col_mean < threshold:
                col_mean_index_list.append(i)
        col_mean_min_index = col_mean_index_list[0]
        col_mean_max_index = col_mean_index_list[-1]

        separator_index_list = [col_mean_min_index]
        for i, v in enumerate(col_mean_index_list[:-1]):
            if v != col_mean_index_list[i + 1] - 1:
                separator_index_list.append(v)
        separator_index_list.append(col_mean_max_index)

    # rotate each character and send to pytesseract
    result = ''
    for i, x in enumerate(separator_index_list[:-1]):
        if i % 2 == 0:
            rotate_angle = 15
        else:
            rotate_angle = -15
        crop_image = image.crop((
            x + 1,
            0,
            separator_index_list[i + 1],
            height,
            )).rotate(
                rotate_angle,
                expand=1,
                ).convert('RGBA')

        fff = Image.new('RGBA', crop_image.size, (255,)*4)
        char_image = Image.composite(crop_image, fff, crop_image)

        # char_image.show()
        char = pytesseract.image_to_string(
            char_image,
            config='''
                -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ
                --psm 10
                ''').upper()  # noqa
        if char == '':
            return 'not get any letter QQ'
        elif len(char) > 1:
            for c in char:
                if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    result += c
                    break
            else:
                return 'get not English letter'
        elif char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            return 'get not English letter "{}"'.format(char)
        else:
            result += char
    return result


# NOTE: some captcha still fail due to crop not correct
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha0.jpg'), 'BTRPRK'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha1.jpg'), 'FYKLXE'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha2.jpg'), 'MXRCTR'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha3.jpg'), 'MBEPFA'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha4.jpg'), 'GRJBUY'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha5.jpg'), 'LACNMU'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha6.jpg'), 'LXUJEP'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha7.jpg'), 'JEPMRY'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha8.jpg'), 'BTCAJK'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha9.jpg'), 'BXYHJX'))
print('{} == {}'.format(anti_amazon_captcha('amazon_captcha10.jpg'), 'HXEJFM'))

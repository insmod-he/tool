#encoding=utf-8
__author__ = 'insmod'
import sys
import os
import dicom
import PIL.Image as Image
import PIL.ImageDraw as Draw
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# 将一个文件夹里面的所有图片拼在一起,便于观察
print("usage:python gen_mp4.py fold_path")
print ""

if len(sys.argv) < 2:
    print "Too few parameter"
    sys.exit(0)

# 1.提取所有图片路径,组成list
fold_path = sys.argv[1]          # 获取输入的文件夹路径
#print fold_path

# 生成文件夹列表;在每个文件夹列表里生成图片列表
for sub_root,sub_dir,sub_files in os.walk(fold_path):
    if len(sub_dir) < 1:
        continue

    # 将2ch,4ch,sax三种分开
    ch2_path = ''
    ch4_path = ''
    sax_list = []
    for sub_dir_entry in sub_dir:
        if "2ch_" in sub_dir_entry:
            ch2_path = sub_root + '/' + sub_dir_entry
        elif "4ch_" in sub_dir_entry:
            ch4_path = sub_root + '/' + sub_dir_entry;
        else:
            sax_list.append(sub_dir_entry)

    #　文件夹后缀转为数字,便于排序
    sax_num = []
    sub_dir_num = []
    for sub_dir_entry in sax_list:
        str_seg = sub_dir_entry.split('_')
        sax_num.append(int(str_seg.pop())) # 去最后一个值
    # 排序以后的数组情况
    sax_num.sort()
    print sax_num

    # total_pic_path里保存所有图像的子文件夹路径
    total_pic_path = []
    total_pic_path.append(ch2_path)
    total_pic_path.append(ch4_path)

    for num in sax_num:
        total_pic_path.append(sub_root + '/sax_'+'%d'%num)

pic_wdh = 256;  # 单张图像宽
pic_len = 256;  # 单张图像高
col_num = 30    # 30列
row_num = len(total_pic_path);
big_image = Image.new("L", (pic_wdh*col_num, pic_len*row_num))
draw = Draw.Draw(big_image,"L")

def update_pic(idx, pics, fg):
    return plt.imshow(pics[idx],cmap=plt.cm.bone,)

# 2.绘制图像 每行30张图像,列数不定
Writer = animation.writers['ffmpeg']   # Set up formatting for the movie files
writer = Writer(fps=10, metadata=dict(artist='Me'))

for tmp_full_path in total_pic_path:
    prefix = tmp_full_path.split('/')[-1]
    image_seris = []
    for tmp_root,tmp_sub_path,tmp_files in os.walk(tmp_full_path):
        if len(tmp_files)<1:
            continue

        # 获取文件名前缀之后,手动生成有顺序的图像序列名称
        names = tmp_files[0].split('-')
        file_name = names[0]+'-'+names[1]
        tmp_files = []
        for idx in range(1,31):
            tmp_files.append(file_name+'-%04d'%idx+'.dcm')

        pics = []
        fig3 = plt.figure()
        for dicom_file in tmp_files:
            ds = dicom.read_file(tmp_full_path+'/'+dicom_file)
            I = np.uint8(ds.pixel_array/2);    # 16位图像变为８位图像
            image_seris.append(Image.fromarray(I, "L"))
            pics.append(I)

        idx = range(0,30);
        pic_ani = animation.FuncAnimation(fig3, update_pic, 30, fargs=(pics, fig3),
                                           interval=100, blit=True)
        print 'writing',prefix
        pic_ani.save(prefix+'.mp4', writer=writer)



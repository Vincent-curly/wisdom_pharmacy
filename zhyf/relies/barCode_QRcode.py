# coding:utf-8
"""
  Time : 2021/1/27 下午3:31
  Author : vincent
  FileName: barCode_QRcode
  Software: PyCharm
  Last Modified by: vincent
  Last Modified time: 2021/1/27 下午3:31
"""
import barcode
from barcode.writer import ImageWriter


def generateBarcode(code):
    # print(barcode.PROVIDED_BARCODES)  # 查看python-barcode支持的条形码格式
    # 获取编码类
    EAN = barcode.get_barcode_class('code128')  # 创建ean13格式的条形码格式对象 参数为支持的格式
    ean = EAN(code, writer=ImageWriter())  # 创建条形码对象
    # fullname = ean.save('d:\ean13_barcode')  # #此处不需要输入文件后缀 保存条形码图片，并返回保存路径。图片格式为png
    # print(ean)
    return ean
    # return fullname

'''
Code构造函数有3个参数：Code(code, writer=None, add_checksum=True)
code参数为编码数据，如'123445'等
writer参数默认值为None，此时默认使用barcodr.writer.SVGWriter()，生成的文件为SVG格式。如果想获得PNG、JPEG或BMP图像格式，需要将该参数设置为barcode.writer.ImageWriter()，例如：Code('123456',barcode.writer.ImageWriter(),False)
add_checksum参数默认值为True，生成的条码中会自动加上校验和，如果为False，则不加校验和
'''

'''
save函数有两个参数：save(filename,options=None)
filename参数为保存文件名，不需要加扩展名，将根据设置自动添加扩展名，由函数返回文件全名。当前面构造函数使用默认writer时，保存为SVG文件，扩展名为.svg。
options参数默认值为None，此时使用默认参数。如果需要修改设置，使用字典传入参数，例如：save("d:\\barcode",{'text': 'ABCD','format':'JPEG'})。可用参数如下：
    'module_width'：默认值0.2，每个条码宽度（？），单位为毫米
    'module_height'：默认值15.0，条码高度，单位为毫米
    'quiet_zone'：默认值6.5，两端空白宽度，单位为毫米
    'font_size'：默认值10，文本字体大小，单位为磅
    'text_distance'：默认值5.0，文本和条码之间的距离，单位为毫米
    'background'：默认值'white'，背景色
    'foreground'：默认值'black'，前景色
    'text'：默认值''，显示文本，默认显示编码，也可以自行设定
    'write_text'：默认值True，是否显示文本，如果为True自动生成text的值，如果为False则不生成（如果此时手工设置了text的值，仍然会显示文本）。
    'center_text'：默认值True，是否居中显示文本
    'format'：默认值'PNG'，保存文件格式，默认为PNG，也可以设为JPEG、BMP等，只在使用ImageWriter时有效。
    'dpi'：默认值300，图片分辨率，，只在使用ImageWriter时有效。
'''
if __name__ == "__main__":
    generateBarcode('KM20092300001-1')
    generateBarcode('huanglei')
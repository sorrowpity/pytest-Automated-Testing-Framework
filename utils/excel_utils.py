import openpyxl
import os
def read_excel(): # 参数传文件路径

    cur_path = os.path.dirname(__file__) # 获取当前文件所在目录路径
    excel_path = os.path.join(cur_path, "../data/data1.xlsx") # 拼接文件路径
    workbook = openpyxl.load_workbook(excel_path) # 参数传文件路径


    # 选择表
    worksheet = workbook["Sheet1"]  # 参数传表名

    # 读取数据
    # zip函数可以将可迭代对象打包成一个元组列表
    # 因为dict(zip(key,values))，可以把读取到的数据变成字典类型，所以只需分别取出key行和value行即可

    data = [] # 用于组装字典
    keys = [cell.value for cell in worksheet[2]] # 拿表中的第2行，拿key行
    # 从第3行开始拿，只返回值的信息
    for row in worksheet.iter_rows(min_row=3, values_only=True):
        dict_data = dict(zip(keys, row))
        # 如果读取的is_true字段的值是TRUE，就将字典添加到data列表中
        # 否则不append到data列表中
        if dict_data['is_true'] == True:
            data.append(dict_data)
        
    # data最终长成这样  [{},{}]符合测试用例需要的数据


    # 关闭文件
    workbook.close()
    return data
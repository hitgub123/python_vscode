import time,os


def upload_file(myfile, filename_dir):
    suffix = str(myfile.name.split('.')[-1])
    times = str(time.time()).split('.').pop()   # 生成时间戳，取小数点后的值
    fil = str(myfile.name.split('.')[0])
    filename = times + '_' + fil + '.' + suffix
    print(filename, filename_dir)
    with open(os.path.join(filename_dir,filename), 'wb+') as destination:
        for chunk in myfile.chunks():
            destination.write(chunk)
        destination.close()
    return filename

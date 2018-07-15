import os

#os.mkdir('subfolder')
#os.rmdir('subfolder')

all_file_names = os.listdir('subfolder')
print(all_file_names)
print(os.getcwd())
print(os.path.exists('subfolder/file1.txt'))
print(os.path.getsize('subfolder/file1.txt'))
print(os.path.isdir('subfolder'))
print(os.path.getatime('subfolder'))
print(os.path.getmtime('subfolder'))
print(os.path.getctime('subfolder'))
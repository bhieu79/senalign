import os

for i in range(1, 2, 1):
    vi = './TraVinhEDU/vi' + str(i) + '.txt'
    km = './TraVinhEDU/km' + str(i) + '.txt'
    out = './TraVinhEDU/o' + str(i) + '.txt'
    command = 'python3 senalign.py -s ' + vi + ' -t ' + km + ' -o ' + out + ' -lang km -pair 1'
    print(command)
    os.system(command)
    print('Done!\n')

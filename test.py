import os

for i in range(3, 4, 1):
    vi = './VietKhmer/Vietnamese_100_0' + str(i) + '.txt'
    km = './VietKhmer/Khmer_100_0' + str(i) + '.txt'
    out = './VietKhmer/o' + str(i) + '.txt'
    command = 'python3 senalign.py -s ' + vi + ' -t ' + km + ' -o ' + out + ' -lang km -pair 1'
    print(command)
    os.system(command)
    print('Done!\n')

import glob
import os

''' Warning: this is slow normally and mind-numbingly slow over VPN '''

def mine_param(param):
    outputlist = []
    for f in biglist:
        with open(f, 'rt') as fin:
            for line in fin:
                if line.startswith(f'##${param.upper()}'):
                    outputlist.append(line.partition('<')[2].partition('>')[0])
                    break
    return outputlist

def saveBiglist(biglist):
    with open('mine_params_output.csv', 'w', newline = '') as fout:
        writer = csv.writer(fout)
        for b in biglist:
            _ = writer.writerow([b])

path = r"S:\opacc"
#biglist = glob.glob(os.path.join(path, '**', 'acqu'), recursive = True)

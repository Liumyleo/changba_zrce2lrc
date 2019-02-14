import six
import os
import re
dir_path = os.getcwd()


def decoding(encode_data):
    mask = [-50, -45, 110, 105, 64, 90, 97, 119, 94, 50, 116, 71, 81, 54, -91, -68]
    record_byte = bytes()
    i = 0
    for encode in encode_data:
        if encode >= 128:
            encode = encode - 256
        else:
            pass
        decode = encode ^ mask[i % 16]
        if decode < 0:
            decode = decode + 256
        else:
            pass
        one_byte = six.int2byte(decode)
        record_byte += one_byte
        i += 1
    data = str(record_byte, encoding='utf-8')
    return data


def str_to_list(string):
    datalist = []
    a = str()
    for aa in string:
        a += aa
        if aa == "\n":
            datalist.append(a)
            a = str()
    return datalist


def start_index(datalist):
    for ids, line in enumerate(datalist):
        if re.search("\[[0-9]+,[0-9]+\]", line.strip("\n")) is not None:
            break
    return ids


def get_zrce_files(zrce_path):
    zrce_files = []
    filelist = []
    for (dirpath, dirnames, filenames) in os.walk(zrce_path):
        for filename in filenames:
            if filename.endswith('.zrce'):
                filename_path = os.sep.join([dirpath, filename])
                filelist.append(os.path.splitext(filename)[0])
                zrce_files.append(filename_path)
    return zrce_files, filelist


in_file_list, names = get_zrce_files('./zrce')

for byte_file, name in zip(in_file_list, names):
    f = open(byte_file, "rb")
    encoding_data = f.read()
    data = decoding(encoding_data)
    data_list = str_to_list(data)
    index = start_index(data_list)
    fout = open(os.path.join('./txt/') + name + "_converted.txt", 'w+')
    fout2 = open(os.path.join('./txt/') + name+"_decoded.txt", 'w+')

    i = 0
    for line in data_list[index:]:
        if line == "\r\n":
            break
        sentence_time_info = re.search("\[[0-9]+,[0-9]+\]", line).group()
        # print(sentence_time_info)
        sentence_start_end_info = sentence_time_info.split("[")[1].split("]")[0].split(',')
        sentence_start_time = int(sentence_start_end_info[0])
        sentence_end_time = int(sentence_start_end_info[1]) + sentence_start_time
        lyric_data = line.strip("\n").strip("\r").split("]")[1]
        word_time = re.findall("<[0-9]+,[0-9]+,[0-9]+>", lyric_data)
        word_data = re.findall(">(.+?)", lyric_data)

        j = 0
        word_size = len(word_time)
        for wTime in word_time:
            word_time_split = wTime.split("<")[1].split(',')
            word_start_time = int(word_time_split[0]) + sentence_start_time
            word_hold_time = int(word_time_split[1])
            word_end_time = word_start_time + word_hold_time
            line_end = 0
            if j == word_size-1:
                line_end = 1
            fout.write("%d %d %d %d %s\n" % (word_start_time, word_end_time, i, line_end, word_data[j]))
            j += 1
        i += 1

        sentence_start_time_sec = sentence_start_time / 1000
        sentence_start_time_min = int(sentence_start_time_sec / 60)
        time = "[" + "%.2d" % sentence_start_time_min + ":" + "%05.2f" % (sentence_start_time_sec % 60) + "]"
        line = line.replace("\r", "").replace(sentence_time_info, time)

        fout2.write(line)

    print(name + " done!")

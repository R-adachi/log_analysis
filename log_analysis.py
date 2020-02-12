import sys
import os
import re
import calendar
import datetime
import gc

LOGFILE_PATH = '/var/log/httpd/'

def log_split(input_log):
    cell = re.compile(r'".+"')
    # cell_str = cell.findall(input_log)
    time_host_log = cell.sub('', input_log)
    time_host_log = time_host_log.translate(str.maketrans('', '', '[]'))
    return(time_host_log.split(' '))

def log_time(input_log):
    month_name = []
    for i in enumerate(calendar.month_abbr):
        month_name.append(list(i))
    del month_name[0]

    tmp = re.split('[:/]',input_log)
    for row in month_name:
        if(row[1] == tmp[1]):
            tmp[1] = row[0]

    tmp2 = list(map(int,tmp))
    time = datetime.datetime(tmp2[2],tmp2[1],tmp2[0],tmp2[3],tmp2[4],tmp2[5])
    return(time)


if __name__ == '__main__':
    syspara = sys.argv
    filenum = 0
    filename = []
    input_para_success_flg = 0
    while(input_para_success_flg==0):
        if(len(syspara)<3):
            print('正しくパラメータを指定してください')
            print('ログファイルの数:',end="")
            filenum = float(input())
            if(filenum>=1 and filenum%1 == 0):
                input_para_success_flg = 1
                filenum = int(filenum)
            else:
                continue
            success_file_cnt = 0
            while(success_file_cnt != filenum):
                print(str(success_file_cnt + 1)+'個目のログファイル名を入力してください:',end="")
                now_filename = LOGFILE_PATH+str(input())
                if(os.path.exists(now_filename)):
                    filename.append(now_filename)
                    success_file_cnt += 1
                else:
                    print('そのログファイルは存在しません。')
        else:
            filenum = float(syspara[1])
            if(filenum>=1 and filenum%1 == 0):
                input_para_success_flg = 1
                filenum = int(filenum)
            else:
                syspara=[]
                continue
            success_file_cnt = 0
            input_filename_list = syspara[2:]
            while(success_file_cnt != filenum):
                now_filename = LOGFILE_PATH + str(input_filename_list[success_file_cnt])
                if(os.path.exists(now_filename)):
                    filename.append(now_filename)
                    success_file_cnt += 1
                else:
                    input_para_success_flg = 0
                    syspara = []
                    break

    periodflg = -1
    while(periodflg < 0):
        print('期間を指定しますか?(yes/no):',end="")
        input_line = str(input())
        if(input_line == 'yes'):
            periodflg = 1
        elif(input_line == 'no'):
            periodflg = 0

    input_period_success_flg = 0

    if(periodflg):
        while(input_period_success_flg == 0):
            print('期間の始まりを入力してください。\n形式は年月日を半角区切りで入力してください。(例:2020 1 1)',end="")
            start_str = input()
            print('期間の終わりを入力してください。\n形式は年月日を半角区切りで入力してください。(例:2020 12 31)',end="")
            end_str = input()
            try:
                tmp = start_str.split(' ')
                tmp = list(map(int,tmp))
                start = datetime.datetime(tmp[0],tmp[1],tmp[2],0,0,0)
                tmp = end_str.split(' ')
                tmp = list(map(int,tmp))
                end = datetime.datetime(tmp[0],tmp[1],tmp[2],23,59,59)
                if(start < end):
                    input_period_success_flg = 1
                else:
                    print('終わりが始まり以前に指定されています。')
            except:
                print('入力形式に誤りがあります。')
                pass

    host_list = []
    host_access_count = []
    time_list = []
    time_access_count = []
    newtime = datetime.datetime(1,1,1,0,0,0)
    oldtime = datetime.datetime(9999,12,31,23,59,59)
    hours = datetime.time(0)
    hours_list = []
    hours_count_list = []
    hours_list.append(hours.hour)
    hours_count_list.append(0)
    while(hours < datetime.time(23)):
        hours = hours.replace(hour = hours.hour+1)
        hours_list.append(hours.hour)
        hours_count_list.append(0)

    if(periodflg == 0):
        for i in filename:
            f = open(i,'r')
            line = f.readline()
            while line:
                log=log_split(line)
                time = log_time(log[3])
                time_hour = int(time.strftime('%H'))
                hours_count_list[hours_list.index(time_hour)] += 1
                if(log[0] not in host_list):
                    host_list.append(log[0])
                    host_access_count.append([log[0],1])
                else:
                    host_access_count[host_list.index(log[0])][1] += 1
                gc.collect()
                line = f.readline()
            f.close()

    else:
        for i in filename:
            f = open(i,'r')
            line = f.readline()
            while line:
                log=log_split(line)
                time = log_time(log[3])
                time_hour = int(time.strftime('%H'))
                if(start<time<end):
                    hours_count_list[hours_list.index(time_hour)] += 1
                    if(log[0] not in host_list):
                        host_list.append(log[0])
                        host_access_count.append([log[0],1])
                    else:
                        host_access_count[host_list.index(log[0])][1] += 1
                gc.collect()
                line = f.readline()
            f.close()

    host_access_count.sort(key = lambda l: l[1],reverse=True)


    if(len(host_access_count) == 0):
        print('アクセス記録はありません。')
    else:
        print('リモートホスト毎のアクセス記録')
        for i in range(len(host_access_count)):
            print('ホスト'+str(host_access_count[i][0])+'からのアクセスは'+str(host_access_count[i][1])+'回です。')
        print('\n')
        print('時刻毎のアクセス記録')
        for i in range(len(hours_count_list)):
            print(str(hours_list[i])+'時のアクセス件数は'+str(hours_count_list[i])+'回です。')

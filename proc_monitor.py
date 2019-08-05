'''
命令： python proc_monitor.py : //pcpu+降序排列
   
       python proc_monitor.py -s pmem : // pmem+降序排列 

       或加 -l 7 ,显示7条进程信息

       加 -h， 打印帮助信息

       加 -v， 显示版本号	   
'''

from optparse import OptionParser # 命令行
import psutil # 系统库
import heapq # 取列表的前n大个值时用到
import socket # DNF以及ip值时用到
import sys 
from decimal import Decimal # 四舍五入时
import logging # 日志库
import os 
import time # 统计系统运行时间

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
def main():
    start_time = time.clock()

    #新建命令行对象
    parser = OptionParser()
    parser.add_option("-s","--sort",action="store",  # 此处action默认为store，不能用store_true
                     # action指示 optparse 当解析到一个命令行参数时该如何处理
                     type='string', #参数类型
                     dest="sort_info", # dest为存储的变量
                     default="pcpu", # 默认值
                     help="指定输出进程的排序,(默认为pcpu)")

    parser.add_option("-d","--direction",action="store",
                     type='string',
                     dest="direction_info",
                     default="desc",
                     help="指定sort字段的排序方式,(默认desc降序)")

    parser.add_option("-l","--limit",action="store",
                     type='int',
                     dest="limit_info",
                     default=5,
                     help="指定输出的信息的进程的个数,(默认为5)")

    parser.add_option("-v","--version",action="store_true",
                     dest="version_info",
                     default=False,
                     help="显示当前脚本版号并退出")

    (options,args) = parser.parse_args() # 解析命令行
	
    if options.version_info is True: # 输出版本号
        print('proc_monitor.py 1.0.0')
        sys.exit(0) # 0表示正常退出

#--------------------------------------------------------------------#

    # 设置日志,logging.txt
    log_filename = "logging.txt" #设置日志输出文件

    log_format = '[%(asctime)s] %(message)s' #设置日志输出格式

    #filemode取‘a’时，原日志文件内容不会被覆盖；取‘w’时，每次都会覆盖原内容
    logging.basicConfig(format=log_format,datefmt='%Y-%m-%d %H:%M:%S %p',level=logging.INFO,filename=os.path.join(os.getcwd(),log_filename),filemode='a')

    logging.info('日志输出！')

#—————————————————————————————————————————————————————————————————————#

    #得到进程id值
    proc_ids = psutil.pids()

    #得到用户进程，删去内核进程
    proc_ids_new = []  #用来存储用户进程，取掉内核进程
    for proc_id in proc_ids:
        try: #此处根据进程的cmdline()是否为空列表来判断，内核进程，估计此处还有问题；
            if len(psutil.Process(proc_id).cmdline())!= 0 :
                proc_ids_new.append(proc_id)
        except: # 凡是无访问权限的一律跳过
            continue

    #得到需要展示的进程
    proc_middle = [] # 用来存储各个进程的pcpu或者pmem
    temp = [] # 用来存储最靠前的那几个进程id
    
    #情况一：pcpu排序+desc
    if options.sort_info == "pcpu" and options.direction_info == "desc":
        for proc_id in proc_ids_new:
            try: #得到用户进程的pcpu
                proc_middle.append(psutil.Process(proc_id).cpu_percent(interval=1))
            except: # 得不到的跳过
                continue
        max_n = options.limit_info; # 取pcpu最大的5个进程id
        temp.extend(list(map(proc_middle.index,heapq.nlargest(max_n,proc_middle)))) 
        # 使用heapd来找，放在temp中

    #情况三：pmem排序+desc
    if options.sort_info == "pmem" and options.direction_info == "desc": # 同上，pcpu换为pmem
        for proc_id in proc_ids_new:
            try:
                proc_middle.append(psutil.Process(proc_id).memory_percent())
            except:
                continue
        max_n = options.limit_info;
        temp.extend(list(map(proc_middle.index,heapq.nlargest(max_n,proc_middle))))
	
    res = [] # 用来存放结果，即需要打印的进程信息
    gate = 0 # 限制需要打印的进程数
    for index in temp: 
        try: #得到需要的进程信息
            while gate == options.limit_info: #如果进程够了，就不再获取
                break
            p = psutil.Process(proc_ids_new[index]) # 根据进程id得到的进程
            middle = str(p.username()) + "  " #用户信息
            middle += str(proc_ids_new[index]) + "  " #进程pid
            middle += str(p.cmdline()[0]) + "  " # 进程启动的命令行
            middle += str(p.memory_info().vms) + "  " #虚拟内存
            middle += str(p.memory_info().rss) + "  "  #物理内存
            middle += str(p.cpu_percent(interval=1)) + "%" + "  " #进程cpu百分比
            middle += str(round(p.memory_percent(),2)) + "%" + " " #进程内存百分>比
            res.append(middle) # 将进程添加到res中
            gate += 1
			
        except:
            continue

#—————————————————————————————————————————————————————————————————————#

    #开始打印并写入日志中
    print("host info: ")
    logging.info("host info: ")

    #ip地址
    ip_addr = socket.gethostbyname(socket.gethostname())
    #DNS反解域名
    try: # 题目要求
        myfullyname = socket.gethostbyaddr(ip_addr)[0]
    except:
        myfullyname = "unknown"
    print("%s  %s" %(ip_addr,myfullyname))
    logging.info("%s  %s" %(ip_addr,myfullyname))

    print('\n')
    logging.info('\n')
    print("proc info: ") # 开始打印进程信息
    logging.info("proc info: ")
    for item in res: # 循环res，打印进程
        print(item)
        logging.info(item) # 写入log中
    print('\n')
    logging.info('\n')
    end_time = time.clock()
    # print("运行时间：" + str(int(end_time - start_time)) + " s")
    return

if __name__=="__main__":
    main()
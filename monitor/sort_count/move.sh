#!/bin/bash

#获取前一天的数据，day：天数
date=`date -d -1days "+%Y%m%d"`
datadir="/data/count/access_log/$date/"
base="/home/iris/online_task/monitor/sort_count/$date/"

if [ ! -d $base ];
then
        echo "新创建"$date
        mkdir -p ${base}ask
        mkdir ${base}wap_ask
else
        echo "已创建"$date
fi

cp ${datadir}ask/*.log.gz ${base}ask
cp ${datadir}ask/filelist.txt ${base}ask
cp ${datadir}wap_ask/*.log.gz ${base}wap_ask
cp ${datadir}wap_ask/filelist.txt ${base}wap_ask

chown -R iris:iris ${base}


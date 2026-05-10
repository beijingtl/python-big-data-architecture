# -*- coding:utf-8 -*-

# 4.5 Python操作Datax实现数据同步

import os

log_file = 'test.log'
datax_str = 'python /bigdata/packages/datax/bin/datax.py '
json_file = './datax_conf/mysql2mysql_full_migration_more_config.json'
cmd = f'{datax_str} {json_file} | tee -a {log_file}'
response = os.popen(cmd).read()

# 4.6 Python操作第三方库实现Google Analytics数据同步
# 4.6.2
import pandas as pd
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


# 初始化GA对象
def init_analytics(json_file, scope):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)
    return build('analyticsreporting', 'v4', credentials=credentials)


# 根据请求条件获得数据
def get_report(analytics, query_condition):
    return analytics.reports().batchGet(body={'reportRequests': query_condition}).execute()


# 格式化数据
def format_data(response):
    df_list = []
    for report in response['reports']:
        # 获得维度名和指标名
        dim_headers = report['columnHeader']['dimensions']
        metrics_headers = [i['name'] for i in report['columnHeader']['metricHeader']['metricHeaderEntries']]
        columns = dim_headers + metrics_headers
        # 获得详细记录数据
        records = [row['dimensions'] + row['metrics'][0]['values'] for row in report['data']['rows']]
        # 生成pandas df并返回
        df_list.append(pd.DataFrame(records, columns=columns))
    return df_list


# 调用集成
def app(json_file, scope, query_condition):
    analytics = init_analytics(json_file, scope)
    response = get_report(analytics, query_condition)
    data = format_data(response)
    print([df.info() for df in data])
    print([df.head(5) for df in data])


# 完整使用
SCOPE = ['https://www.googleapis.com/auth/analytics.readonly']
JSON_FILE = "data-python-for-ga-c8ece0474e37.json"
VIEW_ID = '85815377'
query_condition1 = [
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}],
        'dimensions': [{'name': 'ga:country'}]
    }]
app(JSON_FILE, SCOPE, query_condition1)

query_condition2 = [
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}],
        'dimensions': [{'name': 'ga:country'}]
    },
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}, {'expression': 'ga:newUsers'},
                    {'expression': 'ga:sessionsPerUser'}],
        'dimensions': [{'name': 'ga:date'}, {'name': 'ga:browser'}]
    }]
app(JSON_FILE, SCOPE, query_condition2)

query_condition3 = [
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}],
        'dimensions': [{'name': 'ga:date'}, {'name': 'ga:browser'}],
        "dimensionFilterClauses": [
            {
                "filters": [
                    {
                        "dimensionName": "ga:browser",
                        "operator": "EXACT",
                        "expressions": ["Chrome"]
                    }
                ]
            }
        ]
    }]
app(JSON_FILE, SCOPE, query_condition3)

query_condition4 = [
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}],
        'dimensions': [{'name': 'ga:date'}, {'name': 'ga:browser'}],
        "dimensionFilterClauses": [
            {
                "filters": [
                    {
                        "dimensionName": "ga:browser",
                        "operator": "EXACT",
                        "expressions": ["Chrome"]
                    }
                ]
            }
        ],
        "metricFilterClauses": [
            {"filters": [
                {"metricName": "ga:sessions",
                 "operator": "GREATER_THAN",  # EQUAL, LESS_THAN, GREATER_THAN, IS_MISSING
                 "comparisonValue": "70"}
            ]}
        ],
    }]
app(JSON_FILE, SCOPE, query_condition4)

query_condition5 = [
    {
        'viewId': VIEW_ID,
        'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
        'metrics': [{'expression': 'ga:sessions'}],
        'dimensions': [{'name': 'ga:date'}, {'name': 'ga:browser'}],
        "dimensionFilterClauses": [
            {
                "filters": [
                    {
                        "dimensionName": "ga:browser",
                        "operator": "IN_LIST",
                        # 列表匹配
                        "expressions": ["Chrome", "Firefox"],
                        "caseSensitive": False
                    },
                    {
                        "dimensionName": "ga:date",
                        "operator": "BEGINS_WITH",
                        "expressions": ["202106"],
                        "caseSensitive": True
                    },
                ],
                "operator": "AND"  # AND/OR
            }
        ]
    }]
app(JSON_FILE, SCOPE, query_condition5)

# 4.7 Python操作API实现百度统计数据同步
# 4.7.2
# 1. 获得站点列表数据
import json
import requests

# 获取站点列表
header = {
    "username": "bj-触脉",  # 请填写百度推广账户的真实用户名
    "password": "chumai2019Truemetrics-",  # 请填写百度推广账户的真实密码
    "token": "********************",  # 请填写实际获取的token信息 cb338f1cf4294de0554cf86f095acea7
}
site_info_body = {"header": header}
site_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getSiteList'
rep = requests.post(site_info_url, json.dumps(site_info_body))
print(rep.json())

# 2. 获得报告数据
# 定义请求体
from datetime import timedelta, datetime
import pandas as pd

yesterday_str = (datetime.today() + timedelta(-1)).strftime('%Y%m%d')
body = {
    "site_id": "5006682",
    "start_date": yesterday_str,
    "end_date": yesterday_str,
    "metrics": "pv_count,pv_ratio,visit_count,visitor_count,new_visitor_count,new_visitor_ratio,ip_count,bounce_ratio,avg_visit_time,avg_visit_pages,trans_count,trans_ratio",
    "method": "source/all/a"
}
site_info_body2 = {"header": header,
                   "body": body}
data_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'

# 发送请求并获得返回数据
rep = requests.post(data_info_url, json.dumps(site_info_body2))
# 打印输出
print(rep.text)

# 解析分渠道数据
res_root = rep.json()['body']['data'][0]['result']
fields = res_root['fields']
items = res_root['items']
source_data = [i[0]['name'] for i in items[0]]
for i, j in zip(items[1], source_data):
    i.insert(0, j)
source_df = pd.DataFrame(items[1], columns=fields)

# 解析汇总数据
total = res_root['sum'][0]
total.insert(0, 'total')
total_df = pd.DataFrame(total).T
total_df.columns = fields

# 合并分渠道数据和汇总数据
df = pd.concat((source_df, total_df), axis=0)
df['date'] = yesterday_str
print(df)

# 4.7.3
# 2. 条件查询
body = {
    "site_id": "5006682",
    "start_date": yesterday_str,
    "end_date": yesterday_str,
    "metrics": "pv_count,pv_ratio,visit_count,visitor_count,new_visitor_count,new_visitor_ratio,ip_count,bounce_ratio,avg_visit_time,avg_visit_pages,trans_count,trans_ratio",
    "method": "source/all/a",
    "gran": "hour",
    "source": "search,0",
    "clientDevice": "pc",
    "visitor": "new",
    "area": "china",
    "target": 1,
}
site_info_body3 = {"header": header,
                   "body": body}
data_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'

# 发送请求并获得返回数据
rep = requests.post(data_info_url, json.dumps(site_info_body3))
# 打印输出
print(rep.json())

# 3. 排序和分页查询
body = {
    "site_id": "5006682",
    "start_date": yesterday_str,
    "end_date": yesterday_str,
    "metrics": "pv_count,pv_ratio,visit_count",
    "method": "source/all/a",
    "order": "pv_count,asc",
    "start_index": 0,
    "max_results": 0
}
site_info_body4 = {"header": header,
                   "body": body}
data_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getData'

# 发送请求并获得返回数据
rep = requests.post(data_info_url, json.dumps(site_info_body4))
# 打印输出
print(rep.json())

# 4. 分析云事件分析数据导出服务
metrics = [
    {
        "event": "pageview_",
        "aggregation": "visitor_avg,1",
    },
    {
        "id": 3340,
        "name": "人均事件数",
        "label": "人均事件数",
        "expression": [
            {
                "event": "any_",
                "aggregation": "sum,1",
                "filter": {"items": [], "op": "AND"}
            },
            "/",
            {
                "event": "any_",
                "aggregation": "distinct_count,virtual_visitor_id__",
                "filter": {"items": [], "op": "AND"}
            },
        ],
        "formatType": 1,
        "expired": False,
        "isPredefined": False,
        "groupId": 0
    }
]
dimensions = [
    {
        "key": "province_",
    },
    {
        "key": "is_new_visitor_",
    }
]
where = {
    "op": "AND",
    "items": [
        {
            "key": "province_",
            "op": "LIKE",
            "val": ["上海", "北京", "广东"]
        },
        {
            "key": "visitdomain_",
            "op": "=",
            "val": ["www.truemetrics.cn"]
        }
    ]
}
body = {
    "site_id": "5006682",
    "start_date": yesterday_str,
    "end_date": yesterday_str,
    "method": "event/a",
    "metrics": metrics,
    "order": "metric_0,desc",
    "dimensions": dimensions,
    "gran": "day",
    "where": where,
}
site_info_body6 = {"header": header,
                   "body": body}
data_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getAnalyticsData'

# 发送请求并获得返回数据
rep = requests.post(data_info_url, json.dumps(site_info_body6))
# 打印输出
print(rep.json())

# 5. 分析云数据例行导出服务
body = {
    "site_id": "5006682",
}
site_info_body6 = {"header": header,
                   "body": body}
data_info_url = 'https://api.baidu.com/json/tongji/v1/ReportService/getAnalyticsDataList'

# 发送请求并获得返回数据
rep = requests.post(data_info_url, json.dumps(site_info_body6))
# 打印输出
print(rep.json())
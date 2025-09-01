# 前端启动
cd fronted

npm run dev


# 后端运行
cd backend
uvicorn app.main:app --reload --port 8000


数据爬取， 需要补充headers.txt
python qimai_crawl.py --start 2025-5-31 --end 2025-08-25 --brands 0 1 2 --cookie_file headers.txt

# spark 配置路径
/opt/homebrew/Cellar/apache-spark/4.0.0/libexec/conf/spark-defaults.conf

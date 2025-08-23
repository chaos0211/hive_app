from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/kpis")
def kpis():
    return {
        "collect_yesterday": 12845,
        "partitions": 248,
        "top_app": {"name":"华为应用市场","rating":4.8,"category":"工具"},
        "top_category": {"name":"游戏","share":"32.5%","apps":128},
        "predict_cover": 89.7,
        "task_success": 96.2
    }

@router.get("/topn-trend")
def topn_trend(days:int=7, top:int=5):
    x = ["6/10","6/11","6/12","6/13","6/14","6/15","6/16"]
    return {"x": x, "series": {
        "华为应用市场":[1,1,1,1,1,1,1],
        "微信":[2,2,3,2,2,2,2],
        "抖音":[3,3,2,3,3,3,3],
        "支付宝":[4,4,4,4,5,4,4],
        "淘宝":[5,5,5,5,4,5,5]
    }}

@router.get("/category-share")
def category_share():
    return [
        {"name":"游戏","value":325},{"name":"社交","value":244},{"name":"工具","value":188},
        {"name":"娱乐","value":155},{"name":"教育","value":102},{"name":"其他","value":85}
    ]

@router.get("/region-heatmap")
def region_heatmap():
    return [
        {"name":"北京","value":150},{"name":"天津","value":80},{"name":"上海","value":180},
        {"name":"广东","value":170},{"name":"浙江","value":130},{"name":"江苏","value":120},
        {"name":"四川","value":100},{"name":"福建","value":95},{"name":"山东","value":90}
    ]

@router.get("/task-gantt")
def task_gantt():
    return [
        {"name":"数据采集","start":"2023-06-15 08:00","end":"2023-06-15 09:30","color":"#00B42A"},
        {"name":"数据清洗","start":"2023-06-15 09:30","end":"2023-06-15 10:45","color":"#00B42A"},
        {"name":"数据分析","start":"2023-06-15 10:45","end":"2023-06-15 12:30","color":"#00B42A"},
        {"name":"数据预测","start":"2023-06-15 12:30","end":"2023-06-15 14:15","color":"#FF7D00"},
        {"name":"报表生成","start":"2023-06-15 14:15","end":"2023-06-15 15:00","color":"#165DFF"}
    ]

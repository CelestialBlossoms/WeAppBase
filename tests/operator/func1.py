from kit.sf_api.api import SF
import wechatpayv3
clientcode= "JJFJYOZQ6S27"
checkword="UPJlC9gp2jKsEagsk57DCfGtUpw6SKfr"
order_no ="SF3168066551472"
checkPhoneNo=6852
sf_client = SF(clientcode, checkword)
order_result:dict = sf_client.order.get_route_info(
    trackingNumber=order_no,
    checkPhoneNo=checkPhoneNo,

)
routes = order_result.get("msgData", {}).get("routeResps", [{}])[0].get("routes", [])
# 格式化输出

for node in sorted(routes, key=lambda x: x['acceptTime']):
    print(f"时间：{node['acceptTime']}")
    print(f"地点：{node['acceptAddress']} | 状态：{node['firstStatusName']}-{node['secondaryStatusName']}")
    print(f"详情：{node['remark']}\n{'-'*50}")


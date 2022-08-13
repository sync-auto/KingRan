#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
cron: 1 1 1 1 *
new Env('发财挖宝');
活动入口: 京东极速版 > 我的 > 发财挖宝
最高可得总和为10元的微信零钱和红包
脚本功能为: 挖宝，提现，没有助力功能，当血量剩余 1 时停止挖宝，领取奖励并提现 

目前需要完成逛一逛任务并且下单任务才能通关，不做的话大概可得1.5～2块的微信零钱
'''
import os,json,random,time,re,string,functools,asyncio
import sys
sys.path.append('../../tmp')
print('\n运行本脚本之前请手动进入游戏点击一个方块\n')
print('\n挖的如果都是0.01红包就是黑了，别挣扎了！\n')
print('\n默认自动领取奖励，关闭请在代码383行加上#号注释即可\n')
try:
    import requests
except Exception as e:
    print(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")
requests.packages.urllib3.disable_warnings()


linkId="pTTvJeSTrpthgk9ASBVGsw"


# 获取pin
cookie_findall=re.compile(r'pt_pin=(.+?);')
def get_pin(cookie):
    try:
        return cookie_findall.findall(cookie)[0]
    except:
        print('ck格式不正确，请检查')

# 读取环境变量
def get_env(env):
    try:
        if env in os.environ:
            a=os.environ[env]
        elif '/ql' in os.path.abspath(os.path.dirname(__file__)):
            try:
                a=v4_env(env,'/ql/config/config.sh')
            except:
                a=eval(env)
        elif '/jd' in os.path.abspath(os.path.dirname(__file__)):
            try:
                a=v4_env(env,'/jd/config/config.sh')
            except:
                a=eval(env)
        else:
            a=eval(env)
    except:
        a=''
    return a

# v4
def v4_env(env,paths):
    b=re.compile(r'(?:export )?'+env+r' ?= ?[\"\'](.*?)[\"\']', re.I)
    with open(paths, 'r') as f:
        for line in f.readlines():
            try:
                c=b.match(line).group(1)
                break
            except:
                pass
    return c 


# 随机ua
def ua():
    sys.path.append(os.path.abspath('.'))
    try:
        from jdEnv import USER_AGENTS as a
    except:
        a='jdpingou;android;5.5.0;11;network/wifi;model/M2102K1C;appBuild/18299;partner/lcjx11;session/110;pap/JA2019_3111789;brand/Xiaomi;Mozilla/5.0 (Linux; Android 11; M2102K1C Build/RKQ1.201112.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36'
    return a

# 13位时间戳
def gettimestamp():
    return str(int(time.time() * 1000))

## 获取cooie
class Judge_env(object):
    def main_run(self):
        if '/jd' in os.path.abspath(os.path.dirname(__file__)):
            cookie_list=self.v4_cookie()
        else:
            cookie_list=os.environ["JD_COOKIE"].split('&')       # 获取cookie_list的合集
        if len(cookie_list)<1:
            print('请填写环境变量JD_COOKIE\n')    
        return cookie_list

    def v4_cookie(self):
        a=[]
        b=re.compile(r'Cookie'+'.*?=\"(.*?)\"', re.I)
        with open('/jd/config/config.sh', 'r') as f:
            for line in f.readlines():
                try:
                    regular=b.match(line).group(1)
                    a.append(regular)
                except:
                    pass
        return a
cookie_list=Judge_env().main_run()   


def taskGetUrl(functionId, body, cookie):
    url=f'https://api.m.jd.com/?functionId={functionId}&body={json.dumps(body)}&t={gettimestamp()}&appid=activities_platform&client=H5&clientVersion=1.0.0'
    headers={
        'Cookie': cookie,
        'Host': 'api.m.jd.com',
        'Connection': 'keep-alive',
        'origin': 'https://bnzf.jd.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'accept': 'application/json, text/plain, */*',
        "User-Agent": ua(),
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    for n in range(3):
        try:
            res=requests.get(url,headers=headers, timeout=10).json()
            return res
        except:
            if n==2:
                print('API请求失败，请检查网路重试❗\n')   


# 剩余血量
def xueliang(cookie):
    body={"linkId":linkId,"round":1}
    res=taskGetUrl("happyDigHome", body, cookie)
    if not res:
        return
    if res['code']==0:
        if res['success']:
            curRound=res['data']['curRound']                        # 未知
            blood=res['data']['blood']                              # 剩余血量
            return blood      

def jinge(cookie,i):
    body={"linkId":linkId}
    res=taskGetUrl("happyDigHome", body, cookie)
    if not res:
        return
    if res['code']==0:
        if res['success']:
            curRound=res['data']['curRound']                        # 未知
            blood=res['data']['blood']                              # 剩余血量
            roundList=res['data']['roundList']                      # 3个总池子
            roundList_n=roundList[0]
            redAmount=roundList_n['redAmount']                  # 当前池已得京东红包
            cashAmount=roundList_n['cashAmount']                # 当前池已得微信红包

            return [blood,redAmount,cashAmount]   

# 页面数据
def happyDigHome(cookie):
    body={"linkId":linkId,"round":1}
    res=taskGetUrl("happyDigHome", body, cookie)
    exit_flag = "false"
    if not res:
        return
    if res['code']==0:
        if res['success']:
            curRound=res['data']['curRound']                        # 未知
            incep_blood=res['data']['blood']                        # 剩余血量
            roundList=res['data']['roundList']                      # 3个总池子
            for e,roundList_n in enumerate(roundList):              # 迭代每个池子
                roundid=roundList_n['round']                        # 池序号
                state=roundList_n['state'] 
                rows=roundList_n['rows']                            # 池规模，rows*rows
                redAmount=roundList_n['redAmount']                  # 当前池已得京东红包
                cashAmount=roundList_n['cashAmount']                # 当前池已得微信红包
                leftAmount=roundList_n['leftAmount']                # 剩余红包？
                chunks=roundList_n['chunks']                        # 当前池详情list

                a=jinge(cookie,roundid)
                if roundid==1:
                    print(f'\n开始 "入门" 难度关卡（{rows}*{rows}）')
                elif roundid==2:
                    print(f'\n开始 "挑战" 难度关卡（{rows}*{rows}）')
                elif roundid==3:
                    print(f'\n开始 "终极" 难度关卡（{rows}*{rows}）')
                print(f'当前剩余血量 {a[0]}🩸')
                ## print(f'当前池已得京东红包 {a[2]}\n当前池已得微信红包 {a[1]}\n')
                _blood=xueliang(cookie)
                if _blood>1  or incep_blood>=21:
                    happyDigDo(cookie,roundid,0,0)
                    if e==0 or e==1:
                        roundid_n=4
                    else:
                        roundid_n=5
                    for n in range(roundid_n):
                        for i in range(roundid_n):
                            _blood=xueliang(cookie)
                            if _blood>1 or incep_blood>=21:
                                ## print(f'当前血量为 {_blood}')
                                a=n+1
                                b=i+1
                                print(f'挖取坐标({a},{b})')
                                happyDigDo(cookie,roundid,n,i)
                            else:
                                a=jinge(cookie,roundid)
                                print(f'没血了，不挖了')
                                exit_flag = "true"
                                ## print(f'当前池已得京东红包 {a[2]}\n当前池已得微信红包 {a[1]}\n')
                                break

                        if exit_flag == "true":
                            break
                if exit_flag == "true":
                    break
        else:
            print(f'获取数据失败\n{res}\n')
    else:
        print(f'获取数据失败\n{res}\n')


 # 玩一玩
def apDoTask(cookie):
     print('开始做玩一玩任务')
     body={"linkId":linkId,"taskType":"BROWSE_CHANNEL","taskId":840,"channel":4,"itemId":"https%3A%2F%2Fprodev.m.jd.com%2Fjdlite%2Factive%2FeVgKdaU5TKnGZfSWCRe79hqfLXp%2Findex.html","checkVersion":False}
     res=taskGetUrl('apDoTask', body, cookie)
     if not res:
         return
     try:    
         if res['success']:
             print('玩好了')
         else:
             print(f"{res['errMsg']}")
     except:
         print(f"错误\n{res}")
    

# 挖宝
def happyDigDo(cookie,roundid,rowIdx,colIdx):
    body={"round":roundid,"rowIdx":rowIdx,"colIdx":colIdx,"linkId":linkId}
    res=taskGetUrl("happyDigDo", body, cookie)
    if not res:
        return
    if res['code']==0:
        if res['success']:
            typeid=res['data']['chunk']['type']
            if typeid==2:
                print(f"获得极速版红包 {res['data']['chunk']['value']} 🧧\n")
            elif typeid==3:
                print(f"🎉 获得微信零钱 {res['data']['chunk']['value']} 💰\n")
            elif typeid==4:
                print(f"💥Boom💥 挖到了炸弹 💣\n")
            elif typeid==1:
                print(f"获得优惠券 🎟️\n")
            else:
                print(f'不知道挖到了什么 🎁\n')
        else:
            print(f'{res}\n挖宝失败\n')
    else:
        print(f'{res}\n挖宝失败\n')

# # 助力码
# def inviteCode(cookie):
#     global inviteCode_1_list,inviteCode_2_list
#     body={"linkId":linkId}
#     res=taskGetUrl("happyDigHome", body, cookie)
#     if not res:
#         return
#     try:
#         if res['success']:
#             print(f"账号{get_pin(cookie)}助力码为{res['data']['inviteCode']}")
#             inviteCode_1_list.append(res['data']['inviteCode'])
#             print(f"账号{get_pin(cookie)}助力码为{res['data']['markedPin']}")
#             inviteCode_2_list.append(res['data']['markedPin'])
#         else:
#             print('快去买买买吧')
#     except:
#         print(f"错误\n{res}\n")

# # 助力
# def happyDigHelp(cookie,fcwbinviter,fcwbinviteCode):
#     print(f"账号 {get_pin(cookie)} 去助力{fcwbinviteCode}")
#     xueliang(cookie)
#     body={"linkId":linkId,"inviter":fcwbinviter,"inviteCode":fcwbinviteCode}
#     res=taskGetUrl("happyDigHelp", body, cookie)
#     if res['success']:
#         print('助力成功')
#     else:
#         print(res['errMsg'])

# 领取奖励
def happyDigExchange(cookie):
    for n in range(1,4):
        xueliang(cookie)
        print(f"\n开始领取第{n}场的奖励")
        body={"round":n,"linkId":linkId}
        res=taskGetUrl("happyDigExchange", body, cookie)
        if not res:
            return
        if res['code']==0:
            if res['success']:
                try:
                    print(f"已领取极速版红包 {res['data']['redValue']} 🧧")
                except:
                    print('')
                if res['data']['wxValue'] != "0":
                    try:
                        print(f"可提现微信零钱 {res['data']['wxValue']} 💰")
                    except:
                        pass
            else:
                print(res['errMsg'])
        else:
            print(res['errMsg'])



# 微信现金id
def spring_reward_list(cookie):
    happyDigExchange(cookie)
    xueliang(cookie)
    
    body={"linkId":linkId,"pageNum":1,"pageSize":6}
    res=taskGetUrl("spring_reward_list", body, cookie)
    
    if res['code']==0:
        if res['success']:
            items=res['data']['items']
            for _items in items:
                amount=_items['amount']         # 金额
                prizeDesc=_items['prizeDesc']   # 金额备注
                amountid=_items['id']           # 金额id
                poolBaseId=_items['poolBaseId']
                prizeGroupId=_items['prizeGroupId']
                prizeBaseId=_items['prizeBaseId']
                if '红包' in f"{prizeDesc}":
                    continue
                if '券' in f"{prizeDesc}":
                    continue
                else:
                    print('\n去提现微信零钱 💰')
                    time.sleep(3.2)
                    wecat(cookie,amountid,poolBaseId,prizeGroupId,prizeBaseId)
        else:
            print(f'获取数据失败\n{res}\n')
    else:
        print(f'获取数据失败\n{res}\n')

# 微信提现
def wecat(cookie,amountid,poolBaseId,prizeGroupId,prizeBaseId):
    xueliang(cookie)
    
    url='https://api.m.jd.com'
    headers={
        'Cookie': cookie,
        'Host': 'api.m.jd.com',
        'Connection': 'keep-alive',
        'origin': 'https://bnzf.jd.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": ua(),
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    body={"businessSource":"happyDiggerH5Cash","base":{"id":amountid,"business":"happyDigger","poolBaseId":poolBaseId,"prizeGroupId":prizeGroupId,"prizeBaseId":prizeBaseId,"prizeType":4},"linkId":linkId}
    data=f"functionId=apCashWithDraw&body={json.dumps(body)}&t=1635596380119&appid=activities_platform&client=H5&clientVersion=1.0.0"
    for n in range(3):
        try:
            res=requests.post(url,headers=headers,data=data,timeout=10).json()
            break
        except:
            if n==2:
                print('API请求失败，请检查网路重试❗\n') 
    try:
        if res['code']==0:
            if res['success']:
                print(res['data']['message']+'\n')
    except:
        print(res)
        print('')
    

def main():
    print('🔔发财挖宝，开始！\n')

    # print('获取助力码\n')
    # global inviteCode_1_list,inviteCode_2_list
    # inviteCode_1_list=list()
    # inviteCode_2_list=list()
    # for cookie in cookie_list:
    #    inviteCode(cookie) 

    # print('互助\n')
    # inviteCode_2_list=inviteCode_2_list[:2]
    # for e,fcwbinviter in enumerate(inviteCode_2_list):
    #     fcwbinviteCode=inviteCode_1_list[e]
    #     for cookie in cookie_list:
    #         happyDigHelp(cookie,fcwbinviter,fcwbinviteCode)

    print(f'====================共{len(cookie_list)}京东个账号Cookie=========\n')

    for e,cookie in enumerate(cookie_list,start=1):
        print(f'******开始【账号 {e}】 {get_pin(cookie)} *********\n')
        apDoTask(cookie)
        happyDigHome(cookie)
        spring_reward_list(cookie)


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
# Time       : 2021/12/16 21:53
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: SSPanel-Uim 人机验证案例

# ==============================================
# TODO [√]用于项目演示的运行实例，（也许）需要使用代理
# ==============================================
# - `anti_recaptcha` 表示需要人机验证
# - 无标记实例为对照组
ActionNiuBiCloud = {
    "register_url": "https://niubi.cyou/auth/register",
}
ActionLoLiCloud = {
    "register_url": "https://lo-li.xyz/auth/register",
    "hyper_params": {"anti_recaptcha": True, "usr_email": True}
}
ActionGsouCloud = {
    "register_url": "https://gsoula.cloud/auth/register",
    "hyper_params": {"anti_recaptcha": True, }
}
# ==============================================
# TODO [√]运行前请检查 chromedriver 配置
# ==============================================
from examples import demo_recaptcha2walk

if __name__ == '__main__':
    demo_recaptcha2walk(
        # 无验证对照组
        # atomic=ActionNiuBiCloud,

        # 人机验证实验组
        atomic=ActionLoLiCloud,
        # atomic=ActionGsouCloud,

        # 控制台参数 保持默认即可
        penetrate=True,
        silence=False,
    )

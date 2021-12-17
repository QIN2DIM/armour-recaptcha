# -*- coding: utf-8 -*-
# Time       : 2021/12/16 21:54
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import time

from src.config import logger, DIR_RUNTIME_CACHE
from ._base import CatWalk


class Recaptcha2Walk(CatWalk):
    def __init__(self, register_url: str, silence: bool = False, hyper_params: dict = None, penetrate=False,
                 dir_runtime_cache: str = None):
        super(Recaptcha2Walk, self).__init__(register_url, silence=silence, penetrate=penetrate,
                                             dir_runtime_cache=dir_runtime_cache)

        self.hyper_params = {
            "anti_recaptcha": False,
            "usr_email": False,
        }
        if hyper_params:
            self.hyper_params.update(hyper_params)
        self.usr_email = self.hyper_params["usr_email"]
        self.anti_recaptcha = self.hyper_params["anti_recaptcha"]

    def go(self):
        # 检测实例状态
        if not self.check_heartbeat():
            return

        # 获取任务设置
        api = self.set_spider_option()
        try:
            # 弹性访问
            self.get_html_handle(api, url=self.register_url)

            # 注册账号
            self.sign_up(api)

            logger.success("实例运行完毕，10s后退出程序。")
            time.sleep(10)
        finally:
            api.quit()


@logger.catch()
def demo_recaptcha2walk(atomic: dict, silence: bool = False, penetrate: bool = None):
    """

    :param atomic:
    :param silence:
    :param penetrate: 若短时间内实验次数过多 导致 reCAPTCHA 阻断访问，可以使用该参数激活无痕实例
                    -->该参数已弃用，无痕实例并不能躲避风控
    :return:
    """
    logger.info("加载运行实例 - atomic={}".format(atomic))

    e2w = Recaptcha2Walk(
        silence=silence,
        penetrate=penetrate,
        register_url=atomic.get("register_url"),
        hyper_params=atomic.get("hyper_params"),
        dir_runtime_cache=DIR_RUNTIME_CACHE,

    )

    e2w.go()

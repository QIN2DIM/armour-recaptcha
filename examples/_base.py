# -*- coding: utf-8 -*-
# Time       : 2021/12/16 21:54
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 用于运行实例的调度框架
import os.path
import random
import time
from string import printable

import requests
from requests.exceptions import (
    ConnectionError,
    SSLError,
    HTTPError,
    Timeout,
    ProxyError
)
from selenium.common.exceptions import (
    WebDriverException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException
)
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located
)
from selenium.webdriver.support.wait import WebDriverWait

from src.armour import activate_recaptcha, submit_recaptcha, handle_audio, parse_audio
from src.config import logger


class CatWalk:
    def __init__(
            self, register_url: str, silence: bool = None, anti_recaptcha: bool = None,
            usr_email: bool = None, chromedriver_path: str = None, penetrate: bool = None,
            dir_runtime_cache: str = None
    ):
        self.register_url = register_url

        self.silence = bool(silence)
        self.anti_recaptcha = bool(anti_recaptcha)
        self.usr_email = bool(usr_email)
        self.chromedriver_path = "chromedriver" if chromedriver_path is None else chromedriver_path
        self.dir_runtime_cache = os.path.dirname(__file__) if dir_runtime_cache is None else dir_runtime_cache
        self.penetrate = bool(penetrate)

        self.username, self.password, self.email = "", "", ""
        self.email_class = "@gmail.com"
        self.beat_dance = 0
        self.timeout_retry_time = 3

    def set_spider_option(self):
        options = ChromeOptions()
        if self.silence:
            options.add_argument("--headless")
        options.add_argument("user-agent={Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                             " Chrome/60.0.3112.50 Safari/537.36}")
        return Chrome(options=options, executable_path=self.chromedriver_path)

    def check_heartbeat(self):
        url = self.register_url
        session = requests.session()
        try:
            response = session.get(url, timeout=5)
            if response.status_code > 400:
                logger.error(f"站点异常 - url={url} status_code={response.status_code} ")
                return False
            return True
        # 站点被动行为，流量无法过墙
        except ConnectionError:
            logger.error(f"流量阻断 - url={url}")
            return False
        # 站点主动行为，拒绝国内IP访问
        except (SSLError, HTTPError, ProxyError):
            logger.warning(f"代理异常 - url={url}")
            return False
        # 站点负载紊乱或主要服务器已瘫痪
        except Timeout:
            logger.error(f"响应超时 - url={url}")
            return False

    @staticmethod
    def get_html_handle(api: Chrome, url, wait_seconds: int = 15):
        api.set_page_load_timeout(time_to_wait=wait_seconds)
        api.get(url)

    def generate_account(self, email_class: str = "@qq.com"):
        # 账号信息
        username = "".join(
            [random.choice(printable[: printable.index("!")]) for _ in range(9)]
        )
        password = "".join(
            [random.choice(printable[: printable.index(" ")]) for _ in range(15)]
        )

        # 根据实例特性生成 faker email object
        # 若不要求验证邮箱，使用随机字节码，否则使用备用方案生成可接受验证码的邮箱对象
        if not self.usr_email:
            email = username
        else:
            email = username + email_class
        return username, password, email

    def utils_recaptcha(self, api: Chrome):
        """
        处理 SSPanel 中的 Google reCAPTCHA v2 Checkbox 人机验证。

        使用音频声纹识别验证而非直面图像识别。

        > 无论站点本身可否直连访问，本模块的执行过程的流量必须过墙，否则音频文件的下载及转码必然报错。
        > 可能的异常有:
         - speech_recognition.RequestError
         - http.client.IncompleteRead

        :param api:
        :return:
        """
        time.sleep(random.randint(2, 4))

        # 激活 reCAPTCHA 并获取音频文件下载链接
        audio_url: str = activate_recaptcha(api)

        # Google reCAPTCHA 风控
        if not audio_url:
            logger.error("运行实例已被风控。\n"
                         "可能原因及相关建议如下：\n"
                         "1.目标站点可能正在遭受流量攻击，请更换测试用例；\n"
                         "2.代理IP可能已被风控，建议关闭代理运行或更换代理节点；\n"
                         "3.本机设备所在网络正在传输恶意流量，建议切换网络如切换WLAN。\n"
                         ">>> https://developers.google.com/recaptcha/docs/faq#"
                         "my-computer-or-network-may-be-sending-automated-queries")
            raise WebDriverException

        # 音频转码 （MP3 --> WAV） 增加识别精度
        path_audio_wav: str = handle_audio(audio_url=audio_url, dir_audio_cache=self.dir_runtime_cache)
        logger.success("Handle Audio - path_audio_wav=`{}`".format(path_audio_wav))

        # 声纹识别 --(output)--> 文本数据
        # speech_recognition.RequestError 需要挂起代理
        # http.client.IncompleteRead 网速不佳，音频文件未下载完整就开始解析
        answer: str = parse_audio(path_audio_wav)
        logger.success("Parse Audio - answer=`{}`".format(answer))

        # 定位输入框并填写文本数据
        response = submit_recaptcha(api, answer=answer)
        if not response:
            logger.error("Submit reCAPTCHA answer.")
            raise TimeoutException

    def sign_up(self, api: Chrome):
        self.username, self.password, self.email = self.generate_account(self.email_class)

        while True:
            # 实验环境下无需关心循环正常退出的条件
            # 生产环境下建议加入超时判断从外部中断循环

            # ======================================
            # 填充注册数据
            # ======================================
            time.sleep(0.5 + self.beat_dance)
            try:
                WebDriverWait(api, 20).until(
                    presence_of_element_located((By.ID, "name"))
                ).send_keys(self.username)

                email_ = api.find_element(By.ID, "email")
                passwd_ = api.find_element(By.ID, "passwd")
                repasswd_ = api.find_element(By.ID, "repasswd")
                email_.clear()
                email_.send_keys(self.email)
                passwd_.clear()
                passwd_.send_keys(self.password)
                repasswd_.clear()
                repasswd_.send_keys(self.password)
            except (ElementNotInteractableException, WebDriverException, TimeoutException):
                time.sleep(0.5 + self.beat_dance)
                continue

            # ======================================
            # 依据实体抽象特征，选择相应的解决方案
            # ======================================
            # 人机声纹验证
            if self.anti_recaptcha:
                try:
                    self.utils_recaptcha(api)
                    # 回到 main-frame 否则后续DOM操作无法生效
                    api.switch_to.default_content()
                except TimeoutException:
                    time.sleep(0.5 + self.beat_dance)
                    continue
                # Google reCAPTCHA 风控
                except WebDriverException:
                    exit()
            # ======================================
            # 提交注册数据，完成注册任务
            # ======================================
            # 点击注册按键
            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.ID, "register-confirm").click()
                except (ElementNotInteractableException, WebDriverException):
                    time.sleep(self.timeout_retry_time + self.beat_dance)
                    continue

            time.sleep(0.5)
            for _ in range(3):
                try:
                    api.find_element(By.XPATH, "//button[contains(@class,'confirm')]").click()
                    return True
                except NoSuchElementException:
                    time.sleep(self.timeout_retry_time + self.beat_dance)
                    continue
            else:
                api.refresh()
                self.sign_up(api)

    def go(self):
        """

        :return:
        """
        raise ImportError

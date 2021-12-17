# -*- coding: utf-8 -*-
# Time       : 2021/12/16 21:56
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import os
import time
import urllib
from random import randint
from time import sleep
from urllib.request import urlretrieve

import pydub
from selenium.common.exceptions import (
    NoSuchElementException
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from speech_recognition import Recognizer, AudioFile


def activate_recaptcha(api: Chrome) -> str:
    """
    激活 reCAPTCHA 人机验证，并跳转至声纹识别界面，返回声源文件的下载地址

    :param api: 为了消除 driver 指纹特征，可在高并发场景使用  undetected_chromedriver.v2 替代 selenium
    :return:
    """
    # 定位并切换至 reCAPTCHA iframe
    recaptcha_iframe = WebDriverWait(api, 10).until(presence_of_element_located((
        By.XPATH, "//iframe[@title='reCAPTCHA']"
    )))
    api.switch_to.frame(recaptcha_iframe)

    # 点击并激活 recaptcha
    api.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()

    # 回到 main_frame
    api.switch_to.default_content()

    # 切换到 main_frame 中的另一个 frame
    api.switch_to.frame(api.find_element(By.XPATH, "//iframe[@title='reCAPTCHA 验证将于 2 分钟后过期']"))

    sleep(randint(2, 4))

    # 点击切换到声纹识别界面
    api.find_element(By.ID, "recaptcha-audio-button").click()

    sleep(randint(2, 4))

    # 点击播放按钮
    try:
        api.find_element(By.XPATH, "//button[@aria-labelledby]").click()
    except NoSuchElementException:
        return ""

    # 定位声源文件 url
    audio_url = api.find_element(By.ID, "audio-source").get_attribute("src")

    return audio_url


def handle_audio(audio_url: str, dir_audio_cache: str) -> str:
    """
    reCAPTCHA Audio 音频文件的定位、下载、转码

    :param audio_url: reCAPTCHA Audio 链接地址
    :param dir_audio_cache: 音频缓存目录
    :return:
    """
    # 拼接音频缓存文件路径
    timestamp_ = int(time.time())
    path_audio_mp3 = os.path.join(dir_audio_cache, f"audio_{timestamp_}.mp3")
    path_audio_wav = os.path.join(dir_audio_cache, f"audio_{timestamp_}.wav")

    # 将声源文件下载到本地
    urllib.request.urlretrieve(audio_url, path_audio_mp3)

    # 转换音频格式 mp3 --> wav
    pydub.AudioSegment.from_mp3(path_audio_mp3).export(path_audio_wav, format="wav")

    # 返回 wav 格式的音频文件 增加识别精度
    return path_audio_wav


def parse_audio(path_audio_wav: str, language: str = None) -> str:
    """
    声纹识别，音频转文本

    :param path_audio_wav: reCAPTCHA Audio 音频文件的本地路径（wav格式）
    :param language: 音频文件的国际化语言格式，默认 en-US 美式发音。非必要参数，但可增加模型精度。
    :return:
    """
    language = "en-US" if language is None else language

    # 将音频读入并切割成帧矩阵
    recognizer = Recognizer()
    audio_file = AudioFile(path_audio_wav)
    with audio_file as stream:
        audio = recognizer.record(stream)

    # 流识别
    answer: str = recognizer.recognize_google(audio, language=language)

    # 返回短音频对应的文本(str)，en-US 情况下为不成句式的若干个单词
    return answer


def submit_recaptcha(api: Chrome, answer: str) -> bool:
    """
    提交 reCAPTCHA 人机验证，需要传入 answer 文本信息，需要 action 停留在可提交界面

    :param api: 为了消除 driver 指纹特征，可在高并发场景使用  undetected_chromedriver.v2 替代 selenium
    :param answer: 声纹识别数据
    :return:
    """
    try:
        # 定位回答框
        input_field = api.find_element(By.ID, "audio-response")

        # 提交文本数据
        input_field.clear()
        input_field.send_keys(answer.lower())

        # 使用 clear + ENTER 消除控制特征
        input_field.send_keys(Keys.ENTER)

        return True
    except (NameError, NoSuchElementException):
        return False

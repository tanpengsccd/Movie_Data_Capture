# ConfigModel.py
# 用于逐渐代替confiy.py的文件, 配置转模型会减少硬代码的编写.
# 使用GPT3.5 指令生成pydantic模型: 
'''
    把下面的ini内容转为 python3 class模型, 只要模型 section 和 key ,不要赋值,  内部嵌套Section Class.
以下下面的代码开始
```
class RootConfig(BaseModel):
    class CommonConfig(BaseModel):
        main_mode: int
```
下面是 ini 内容
```
...(ini内容复制来)...
```
'''

import configparser
from enum import Enum 
from pydantic import BaseModel,Field, validator


class ConfigModel(BaseModel):
    @staticmethod
    def getConfig(configIniPath:str):
        """静态方法:读取ini配置转为模型"""
        # configparser 读取配置
        ConfigParser = configparser.ConfigParser()
        ConfigParser.read(configIniPath, encoding='utf-8')
        # 字典推导式（Dictionary Comprehension）:
        # 格式通常是 {key: value for item in iterable}，其中iterable是一个可迭代对象，key和value是每次迭代产生的字典的键和值。
        config_data = {section: dict(ConfigParser.items(section)) for section in ConfigParser.sections()}
        # pydantic的 dict 转 模型实例 
        return ConfigModel(**config_data)
       
     
    class CommonConfig(BaseModel):
        class Main_Mode(Enum):
            Scraping = 'scraping'
            Organizing = 'organizing'
            ScrapingInAnalysisFolder = 'scrapingInAnalysisFolder'

        main_mode: Main_Mode
        source_folder: str
        test_movie_list: str = None
        only_jp_code_number: int = Field(default=0)
        failed_output_folder: str
        success_output_folder: str
        link_mode: int
        scan_hardlink: int
        failed_move: int
        auto_exit: int
        translate_to_sc: int
        multi_threading: int
        actor_gender: str
        del_empty_folder: int
        nfo_skip_days: int
        ignore_failed_list: int
        download_only_missing_images: int
        mapping_table_validity: int
        jellyfin: int
        actor_only_tag: int
        sleep: int
        anonymous_fill: int
        
        # 定制main_mode 字段 的验证器(解析器)
        @validator('main_mode',pre=True)
        def main_mode_valid(cls, v):
            if v == '1':
                return cls.Main_Mode.Scraping
            elif v == '2':
                return cls.Main_Mode.Organizing
            elif v == '3':
                return cls.Main_Mode.ScrapingInAnalysisFolder
            elif isinstance(v,str) and v.lower() in cls.Main_Mode.__members__:
                return cls.Main_Mode(v.lower())
            else:
                raise ValueError('main_mode must be ' + ' or '.join([f'"{e.value}"' for e in cls.Main_Mode]))
        
    class AdvencedSleepConfig(BaseModel):
        stop_counter: int = 0
        rerun_delay: int = 0

    class ProxyConfig(BaseModel):
        switch: int
        type: str
        proxy: str
        timeout: int
        retry: int
        cacert_file: str

    class NameRuleConfig(BaseModel):
        location_rule: str
        naming_rule: str
        max_title_len: int
        image_naming_with_number: int
        number_uppercase: int
        number_regexs: str

    class UpdateConfig(BaseModel):
        update_check: int

    class PriorityConfig(BaseModel):
        website: str

    class EscapeConfig(BaseModel):
        literals: str
        folders: str

    class DebugModeConfig(BaseModel):
        switch: int

    class TranslateConfig(BaseModel):
        switch: int
        engine: str
        target_language: str
        key: str
        delay: int
        values: str
        service_site: str

    class TrailerConfig(BaseModel):
        switch: int

    class UncensoredConfig(BaseModel):
        uncensored_prefix: str

    class MediaConfig(BaseModel):
        media_type: str
        sub_type: str

    class WatermarkConfig(BaseModel):
        switch: int
        water: int

    class ExtrafanartConfig(BaseModel):
        switch: int
        parallel_download: int
        extrafanart_folder: str

    class StorylineConfig(BaseModel):
        switch: int
        site: str
        censored_site: str
        uncensored_site: str
        run_mode: int
        show_result: int

    class CCConvertConfig(BaseModel):
        mode: int
        vars: str

    class JavdbConfig(BaseModel):
        sites: int

    class FaceConfig(BaseModel):
        locations_model: str
        uncensored_only: int
        aways_imagecut: int
        aspect_ratio: float

    class JellyfinConfig(BaseModel):
        multi_part_fanart: int

    class ActorPhotoConfig(BaseModel):
        download_for_kodi: int

    class DirectConfig(BaseModel):
        switch: int

    common: CommonConfig
    advenced_sleep: AdvencedSleepConfig
    proxy: ProxyConfig
    Name_Rule: NameRuleConfig
    update: UpdateConfig
    priority: PriorityConfig
    escape: EscapeConfig
    debug_mode: DebugModeConfig
    translate: TranslateConfig
    trailer: TrailerConfig
    uncensored: UncensoredConfig
    media: MediaConfig
    watermark: WatermarkConfig
    extrafanart: ExtrafanartConfig
    storyline: StorylineConfig
    cc_convert: CCConvertConfig
    javdb: JavdbConfig
    face: FaceConfig
    jellyfin: JellyfinConfig
    actor_photo: ActorPhotoConfig
    direct: DirectConfig
    

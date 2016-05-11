# -*- coding: utf-8 -*-
import json

LOAD_MODULES = [
           "pre_analysis",
           "industry",
           "classifier_v2",
           "brand_name_new",
           "gender",
           "age",
           "price_level",
           "districts_city",
           "number_of_people",
           "pst_analysis",
           "item_tag_nonstd"
           ]

DEFAULT = ["industry",
           "classifier_v2",
           "brand_name_new",
           "gender",
           "age",
           "price_level",
           "districts_city",
           "number_of_people",
           "item_tag_nonstd"
           ]

modules = {"number_of_people":{"type":"python", "path":"portrayal_server.modules.num_of_people.number_of_people.NumberOfPeople","enable":True},
"age":{"type":"python", "path":"portrayal_server.modules.age_.age.Age", "enable":True},
"industry":{"type":"python", "path":"portrayal_server.modules.industry.industry.Industry", "enable":True},
"classifier_v2":{"type":"python", "path":"portrayal_server.modules.classifier_v2.ClassTreePredict.Classifier", "enable":True},
"brand_name_new":{"type":"python", "path":"portrayal_server.modules.bfd_brand.brand_name_new.Brand", "enable":True},
"gender":{"type":"python", "path":"portrayal_server.modules.gender_.gender.GenderRun", "enable":True},
"price_level":{"type":"python", "path":"portrayal_server.modules.price_level.price_level.PriceLevel", "enable":True},
"pre_analysis":{"type":"python", "path":"portrayal_server.modules.pre_analysis.pre_analyser.PreAnalyser", "enable":True},
"pst_analysis":{"type":"python", "path":"portrayal_server.modules.pst_analysis.pst_analyser.PstAnalyser", "enable":True},
"districts_city":{"type":"python", "path":"portrayal_server.modules.district.districts_city.DistrictCity", "enable":True},
"item_tag_nonstd":{"type":"python", "path":"portrayal_server.modules.item_tag_nonstd.item_tag_nonstd.ItemTagNonStd", "enable":True}}


def get_data():
    data = {}
    module_line_ = {}
    modules_={}
    module_line_["default"] = DEFAULT
    for key,value in module_line_.items():
        for item in value:
            if item not in modules_:
                modules_[item] = modules[item]

    for i in LOAD_MODULES:
        if i not in modules_:
            modules_[i] = modules[i]
        
    data["module_lines"] = module_line_
    data["modules"] = modules_ 
    return data

def create_file():
    with open("modules.json","w") as fd:
        data = get_data()
        data_str = json.dumps(data)
        fd.write(data_str)
    
def read_file():
    with open("modules.json","r") as fd:
        data = json.load(fd)
        print(data)

create_file()
read_file()

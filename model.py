#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 20:51
# @Author  : Derek.S
# @Site    : 
# @File    : model.py

from app import mongo
from flask_pymongo import DESCENDING


from math import ceil
import json


def init_idRecode():
    """
    初始化自定义自增id
    :return:
    """
    initID = {
        'id': 0
    }
    dbCollectTest = mongo.db.collection_names()
    if "IPRMS_idRecode" not in dbCollectTest:
        try:
            mongo.db.IPRMS_idRecode.insert_one(initID)
            status = 0
        except:
            status = 1
    else:
        status = 1
    return status


def getID():
    """
    获取自定义ID的值
    :return:
    """
    id = mongo.db.IPRMS_idRecode.find_one()["id"] + 1
    return id


def setLimit(limit=20):
    """
    设置分页参数
    :param limit: int limit num
    :return: None
    """
    limitDict = {
        "sysOption": "limitNum",
        "limitNum": limit
    }
    try:
        limitNum = mongo.db.IPRMS_System.find_one({"sysOption": "limitNum"})
        if(not limitNum):
            mongo.db.IPRMS_System.insert_one(limitDict)
        else:
            mongo.db.IPRMS_System.update_one({"sysOption": "limitNum"}, {"$set": {"limitNum": limit}})
        status = {
            "status": 1
        }
    except Exception as e:
        print(e)
        status = {
            "status": 0
        }
    return json.dumps(status)


def getSystem():
    """
    取系统设置参数
    :return:  int limit num
    """
    option = {}
    try:
        limitNum = mongo.db.IPRMS_System.find_one({"sysOption": "limitNum"})["limitNum"]
        option["limitNum"] = int(limitNum)
    except Exception as e:
        print(e)
    return option


def setProvinces(ProvincesData):
    """
    添加行政区划信息 仅支持到地市一级
    :param ProvincesData: Dict Data
    :return:
    """
    try:
        ProvinceID = mongo.db.IPRMS_idRecode.find_one({"Collection_ID": "IPRMS_Provinces"})["id"]
        for eachProvince in ProvincesData:
            eachProvince["ID"] = ProvinceID
            ProvinceID += 1
        mongo.db.IPRMS_idRecode.update({"Collection_ID": "IPRMS_Provinces"}, {"$set": {"id": ProvinceID}})
        mongo.db.IPRMS_Provinces.insert_many(ProvincesData)
        status = {
            "status": 1
        }
    except Exception as e:
        print(e)
        status = {
            "status": 0
        }
    return json.dumps(status)


def provincesViews():
    """
    查看行政区划数据
    :return:
    """
    limitNum = mongo.db.IPRMS_System.find_one({"sysOption": "limitNum"})["limitNum"]
    try:
        provincesData = mongo.db.IPRMS_Provinces.find({})
        totalPNum = ceil(provincesData.count() / limitNum)
        return provincesData, totalPNum
    except Exception as e:
        print(e)


def getIPRes():
    pass


class Pagination:
    def __init__(self, items, page, per_page, total_items):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total_items = total_items
        self.num_pages = int(ceil(total_items / per_page))

    @property
    def has_next(self):
        return self.page < self.num_pages

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def next_page(self):
        return self.page + 1

    @property
    def prev_page(self):
        return self.page - 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.num_pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and \
                     num < self.page + right_current) or \
                    num > self.num_pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def paginate(queryset, page=1):
    """
    分页
    :param queryset: 查询数据集
    :param page: 页码
    :return: 分页信息
    """
    per_page = mongo.db.IPRMS_System.find_one({"sysOption": "limitNum"})["limitNum"]
    skip  = (page - 1)*per_page
    limit = per_page

    return Pagination(queryset.limit(limit).skip(skip), page=page, per_page=per_page, total_items=queryset.count())


def delProvinces(idList):
    """
    删除省市信息
    :param idDict: 省市ID列表，也可传入str
    :return: 操作结果
    """
    resultCount =0
    idTempList = []
    idLists = idList["idArray"]
    if(isinstance(idLists, str)):
        idTempList.append(idLists)
        idLists = idTempList
    try:
        for eachID in idLists:
            result = mongo.db.IPRMS_Provinces.delete_one({"ID": int(eachID)})
            resultCount += result.deleted_count
        status = {
            "status": 1,
            "result": resultCount
        }
    except Exception as e:
        print(e)
        status = {
            "status": 0
        }
    return json.dumps(status)


def getProvicesModify(idList):
    """
    管理省市信息
    :param idList: 省市ID列表，也可传入str
    :return: 前端查询集
    """
    idTempList = []
    idLists = idList["idArray"]
    if (isinstance(idLists, str)):
        idTempList.append(idLists)
        idLists = idTempList
    result = []
    try:
        for eachID in idLists:
            selectResult = mongo.db.IPRMS_Provinces.find_one({"ID": int(eachID)})
            dictResult = {
                "ID": selectResult["ID"],
                "Provinces": selectResult["Provinces"],
                "City": selectResult["City"]
            }
            result.append(dictResult)
    except Exception as e:
        print(e)

    return result


def setProvicesModify(pDatas):
    """
    修改省市信息
    :param pDatas: 被修改ID，新数据List
    :return: 操作结果
    """
    resultUpdateCount = 0
    newData = pDatas["idArray"]
    try:
        for eachOne in newData:
            PvsID = eachOne["ID"]
            Provinces = eachOne["Provinces"]
            City = eachOne["City"]
            resultUpdate = mongo.db.IPRMS_Provinces.update_one({"ID": int(PvsID)}, {"$set": {"Provinces": Provinces, "City": City}})
            resultUpdateCount += resultUpdate.modified_count
        status = {
            "status": 1,
            "UpdateCount": resultUpdateCount
        }
    except Exception as e:
        print(e)
        status = {
            "status": 0
        }
    return json.dumps(status)
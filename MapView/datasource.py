import asyncio
import json
from datetime import datetime
#import websockets
#from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


import csv
from datetime import datetime

class CSVDataSource:
    def __init__(self,user_id,GPS_src = "./gps.csv",ACC_src = "./data.csv") -> None:
        self.user_id = user_id
        with open(GPS_src) as gps_f:
            self.gps = self.__make_data_list(csv.reader(gps_f),[float,float])
        with open(ACC_src)as acc_f:
            self.acc = self.__make_data_list(csv.reader(acc_f),[int,int,int])
        self.iter =0
        self.iter_max = len(self.gps)-1 if len(self.gps)<len(self.acc) else len(self.acc)-1
    @staticmethod
    def __validate_coord_val(value:int):
        val_abs = value if value>=0 else -value
        if(val_abs>=3000):
            return "Extremely bad"
        if(val_abs>=2500):
            return "Poor"
        if(val_abs>=1000):
            return "Normal"
        if(val_abs>=550):
            return "OK"
        return "Perfect"
    @staticmethod
    def __make_data_list(rdr:csv.reader,struct:list)->list:
        next(rdr)
        res = []
        for line in rdr:
             r = CSVDataSource.__cv_by_struct(line,struct)
             if r is not None:
                res.append(r)
        return res
    
    @staticmethod
    def __cv_by_struct(row,struct):
        if len(row)<len(struct):
            return None
        return [f(row[i])for i,f in enumerate(struct)]

    def get_new_points(self)->list:
        data = None
        if self.iter<=(self.iter_max-1):
            data = [[self.gps[self.iter+i],self.acc[self.iter+i]]for i in range(2)]
        else:
            return None
        res = []
        for i in range(2):
            res.append(ProcessedAgentData(road_state=self.__validate_coord_val(data[i][1][1]),user_id=self.user_id,x=data[i][1][0],y=data[i][1][1],z=data[i][1][2],
                                          latitude=data[i][0][0],longitude=data[i][0][1],timestamp=datetime.now()))
        self.iter+=1
        return res

if __name__=="__main__":
    test = CSVDataSource(user_id=1)
    for i in range(test.iter_max+10):
        print(test.get_new_points())
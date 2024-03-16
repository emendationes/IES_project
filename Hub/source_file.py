from csv import reader
from datetime import datetime
from app.entities.agent_data import GpsData
from app.entities.agent_data import AccelerometerData
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData
import config

from threading import Thread
from time import sleep

class DataSource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.names = [accelerometer_filename,gps_filename]
        self.structs = [[float,float,float],[float,float]]
        self.iters = [0 for name in self.names]
        self.data = [[] for name in self.names]

    def read(self) -> AgentData:
        res = AgentData(
            accelerometer = AccelerometerData(x = 1, y = 2, z = 3),
            gps = GpsData(longitude = 4, latitude = 5),
            timestamp = datetime.now(),
            user_id = 2,
        )
        for i, builder in enumerate([AccelerometerData,GpsData]):
            if i == 0:
                res.accelerometer = builder(x = self.data[i][self.iters[i]][0], y = self.data[i][self.iters[i]][1],z = self.data[i][self.iters[i]][2]) or builder(x = 0,y = 0,z =0 )
            if i == 1:
                res.gps=builder(longitude = self.data[i][self.iters[i]][0],latitude = self.data[i][self.iters[i]][1]) or builder(longitude = 0,latitude = 0)
            self.iters[i]=self.iters[i]+1 if self.iters[i] < (len(self.data[i]) - 1) else 0
        return res

    def startReading(self, *args, **kwargs):
        
        for i,name in enumerate(self.names):
            with open(name,'r') as csv_f:
                rdr = reader(csv_f)
                for line in rdr:
                    self.data[i].append(self.convert_csv_line(line, self.structs[i]))

    def stopReading(self, *args, **kwargs):
        pass
        
    def convert_csv_line(self, line, struct):
        try:
            return [t_conv(line[i]) for i,t_conv in enumerate(struct)]
        except Exception:
            return [0,0,0]
            
def publish(client,topic,datasource,delay):
    datasource.startReading()
    while True:
        sleep(delay)
        data= datasource.read()
        msg = data.model_dump_json()
        result = client.publish(topic,msg)
        status = result[0]
        if status == 0:
            pass
        else:
            print(f"Failed to send message to topic{topic}")
    datasource.stopReading()

def start_constant_publish_to_client(src:DataSource,client,topic):
    rdr = Thread(target=publish,args=(client,topic,src,0.1),daemon=True)
    rdr.start()
    print("[ALERT]:READING THREAD IS RUNNING AND SENDING DATA")


if __name__ == "__main__":
    src = FileDatasource("./data/accelerometer.csv", "./data/gps.csv")
    src.startReading()
    for i in range (10000):
        print(src.read())

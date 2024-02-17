from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.names = [accelerometer_filename,gps_filename]
        self.structs = [[int,int,int],[float,float]]
        self.iters = [0 for name in self.names]
        self.data = [[] for name in self.names]

    def read(self) -> AggregatedData:
        res = AggregatedData(
            Accelerometer(1, 2, 3),
            Gps(4, 5),
            datetime.now(),
            config.USER_ID,
        )
        for i, builder in enumerate([Accelerometer,Gps]):
            match i:
                case 0:
                    res.accelerometer = builder(self.data[i][self.iters[i]][0],self.data[i][self.iters[i]][1],self.data[i][self.iters[i]][2]) or builder(0,0,0)
                case 1:
                    res.gps=builder(self.data[i][self.iters[i]][0],self.data[i][self.iters[i]][1]) or builder(0,0)
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

if __name__ == "__main__":
    src = FileDatasource("./data/accelerometer.csv", "./data/gps.csv")
    src.startReading()
    for i in range (10000):
        print(src.read())